import time
from fastapi import Request

async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    from app.database.connection import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO api_logs (endpoint, method, request_time) VALUES (?, ?, ?)",
        (str(request.url), request.method, process_time)
    )
    conn.commit()
    conn.close()
    return response
