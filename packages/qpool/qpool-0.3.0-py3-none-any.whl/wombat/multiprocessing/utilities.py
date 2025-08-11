from __future__ import annotations

def is_async_context_manager(obj):
    return hasattr(obj, "__aenter__") and hasattr(obj, "__aexit__")

def is_sync_context_manager(obj):
    return hasattr(obj, "__enter__") and hasattr(obj, "__exit__")
