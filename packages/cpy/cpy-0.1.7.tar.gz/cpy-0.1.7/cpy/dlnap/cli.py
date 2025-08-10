#!/usr/bin/env python3
import os, sys, time, stat, errno, threading, requests, asyncio, aiohttp
from datetime import datetime
from fuse import FUSE, Operations, FuseOSError
from defusedxml import ElementTree as ET
from async_upnp_client.search import async_search
from async_upnp_client.aiohttp import AiohttpSessionRequester
from async_upnp_client.client_factory import UpnpFactory

NS = {
    "didl": "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "upnp": "urn:schemas-upnp-org:metadata-1-0/upnp/",
}

MIME_EXT = {
    "video/mp4": ".mp4",
    "video/x-matroska": ".mkv",
    "video/avi": ".avi",
    "video/x-msvideo": ".avi",
    "video/quicktime": ".mov",
    "video/mp2t": ".ts",
    "application/vnd.apple.mpegurl": ".m3u8",
    "application/x-mpegURL": ".m3u8",
    "video/x-m4v": ".m4v",
    "audio/mpeg": ".mp3",
    "audio/mp4": ".m4a",
    "audio/flac": ".flac",
    "audio/wav": ".wav",
}


def guess_ext_from_res(res_el) -> str:
    # 1) try URL extension
    url = (res_el.text or "").strip()
    if url:
        path = url.split("?", 1)[0]
        ext = os.path.splitext(path)[1].lower()
        if ext in {".mp4", ".mkv", ".avi", ".mov", ".ts", ".m3u8", ".m4v", ".mp3", ".m4a", ".flac", ".wav"}:
            return ext
    # 2) try MIME from protocolInfo (http-get:*:<mime>:...)
    pi = res_el.get("protocolInfo", "")
    try:
        mime = pi.split(":")[2]
    except Exception:
        mime = ""
    return MIME_EXT.get(mime, "")


def guess_ext_from_item(item_el) -> str:
    # prefer first <res>; fallback to any
    res = item_el.find("didl:res", namespaces=NS)
    if res is not None:
        ext = guess_ext_from_res(res)
        if ext:
            return ext
    for r in item_el.findall("didl:res", namespaces=NS):
        ext = guess_ext_from_res(r)
        if ext:
            return ext
    return ""  # unknown


def is_video(item):
    clazz = item.findtext("upnp:class", default="", namespaces=NS)
    return "videoItem" in clazz


def item_title(item):
    return item.findtext("dc:title", default="(untitled)", namespaces=NS)


def item_size(item):
    res = item.find("didl:res", namespaces=NS)
    if res is not None:
        s = res.get("size")
        if s and s.isdigit():
            return int(s)
    return None


def item_url(item):
    res = item.find("didl:res", namespaces=NS)
    return (res.text or "").strip() if res is not None else ""


class DLNAFS(Operations):
    """
    Very small, read-only DLNA filesystem:
    - Directories mirror DLNA containers
    - Files are video items; data read via HTTP Range
    """

    def __init__(self, tree, filemap):
        self.tree = tree  # dict path-> [names]
        self.meta = filemap  # dict path-> {'size':int,'url':str}
        self.fd = 3
        self.handles = {}  # fh -> {'url','pos'}
        self.now = int(time.time())

    # Helpers
    def _is_dir(self, path):
        return path in self.tree

    def _is_file(self, path):
        return path in self.meta

    # Filesystem methods
    def getattr(self, path, fh=None):
        st = dict(st_mode=0, st_nlink=1, st_uid=os.getuid(), st_gid=os.getgid(),
                  st_ctime=self.now, st_mtime=self.now, st_atime=self.now)
        if self._is_dir(path):
            st["st_mode"] = stat.S_IFDIR | 0o555
            st["st_nlink"] = 2
            return st
        if self._is_file(path):
            st["st_mode"] = stat.S_IFREG | 0o444
            st["st_size"] = self.meta[path]["size"]
            return st
        raise FuseOSError(errno.ENOENT)

    def readdir(self, path, fh):
        if not self._is_dir(path):
            raise FuseOSError(errno.ENOTDIR)
        entries = ['.', '..'] + self.tree[path]
        for e in entries:
            yield e

    # Read-only
    def open(self, path, flags):
        if not self._is_file(path):
            raise FuseOSError(errno.ENOENT)
        if flags & (os.O_WRONLY | os.O_RDWR):
            raise FuseOSError(errno.EROFS)
        self.fd += 1
        fh = self.fd
        self.handles[fh] = {"url": self.meta[path]["url"], "pos": 0}
        return fh

    def read(self, path, size, offset, fh):
        h = self.handles.get(fh)
        if not h:
            raise FuseOSError(errno.EBADF)
        url = h["url"]
        headers = {"Range": f"bytes={offset}-{offset + size - 1}"}
        r = requests.get(url, headers=headers, stream=True, timeout=30)
        if r.status_code in (200, 206):
            return r.content
        # Some servers ignore range for small reads: fallback whole
        if r.status_code == 416:
            return b""
        r.raise_for_status()
        return b""

    def release(self, path, fh):
        self.handles.pop(fh, None)
        return 0

    # No writes
    def mkdir(self, path, mode):
        raise FuseOSError(errno.EROFS)

    def rmdir(self, path):
        raise FuseOSError(errno.EROFS)

    def unlink(self, path):
        raise FuseOSError(errno.EROFS)

    def rename(self, a, b):
        raise FuseOSError(errno.EROFS)

    def create(self, path, mode, fi=None):
        raise FuseOSError(errno.EROFS)

    def write(self, path, data, offset, fh):
        raise FuseOSError(errno.EROFS)

    def truncate(self, path, length, fh=None):
        raise FuseOSError(errno.EROFS)


