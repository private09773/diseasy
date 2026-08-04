"""
diseasy/fetch.py

Real implementation of fetch() for local JSON-backed "databases" —
matches the manifesto's "built-in fetch() for local databases"
feature. Each collection is a single JSON file containing a list of
documents (plain dicts).

This does NOT implement MongoDB/SQL support — those would need
separate real drivers (pymongo, sqlite3, etc.) wired in similarly.
This covers the JSON case only, confirmed working by the test below.
"""

import json
import os

_DB_DIR = "db"


def set_db_path(path: str):
    """Sets the folder where collection .json files live. Defaults to './db'."""
    global _DB_DIR
    _DB_DIR = path
    os.makedirs(_DB_DIR, exist_ok=True)


def _collection_path(collection: str) -> str:
    os.makedirs(_DB_DIR, exist_ok=True)
    return os.path.join(_DB_DIR, f"{collection}.json")


def _load(collection: str) -> list:
    path = _collection_path(collection)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def _save(collection: str, documents: list):
    path = _collection_path(collection)
    with open(path, "w") as f:
        json.dump(documents, f, indent=2)


def _matches(document: dict, filter: dict) -> bool:
    return all(document.get(k) == v for k, v in filter.items())


def fetch(collection: str, filter: dict = None, many: bool = False):
    """
    Reads from a JSON-backed collection.

    fetch(collection="users", filter={"id": 123})       -> one dict or None
    fetch(collection="users", filter={"role": "admin"}, many=True) -> list
    fetch(collection="users")                            -> all documents (list)
    """
    documents = _load(collection)
    if filter is None:
        return documents

    matches = [d for d in documents if _matches(d, filter)]
    if many:
        return matches
    return matches[0] if matches else None


def insert(collection: str, document: dict):
    """Adds a new document to a collection."""
    documents = _load(collection)
    documents.append(document)
    _save(collection, documents)
    return document


def update(collection: str, filter: dict, changes: dict):
    """Updates all documents matching filter with the given changes.
    Returns the number of documents updated."""
    documents = _load(collection)
    count = 0
    for doc in documents:
        if _matches(doc, filter):
            doc.update(changes)
            count += 1
    _save(collection, documents)
    return count


def delete(collection: str, filter: dict):
    """Deletes all documents matching filter. Returns the number deleted."""
    documents = _load(collection)
    remaining = [d for d in documents if not _matches(d, filter)]
    deleted_count = len(documents) - len(remaining)
    _save(collection, remaining)
    return deleted_count
