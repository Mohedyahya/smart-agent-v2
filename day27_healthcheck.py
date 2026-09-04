import os
import sqlite3
from fastapi import FastAPI, Response, status
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Day 27: Production Healthcheck Agent")

def check_db_connection() -> bool:
    """Verify SQLite connection and read access."""
    try:
        conn = sqlite3.connect("agent.db")
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        conn.close()
        return True
    except Exception:
        return False

@app.get("/health")
async def health_check(response: Response):
    """Production health check endpoint for monitoring uptime and dependencies."""
    db_ok = check_db_connection()
    token_configured = os.getenv("WHATSAPP_TOKEN") is not None
    
    health_status = {
        "status": "healthy" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected",
        "whatsapp_token_present": token_configured,
        "environment": "Termux (Android Native)"
    }
    
    if not db_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        
    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("day27_healthcheck:app", host="0.0.0.0", port=8000, reload=True)

