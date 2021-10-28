import time
from loguru import logger
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler



class OnWatch:
    def __init__(self, path):
        self.observer = Observer()
        self.path = path
    
    def run(self):
        logger.add(f'logs/watchdog_{self.path}.log', level='DEBUG')
        event_handler = Handler()
        self.observer.schedule(event_handler, self.path, recursive=True)
        self.observer.start()
        logger.info('Observer started')
        try:
            while True:
                time.sleep(2)
        except:
            self.observer.stop()
            logger.info('Observer stopped')
        self.observer.join()

class Handler(FileSystemEventHandler):
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