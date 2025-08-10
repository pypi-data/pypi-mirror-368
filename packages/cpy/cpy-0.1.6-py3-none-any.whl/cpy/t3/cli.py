#!/usr/bin/env python3
import grp
import json
import argparse
import os
import pwd
import time
from pathlib import Path
from cpy.t3.fs import TelegramFileSystem, TelegramFileSystemError

CONFIG_PATH = Path.home() / ".t3" / "config"
CACHE_DIR = Path.home() / ".t3" / "cache"


class T3Error(Exception):
    pass


def load_config():
    os.makedirs(CONFIG_PATH.parent, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)

    if not CONFIG_PATH.exists():
        raise T3Error(f"Missing config file: {CONFIG_PATH}")
    with open(CONFIG_PATH) as f:
        return json.load(f)


def get_store(store_name):
    config = load_config()
    for store in config.get("stores", []):
        if store["name"] == store_name:
            return store
    raise T3Error(f"Store '{store_name}' not found in ~/.t3_config")


def get_store_fs(store_name: str) -> TelegramFileSystem:
    store = get_store(store_name)
    return TelegramFileSystem(
        api_id=store["api_id"],
        api_hash=store["api_hash"],
        password=store["secret"],
        channel_id=store["channel_id"],
        workdir=CACHE_DIR,
    )


def parse_uri(uri):
    """Parse s1://a/b/c into (store_name, path)"""
    if "://" not in uri:
        return None, uri
    store, path = uri.split("://", 1)
    return store, path.lstrip("/")


def format_size(size_bytes):
    for unit in ['B', 'K', 'M', 'G', 'T']:
        if size_bytes < 1024:
            return f"{size_bytes:.0f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.0f}P"


def format_mode(mode_str):
    mode = int(mode_str, 8)
    perms = ['-']
    for i in [6, 3, 0]:
        perms.append('r' if mode >> i & 4 else '-')
        perms.append('w' if mode >> i & 2 else '-')
        perms.append('x' if mode >> i & 1 else '-')
    return ''.join(perms)


def _human_time(epoch):
    return time.strftime("%b %d %H:%M", time.localtime(epoch))


def ls(fs: TelegramFileSystem, path: str, long: bool):
    entries = fs.ls(path)

    for name, meta in sorted(entries.items()):
        if not long:
            print(name)
            continue

        if name.endswith("/"):
            perms = "drwxr-xr-x"
            size = "-"
            mtime = _human_time(time.time())
        else:
            perms = format_mode(meta["permissions"])
            size = format_size(meta["size"])
            mtime = _human_time(meta["mtime"])

        user = pwd.getpwuid(os.getuid()).pw_name
        group = grp.getgrgid(os.getgid()).gr_name
        print(f"{perms}@ 1 {user:8} {group:8} {size:>6} {mtime} {name}")


def find(fs: TelegramFileSystem, path: str):
    entries = fs.find(path)
    for name, _ in sorted(entries.items()):
        print(name)


def cli():
    parser = argparse.ArgumentParser(prog="t3", description="Telegram-based S3-like client")
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    ls_parser = subparsers.add_parser("ls")
    ls_parser.add_argument("path", nargs="?", default="")
    ls_parser.add_argument("-l", "--long", action="store_true", help="Use a long listing format")

    find_parser = subparsers.add_parser("find")
    find_parser.add_argument("path", nargs="?", default="")

    cp_parser = subparsers.add_parser("cp")
    cp_parser.add_argument("src")
    cp_parser.add_argument("dst")

    rm_parser = subparsers.add_parser("rm")
    rm_parser.add_argument("path", nargs="?", default="")
    rm_parser.add_argument("-r", "--recursive", action="store_true", help="Remove directories recursively")

    args = parser.parse_args()

    if args.cmd in ["ls", "find", "rm"]:
        store_name, remote_path = parse_uri(args.path)
        if not store_name:
            raise T3Error("Must use format like s1://path for remote access")

        fs = get_store_fs(store_name)
        fs.app.start()
        if args.cmd == "ls":
            ls(fs, remote_path, long=args.long)
        elif args.cmd == "find":
            find(fs, remote_path)
        else:
            fs.rm(remote_path, recursive=args.recursive)
        fs.app.stop()

    elif args.cmd == "cp":
        src_store, src_path = parse_uri(args.src)
        dst_store, dst_path = parse_uri(args.dst)

        if src_store and not dst_store:
            # remote -> local
            fs = get_store_fs(src_store)
            fs.app.start()
            fs.download(target_path=args.dst, remote_path=src_path)
            fs.app.stop()

        elif dst_store and not src_store:
            # local -> remote
            fs = get_store_fs(dst_store)
            fs.app.start()
            fs.upload(local_path=args.src, target_path=dst_path)
            fs.app.stop()

        else:
            raise T3Error("Only one of src or dst can be a remote path like s1://...")


def main():
    try:
        cli()
    except T3Error as e:
        print(f"Error: {e}")
        exit(1)
    except TelegramFileSystemError as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
