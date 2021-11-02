from multiprocessing import Process
import uvicorn
from app.core.util.watchdog import VidaImportWatcher

if __name__ == "__main__":
    watch_VidaVision = Process(target=VidaImportWatcher.run).start()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
