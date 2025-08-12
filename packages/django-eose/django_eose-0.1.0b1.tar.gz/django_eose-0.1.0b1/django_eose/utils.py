from typing import Any

def build_proc_qs(qs, related_field: str | None, only_fields: tuple[str, ...] | None):
    """
    Returns a queryset optimized for fetching: select_related for single-valued relations
    and .only(...) on the correct model (base or related path). Always includes base pk.
    """
    if related_field:
        # For forward single-valued relationships (FK/OneToOne), select_related is ideal
        qs = qs.select_related(related_field)

    if only_fields:
        if related_field:
            rel_only = [f"{related_field}__{f}" for f in only_fields]
            qs = qs.only("pk", *rel_only)
        else:
            qs = qs.only("pk", *only_fields)
    else:
        # Even if we don't limit columns, having select_related already helps avoid N+1.
        pass

    return qs

def resolve_related_field(obj: Any, related_field: str | None):
    """
    Loops through chained attributes using '__' as a delimiter.
    Ex.: resolve_related_field(obj, 'order__client') -> obj.order.client
    """
    if not related_field:
        return obj
    try:
        for attr in related_field.split('__'):
            obj = getattr(obj, attr)
        return obj
    except AttributeError:
        return None

def make_cache_key(model_label: str, qs_signature: str, search: str, fields: tuple[str, ...], related_field: str | None):
    """
    Generates a stable cache key for the combination of queryset, search and fields.
    """
    import hashlib
    base = f"{model_label}|{qs_signature}|{search}|{','.join(fields)}|{related_field or ''}"
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()
    return f"dds:{digest}"
