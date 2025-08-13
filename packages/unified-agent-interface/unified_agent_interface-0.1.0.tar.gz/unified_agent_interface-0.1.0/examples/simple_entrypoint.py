def run(payload: dict):
    text = payload.get("input") or ""
    return f"processed:{text}"
