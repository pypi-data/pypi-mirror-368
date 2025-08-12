async def safe_close(obj):
    if obj is not None:
        try:
            await obj.close()
        except Exception:
            pass