async def build_tree():
    """Discover first MediaServer, crawl ContentDirectory, return (tree, filemap)."""
    servers = []

    async def on_resp(h):
        if "MediaServer" in (h.get("st", "")):
            servers.append(h.get("location", ""))

    await async_search(on_resp, timeout=3, search_target="urn:schemas-upnp-org:device:MediaServer:1")
    if not servers:
        await async_search(on_resp, timeout=3, search_target="ssdp:all")
    if not servers:
        raise RuntimeError("No DLNA MediaServer found.")

    async with aiohttp.ClientSession() as session:
        requester = AiohttpSessionRequester(session, with_sleep=True)
        factory = UpnpFactory(requester)
        dev = await factory.async_create_device(servers[0])
        cd = dev.service("urn:schemas-upnp-org:service:ContentDirectory:1")

        def browse_children(object_id):
            # synchronous wrapper around async call for easier BFS
            return asyncio.get_event_loop().run_until_complete(
                cd.action("Browse").async_call(
                    ObjectID=object_id, BrowseFlag="BrowseDirectChildren",
                    Filter="*", StartingIndex=0, RequestedCount=0, SortCriteria=""
                )
            )

        # BFS through containers, build dir tree and file map
        tree = {"/": []}
        filemap = {}
        q = [("0", "/")]
        seen = set()
        while q:
            oid, p = q.pop(0)
            if oid in seen: continue
            seen.add(oid)
            res = await cd.action("Browse").async_call(
                ObjectID=oid, BrowseFlag="BrowseDirectChildren",
                Filter="*", StartingIndex=0, RequestedCount=0, SortCriteria=""
            )
            xml = res["Result"]
            if not xml.strip():
                continue
            root = ET.fromstring(xml)
            # containers -> subdirs
            for c in root.findall("didl:container", namespaces=NS):
                name = c.findtext("dc:title", default="Folder", namespaces=NS) or "Folder"
                # sanitize name for filesystem
                safe = "".join(ch for ch in name if ch not in "/\0")
                subpath = os.path.join(p, safe)
                if subpath not in tree:
                    tree[subpath] = []
                if safe not in tree[p]:
                    tree[p].append(safe)
                cid = c.get("id")
                if cid:
                    q.append((cid, subpath))
            # items -> files
            for it in root.findall("didl:item", namespaces=NS):
                if not is_video(it):
                    continue
                title = item_title(it)
                safe = "".join(ch for ch in title if ch not in "/\0") or "video"
                url = item_url(it)
                size = item_size(it) or 0

                ext = guess_ext_from_item(it)
                base = safe
                name = base + ext

                candidate = name
                i = 1
                while candidate in tree[p]:
                    i += 1
                    candidate = f"{base} ({i}){ext}"

                tree[p].append(candidate)
                filemap[os.path.join(p, candidate)] = {"url": url, "size": size}
        return tree, filemap


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} MOUNTPOINT")
        sys.exit(1)
    mountpoint = sys.argv[1]
    if not os.path.isdir(mountpoint):
        print("Mountpoint must be an existing directory.")
        sys.exit(1)

    # Build DLNA dir tree (async) before mounting
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tree, filemap = loop.run_until_complete(build_tree())
    print(f"Indexed {len(filemap)} video(s). Mounting at {mountpoint}…")

    # Start FUSE (foreground; ctrl-c to exit)
    FUSE(
        DLNAFS(tree, filemap),
        mountpoint,
        volname="DLNAP Library",
        subtype="dlnafs",
        fsname="DLNAP Library",
        nothreads=True,
        foreground=True,
        ro=True,
    )


if __name__ == "__main__":
    main()
