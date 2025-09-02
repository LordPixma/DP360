
def validate_uuid(val: str) -> bool:
    try:
        import uuid
        uuid.UUID(val)
        return True
    except Exception:
        return False
