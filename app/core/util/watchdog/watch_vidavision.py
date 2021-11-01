import asyncio
from loguru import logger
from watchdog.events import FileSystemEventHandler, RegexMatchingEventHandler
from watchdog.observers import Observer

from app.core.config import settings

EVENT_TYPE_MOVED = "moved"
EVENT_TYPE_DELETED = "deleted"
EVENT_TYPE_CREATED = "created"
EVENT_TYPE_MODIFIED = "modified"


class VidaVisionWatcher:
    def __init__(self, path, handler):
        self.observer = Observer()
        self.handler = handler()
        self.path = path
    
    async def run(self):
        logger.add(f'logs/watch_VidaVision.log', level='DEBUG')
        self.observer.schedule(self.handler, self.path, recursive=True)
        self.observer.start()
        logger.info('Observer started')
        try:
            while True:
                await asyncio.sleep(5)
        except:
            self.observer.stop()
            logger.info('Observer stopped')
        self.observer.join()


class VidaImportHandler(RegexMatchingEventHandler):
    def __init__(self, regexes=['^.*\d+$'], ignore_regexes=[], ignore_directories=False, case_sensitive=False):
        super().__init__(regexes=regexes, ignore_regexes=ignore_regexes, ignore_directories=ignore_directories, case_sensitive=case_sensitive)
        self._loop = asyncio.get_event_loop()
        self._ensure_future = asyncio.create_task
        self._method_map = {
                                EVENT_TYPE_MODIFIED: self.on_modified,
                                EVENT_TYPE_MOVED: self.on_moved,
                                EVENT_TYPE_CREATED: self.on_created,
                                EVENT_TYPE_DELETED: self.on_deleted,
                            }

    def dispatch(self, event):
        handler = self._method_map[event.event_type]
        self._loop.call_soon_threadsafe(self._ensure_future, self.on_any_event(event))
        self._loop.call_soon_threadsafe(self._ensure_future, handler(event))

    @staticmethod
    async def on_created(event):
        if event.is_directory:
            logger.info(f"New VIDA case imported: {event.src_path}")
            await asyncio.sleep(300)
            logger.info(f'wait finished: {event.src_path}')

    @staticmethod
    async def on_any_event(event):
        pass

    @staticmethod
    async def on_moved(event):
        pass

    @staticmethod
    async def on_deleted(event):
        pass

    @staticmethod
    async def on_modified(event):
        pass

class DLSegmentationHandler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        # if event.is_directory:
        #     logger.info("directory event")
        #     return None
        if event.event_type == 'created':
            logger.info("Watchdog received created event - % s." % event.src_path)
        elif event.event_type == 'modified':
            logger.info("Watchdog received modified event - % s." % event.src_path)
        elif event.event_type == 'moved':
            logger.info("Watchdog received moved event - % s." % event.src_path)
        elif event.event_type == 'deleted':
            logger.info("Watchdog received deleted event - % s." % event.src_path)


class VidaProcessingHandler(FileSystemEventHandler):
    pass


VidaImportWatcher = VidaVisionWatcher(settings.VIDA_RESULT_PATH, VidaImportHandler)