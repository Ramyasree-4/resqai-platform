"""
ResQAI – Firestore Mock Client
Wraps the in-memory store with a Firestore-compatible interface.
Used when DEMO_MODE=true so all services work unchanged.
"""
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional
from app.demo import store as _store


class _MockDocument:
    def __init__(self, doc_id: str, data: Optional[Dict]):
        self.id = doc_id
        self._data = data

    @property
    def exists(self) -> bool:
        return self._data is not None

    def to_dict(self) -> Dict:
        return dict(self._data) if self._data else {}


class _MockQuery:
    def __init__(self, collection_name: str, items: List[Dict]):
        self._name = collection_name
        self._items = list(items)

    def where(self, field: str, op: str, value: Any) -> "_MockQuery":
        if op == "==":
            # Support dot-notation
            def _get(item, f):
                parts = f.split(".")
                v = item
                for p in parts:
                    if isinstance(v, dict):
                        v = v.get(p)
                    else:
                        return None
                return v
            self._items = [i for i in self._items if _get(i, field) == value]
        elif op == "not-in":
            def _get2(item, f):
                parts = f.split(".")
                v = item
                for p in parts:
                    v = v.get(p) if isinstance(v, dict) else None
                return v
            self._items = [i for i in self._items if _get2(i, field) not in value]
        elif op == ">=":
            def _get3(item, f):
                parts = f.split(".")
                v = item
                for p in parts:
                    v = v.get(p) if isinstance(v, dict) else None
                return v
            self._items = [i for i in self._items if _get3(i, field) is not None and _get3(i, field) >= value]
        elif op == "<=":
            def _get4(item, f):
                parts = f.split(".")
                v = item
                for p in parts:
                    v = v.get(p) if isinstance(v, dict) else None
                return v
            self._items = [i for i in self._items if _get4(i, field) is not None and _get4(i, field) <= value]
        return self

    def order_by(self, field: str, direction: str = "ASCENDING") -> "_MockQuery":
        reverse = direction.upper() == "DESCENDING"
        self._items.sort(key=lambda x: x.get(field) or "", reverse=reverse)
        return self

    def limit(self, n: int) -> "_MockQuery":
        self._items = self._items[:n]
        return self

    def count(self) -> "_MockCountQuery":
        return _MockCountQuery(len(self._items))

    def stream(self) -> Iterator[_MockDocument]:
        for item in self._items:
            yield _MockDocument(item.get("_firestoreId", item.get("uid", "")), item)

    def get(self) -> List[_MockDocument]:
        return list(self.stream())

    def add(self, data: Dict) -> tuple:
        doc_ref = _MockDocumentRef(self._name, None)
        doc_ref.set(data)
        return None, doc_ref


class _MockCountQuery:
    def __init__(self, count: int):
        self._count = count

    def get(self):
        class _Result:
            def __init__(self, c):
                self.value = c
        return [[_Result(self._count)]]


class _MockDocumentRef:
    def __init__(self, collection_name: str, doc_id: Optional[str]):
        self._col = collection_name
        self._id = doc_id or __import__("uuid").uuid4().hex
        self.id = self._id

    def set(self, data: Dict, merge: bool = False) -> None:
        # Always ensure _firestoreId is stored so services can read doc_ref.id
        enriched = {**data, "_firestoreId": self._id}
        _dispatch_set(self._col, self._id, enriched, merge)

    def update(self, data: Dict) -> None:
        _dispatch_update(self._col, self._id, data)

    def get(self) -> _MockDocument:
        data = _dispatch_get(self._col, self._id)
        return _MockDocument(self._id, data)

    @property
    def reference(self) -> "_MockDocumentRef":
        return self

    def collection(self, subcol: str) -> "_MockSubCollection":
        return _MockSubCollection(self._col, self._id, subcol)


class _MockSubCollection:
    """Handles subcollections like incidents/comments, incidents/statusHistory."""
    def __init__(self, parent_col: str, parent_id: str, subcol: str):
        self._key = f"{parent_col}/{parent_id}/{subcol}"
        if self._key not in _store._incidents:
            # Use a separate dict per subcollection key
            pass
        from app.demo import store as s
        if not hasattr(s, "_subcollections"):
            s._subcollections = {}
        self._s = s

    def document(self, doc_id: Optional[str] = None) -> "_MockDocumentRef":
        if doc_id is None:
            import uuid
            doc_id = str(uuid.uuid4())
        ref = _MockDocumentRef(f"_sub_{self._key}", doc_id)
        return ref

    def add(self, data: Dict) -> tuple:
        import uuid
        doc_id = str(uuid.uuid4())
        from app.demo import store as s
        if not hasattr(s, "_subcollections"):
            s._subcollections = {}
        s._subcollections.setdefault(self._key, {})[doc_id] = data
        return None, _MockDocumentRef(f"_sub_{self._key}", doc_id)

    def order_by(self, field: str, direction: str = "ASCENDING") -> "_MockQuery":
        from app.demo import store as s
        items = list(getattr(s, "_subcollections", {}).get(self._key, {}).values())
        reverse = direction.upper() == "DESCENDING"
        items.sort(key=lambda x: x.get(field) or "", reverse=reverse)
        return _MockQuery(f"_sub_{self._key}", items)

    def where(self, field: str, op: str, value: Any) -> "_MockQuery":
        from app.demo import store as s
        items = list(getattr(s, "_subcollections", {}).get(self._key, {}).values())
        q = _MockQuery(f"_sub_{self._key}", items)
        return q.where(field, op, value)


