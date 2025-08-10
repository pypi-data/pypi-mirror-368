import os
import json
import hashlib
from pathlib import Path
from typing import Dict
from pyrogram import Client
from cpy.ccrypt.encrypt import encrypt_data, hash_file_name
from cpy.ccrypt.decrypt import decrypt_data


def encrypt(data: bytes, password: str) -> str:
    return json.dumps(encrypt_data(data, password))


def decrypt(data: str, password: str) -> bytes:
    return decrypt_data(json.loads(data), password)


def get_file_id(path: str, password: str) -> str:
    return hash_file_name(path, password)


CHUNK_SIZE = 200 * 1024 * 1024  # 200MB chunks for Telegram file limit


class TelegramFileSystem:
    def __init__(self, api_id, api_hash, password, channel_id, workdir=None):
        self.password = password
        self.channel_id = channel_id

        kwargs = {}
        if workdir:
            kwargs['workdir'] = workdir
            self.downloads_dir = (Path(workdir) / "downloads").as_posix() + "/"
        else:
            self.downloads_dir = "downloads/"

        self.app = Client("user_session", api_id=api_id, api_hash=api_hash, **kwargs)

    def resolve_channel_id(self, title: str) -> int:
        for dialog in self.app.get_dialogs():
            if dialog.chat.title == title:
                return dialog.chat.id
        raise TelegramFileSystemError(f"Channel titled '{title}' not found.")

    def _upload_file(self, file_path: Path, rel_path: str, file_id: str):
        with open(file_path, 'rb') as f:
            content = f.read()

        checksum = hashlib.sha256(content).hexdigest()
        chunks = [content[i:i + CHUNK_SIZE] for i in range(0, len(content), CHUNK_SIZE)]

        for i, chunk in enumerate(chunks):
            encrypted = encrypt(chunk, self.password)
            name = f"{file_id}.content-{i}"
            self._send_string_file(encrypted, name)

        stat = file_path.stat()

        metadata = {
            "path": str(rel_path),
            "permissions": oct(file_path.stat().st_mode)[-3:],
            "checksum": checksum,
            "size": stat.st_size,
            "mtime": stat.st_mtime,
            "ctime": stat.st_ctime,
        }

        encrypted_metadata = encrypt(json.dumps(metadata).encode(), self.password)
        self._send_string_file(encrypted_metadata, f"{file_id}.metadata")

    def _send_string_file(self, content: str, filename: str):
        tmp_path = Path(f"/tmp/{filename}")
        with open(tmp_path, 'w') as f:
            f.write(content)
        self.app.send_document(chat_id=self.channel_id, document=str(tmp_path), file_name=filename)
        tmp_path.unlink()

    def _list_remote_files(self) -> Dict[str, str]:
        file_map = {}
        for msg in self.app.get_chat_history(self.channel_id):
            if msg.document:
                file_map[msg.document.file_name] = msg.document.file_id
        return file_map

    def _get_remote_metas(self, remote_files: Dict[str, str]) -> Dict[str, Dict]:
        metas = {}
        for filename, file_id in remote_files.items():
            if filename.endswith(".metadata"):
                file = self.app.download_media(file_id, file_name=self.downloads_dir)
                with open(file, 'r') as f:
                    decrypted = decrypt(f.read(), self.password)
                    meta = json.loads(decrypted)
                    fid = filename.replace(".metadata", "")
                    metas[fid] = meta
                os.remove(file)
        return metas

    @staticmethod
    def _is_a_remote_dir(rel_path: str, remote_metas: Dict[str, Dict]) -> bool:
        rel_path = rel_path.rstrip('/') + "/"
        for meta in remote_metas.values():
            if meta["path"].startswith(rel_path) and meta["path"] != rel_path:
                return True
        return False

    @staticmethod
    def _locate_remote_path(rel_path: str, remote_metas: Dict[str, Dict]) -> str | None:
        rel_path = rel_path.rstrip('/')
        for meta in remote_metas.values():
            if meta["path"] == rel_path:
                return rel_path
            elif meta["path"].startswith(rel_path + "/"):
                return rel_path + "/"
        return None

    def upload(self, local_path: str, target_path: str = "", delete_missing: bool = False):
        if target_path == "/":
            target_path = ""

        local_path = Path(local_path).resolve()
        remote_files = self._list_remote_files()
        remote_metas = self._get_remote_metas(remote_files)

        if local_path.is_file():
            if not target_path:
                raise TelegramFileSystemError("target_path must be specified for single file uploads.")
            if self._is_a_remote_dir(target_path, remote_metas):
                target_path = (Path(target_path) / local_path.name).as_posix()
            local_files = [(target_path, local_path)]
        else:
            local_files = []

            for root, _, files in os.walk(local_path):
                for file in files:
                    path = Path(root) / file
                    rel_path = path.relative_to(local_path)
                    if target_path:
                        rel_path = target_path / rel_path
                    local_files.append((rel_path.as_posix(), path))

        for rel_path, full_path in local_files:
            file_id = get_file_id(rel_path, self.password)
            checksum = hashlib.sha256(full_path.read_bytes()).hexdigest()

            if file_id in remote_metas and remote_metas[file_id].get("checksum") == checksum:
                print(f"✓ Skipping unchanged file: {rel_path}")
                continue

            print(f"↑ Uploading: {rel_path}")
            self._upload_file(full_path, rel_path, file_id)

        if delete_missing:
            remote_paths = {meta["path"] for meta in remote_metas.values()}
            local_paths = {p for p, _ in local_files}
            to_delete = remote_paths - local_paths
            for path in to_delete:
                print(f"🗑 Deleting remote file: {path}")
                self._delete_remote_file(get_file_id(path, self.password), remote_files)

    def rm(self, target_path: str = "", recursive: bool = False):
        if target_path == "/":
            target_path = ""

        remote_files = self._list_remote_files()
        remote_metas = self._get_remote_metas(remote_files)

        if target_path:
            target_path = self._locate_remote_path(target_path, remote_metas)
            if target_path.endswith("/") and not recursive:
                raise TelegramFileSystemError("Cannot delete a directory without -r option.")

        filtered_metas = self._filter_remote_metas_by_path(target_path, remote_metas)
        if len(filtered_metas) == 0:
            print("No files found to delete.")
            return

        for file_id, meta in filtered_metas.items():
            path = Path(meta["path"])
            rel_path = (path.relative_to(target_path) if target_path else path).as_posix()
            if not rel_path:
                rel_path = path.name

            print(f"🗑 Deleting remote file: {rel_path}")
            self._delete_remote_file(file_id, remote_files)

    def _delete_remote_file(self, file_id: str, remote_files: Dict[str, str]):
        for name in list(remote_files.keys()):
            if name.startswith(file_id):
                self.app.delete_messages(chat_id=self.channel_id, message_ids=[remote_files[name]])

    def download(self, target_path: str, remote_path: str = "", delete_missing: bool = False):
        if remote_path == "/":
            remote_path = ""

        target_path = Path(target_path).resolve()
        remote_files = self._list_remote_files()
        remote_metas = self._get_remote_metas(remote_files)

        orig_remote_path = remote_path
        remote_path = remote_path.lstrip("/")
        if remote_path:
            remote_path = self._locate_remote_path(remote_path, remote_metas)
            if remote_path is None:
                raise TelegramFileSystemError(f"Remote path '{orig_remote_path}' not found.")

            if remote_path.endswith("/"):
                if target_path.exists() and not target_path.is_dir():
                    raise TelegramFileSystemError(f"Target path '{target_path}' is not a directory.")

        target_files = {}
        for file_id, meta in self._filter_remote_metas_by_path(remote_path, remote_metas).items():
            path = Path(meta["path"])
            rel_path = path.relative_to(remote_path) if remote_path else path

            full_path = target_path / rel_path
            full_path = full_path.resolve()
            if full_path.is_dir():
                full_path = full_path / path.name

            target_files[str(full_path)] = (file_id, meta)

        for full_path_str, (file_id, meta) in target_files.items():
            full_path = Path(full_path_str)
            full_path.parent.mkdir(parents=True, exist_ok=True)

            if full_path.exists():
                local_checksum = hashlib.sha256(full_path.read_bytes()).hexdigest()
                if local_checksum == meta["checksum"]:
                    print(f"✓ Skipping unchanged file: {meta['path']}")
                    continue

            print(f"↓ Downloading: {meta['path']}")
            chunks = []
            i = 0
            while True:
                fname = f"{file_id}.content-{i}"
                if fname not in remote_files:
                    break
                file = self.app.download_media(remote_files[fname], file_name=self.downloads_dir)
                with open(file, 'r') as f:
                    decrypted = decrypt(f.read(), self.password)
                    chunks.append(decrypted)
                os.remove(file)
                i += 1

            with open(full_path, 'wb') as f:
                for c in chunks:
                    f.write(c)

            os.chmod(full_path, int(meta["permissions"], 8))
            os.utime(full_path, (meta.get("atime", meta["mtime"]), meta["mtime"]))

        if delete_missing:
            existing_local = {str(p) for p in target_path.rglob('*') if p.is_file()}
            expected = set(target_files.keys())
            to_delete = existing_local - expected
            for p in to_delete:
                print(f"🗑 Deleting local file: {p}")
                os.remove(p)

    def ls(self, path: str = "") -> dict[str, dict]:
        if path == "/":
            path = ""

        remote_files = self._list_remote_files()
        remote_metas = self._get_remote_metas(remote_files)
        entries = {}

        for meta in self._filter_remote_metas_by_path(path, remote_metas).values():
            cur_path = Path(meta["path"])

            relative = cur_path.relative_to(path) if path else cur_path

            parts = relative.parts
            if len(parts) > 1:
                key = parts[0] + "/"
            else:
                key = relative.name
            if not key:
                key = cur_path.name

            if key not in entries:
                entries[key] = meta

        return entries

    def find(self, path: str = "") -> dict[str, dict]:
        if path == "/":
            path = ""

        remote_files = self._list_remote_files()
        remote_metas = self._get_remote_metas(remote_files)

        if path:
            path = self._locate_remote_path(path, remote_metas)

        entries = {}

        for meta in self._filter_remote_metas_by_path(path, remote_metas).values():
            cur_path = meta["path"]
            relative = cur_path.relative_to(path) if path else cur_path
            if not relative:
                relative = cur_path.name
            entries[relative] = meta

        return entries

    def _filter_remote_metas_by_path(self, path: str, remote_metas: Dict[str, Dict]) -> Dict[str, Dict]:
        if not path or path == "/":
            return remote_metas

        if not remote_metas:
            raise TelegramFileSystemError(f"No remote files found. Ensure you have uploaded files to the channel.")

        orig_path = path
        path = self._locate_remote_path(path, remote_metas)
        if path is None:
            raise TelegramFileSystemError(f"Remote path '{orig_path}' not found.")

        filtered = {}
        for file_id, meta in remote_metas.items():
            if meta["path"] == path or meta["path"].startswith(path.rstrip("/") + "/"):
                filtered[file_id] = meta
        return filtered


class TelegramFileSystemError(Exception):
    pass
