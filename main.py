from dotenv import load_dotenv
import logging
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Use UTF-8 for log handlers so Unicode (e.g. U+2011) doesn't raise on Windows cp1252
def _stream_handler():
    if sys.platform == "win32":
        import io
        stream = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
        return logging.StreamHandler(stream)
    return logging.StreamHandler()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # File handler for general application logs (UTF-8)
        logging.FileHandler("logs/app.log", encoding="utf-8"),
        # Stream handler for console output (UTF-8 on Windows)
        _stream_handler(),
    ],
)

# Suppress verbose fontTools logging
logging.getLogger('fontTools').setLevel(logging.WARNING)
logging.getLogger('fontTools.subset').setLevel(logging.WARNING)
logging.getLogger('fontTools.ttLib').setLevel(logging.WARNING)

# Create logger instance
logger = logging.getLogger(__name__)

load_dotenv()

from backend.server.app import app

if __name__ == "__main__":
    import uvicorn
    import os
    
    logger.info("Starting server...")
    port = int(os.getenv("PORT", 8067))
    uvicorn.run(app, host="0.0.0.0", port=port)