# ── Collection routing ────────────────────────────────────────────────────────

def _dispatch_set(col: str, doc_id: str, data: Dict, merge: bool = False) -> None:
    if col == "users":
        existing = _store.get_user(doc_id) or {}
        merged = {**existing, **data} if merge else data
        _store._users[doc_id] = merged
    elif col == "incidents":
        existing = _store._incidents.get(doc_id, {})
        merged = {**existing, **data} if merge else data
        _store._incidents[doc_id] = merged
    elif col == "resources":
        existing = _store._resources.get(doc_id, {})
        merged = {**existing, **data} if merge else data
        _store._resources[doc_id] = merged
    elif col == "notifications":
        _store._notifications[doc_id] = data
    elif col.startswith("settings"):
        _store._settings[doc_id] = {**_store._settings.get(doc_id, {}), **data} if merge else data
    elif col.startswith("reports"):
        if not hasattr(_store, "_reports"):
            _store._reports = {}
        _store._reports[doc_id] = data
    else:
        # Generic subcollection storage
        from app.demo import store as s
        if not hasattr(s, "_subcollections"):
            s._subcollections = {}
        s._subcollections.setdefault(col, {})[doc_id] = data


def _dispatch_update(col: str, doc_id: str, data: Dict) -> None:
    if col == "users":
        _store.update_user(doc_id, data)
    elif col == "incidents":
        _store.update_incident(doc_id, data)
    elif col == "resources":
        _store.update_resource(doc_id, data)
    elif col == "notifications":
        _store.mark_notification_read(doc_id)
    elif col.startswith("reports"):
        if not hasattr(_store, "_reports"):
            _store._reports = {}
        _store._reports.setdefault(doc_id, {}).update(data)
    else:
        from app.demo import store as s
        if not hasattr(s, "_subcollections"):
            s._subcollections = {}
        if col in s._subcollections and doc_id in s._subcollections[col]:
            s._subcollections[col][doc_id].update(data)


def _dispatch_get(col: str, doc_id: str) -> Optional[Dict]:
    if col == "users":
        return _store.get_user(doc_id)
    elif col == "incidents":
        return _store._incidents.get(doc_id)
    elif col == "resources":
        return _store._resources.get(doc_id)
    elif col == "notifications":
        return _store._notifications.get(doc_id)
    elif col.startswith("settings"):
        return _store._settings.get(doc_id)
    elif col.startswith("reports"):
        return getattr(_store, "_reports", {}).get(doc_id)
    return None


class _MockCollection:
    def __init__(self, name: str):
        self._name = name

    def _all_items(self) -> List[Dict]:
        if self._name == "users":
            return list(_store._users.values())
        elif self._name == "incidents":
            return list(_store._incidents.values())
        elif self._name == "resources":
            return list(_store._resources.values())
        elif self._name == "notifications":
            return list(_store._notifications.values())
        elif self._name == "settings":
            return list(_store._settings.values())
        elif self._name == "reports":
            return list(getattr(_store, "_reports", {}).values())
        elif self._name == "auditLogs":
            return list(getattr(_store, "_audit", {}).values())
        return []

    def document(self, doc_id: Optional[str] = None) -> _MockDocumentRef:
        if doc_id is None:
            import uuid
            doc_id = str(uuid.uuid4())
        return _MockDocumentRef(self._name, doc_id)

    def where(self, field: str, op: str, value: Any) -> _MockQuery:
        return _MockQuery(self._name, self._all_items()).where(field, op, value)

    def order_by(self, field: str, direction: str = "ASCENDING") -> _MockQuery:
        return _MockQuery(self._name, self._all_items()).order_by(field, direction)

    def limit(self, n: int) -> _MockQuery:
        return _MockQuery(self._name, self._all_items()).limit(n)

    def stream(self) -> Iterator[_MockDocument]:
        return _MockQuery(self._name, self._all_items()).stream()

    def count(self) -> _MockCountQuery:
        return _MockCountQuery(len(self._all_items()))

    def add(self, data: Dict) -> tuple:
        import uuid
        doc_id = str(uuid.uuid4())
        _dispatch_set(self._name, doc_id, {**data, "_firestoreId": doc_id})
        return None, _MockDocumentRef(self._name, doc_id)


class MockFirestoreClient:
    """Drop-in replacement for google.cloud.firestore.Client in demo mode."""

    def collection(self, name: str) -> _MockCollection:
        return _MockCollection(name)

    def batch(self):
        return _MockBatch()


class _MockBatch:
    def __init__(self):
        self._ops = []

    def update(self, ref: _MockDocumentRef, data: Dict) -> None:
        self._ops.append(("update", ref, data))

    def commit(self) -> None:
        for op, ref, data in self._ops:
            if op == "update":
                ref.update(data)


# ── Singleton ─────────────────────────────────────────────────────────────────
_mock_client: Optional[MockFirestoreClient] = None


def get_mock_firestore() -> MockFirestoreClient:
    global _mock_client
    if _mock_client is None:
        _mock_client = MockFirestoreClient()
    return _mock_client
