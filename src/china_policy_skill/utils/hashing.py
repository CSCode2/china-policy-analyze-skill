import hashlib
import json
import os
from typing import Dict, Optional


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _load_store(hash_store_path: str) -> Dict[str, str]:
    if not os.path.exists(hash_store_path):
        return {}
    try:
        with open(hash_store_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_store(store: Dict[str, str], hash_store_path: str) -> None:
    os.makedirs(os.path.dirname(hash_store_path) or ".", exist_ok=True)
    with open(hash_store_path, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False, indent=2)


def is_duplicate(hash_value: str, hash_store_path: str) -> bool:
    store = _load_store(hash_store_path)
    return hash_value in store


def record_hash(hash_value: str, doc_id: str, hash_store_path: str) -> None:
    store = _load_store(hash_store_path)
    store[hash_value] = doc_id
    _save_store(store, hash_store_path)
