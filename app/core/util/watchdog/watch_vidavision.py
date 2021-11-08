import os
import asyncio
from pydicom import dcmread
from loguru import logger
from watchdog.events import FileSystemEventHandler, RegexMatchingEventHandler
from watchdog.observers import Observer

from app.core.config import settings
from app.core.util.watchdog.queries import update_db_on_vida_import

EVENT_TYPE_MOVED = "moved"
EVENT_TYPE_DELETED = "deleted"
EVENT_TYPE_CREATED = "created"
EVENT_TYPE_MODIFIED = "modified"
EVENT_TYPE_CLOSED = "closed"


class VidaVisionWatcher:
    def __init__(self, path, handler):
        self.observer = Observer()
        self.handler = handler()
        self.path = path

    async def _run(self):
        logger.add(f"logs/watch_VidaVision.log", level="DEBUG")
        self.observer.schedule(self.handler, self.path, recursive=True)
        self.observer.start()
        logger.info(f"Observer started: {self.path}")
        try:
            while True:
                await asyncio.sleep(2)
        except:
            self.observer.stop()
            logger.info("Observer stopped")
        self.observer.join()

    def run(self):
        asyncio.get_event_loop().run_until_complete(self._run())


class VidaImportHandler(RegexMatchingEventHandler):
    def __init__(
        self,
        regexes=["^\d+$"],
        ignore_regexes=[],
        ignore_directories=False,
        case_sensitive=False,
    ):
        super().__init__(
            regexes=regexes,
            ignore_regexes=ignore_regexes,
            ignore_directories=ignore_directories,
            case_sensitive=case_sensitive,
        )
        self._loop = asyncio.get_event_loop()
        self._ensure_future = asyncio.create_task
        self._method_map = {
            EVENT_TYPE_MODIFIED: self.on_modified,
            EVENT_TYPE_MOVED: self.on_moved,
            EVENT_TYPE_CREATED: self.on_created,
            EVENT_TYPE_DELETED: self.on_deleted,
            EVENT_TYPE_CLOSED: self.on_closed,
        }

    def _is_dicom_folder(self, event):
        return event.src_path.split("/")[-1] == "dicom"

    def _get_pid_and_acq_date(self, dcm_file_path):
        dcm = dcmread(dcm_file_path)
        return dcm.PatientID, dcm.AcquisitionDate

    def _is_dcm_header_valid(self, pid, acquisition_date):
        return

    def dispatch(self, event):
        handler = self._method_map[event.event_type]
        self._loop.call_soon_threadsafe(self._ensure_future, self.on_any_event(event))
        self._loop.call_soon_threadsafe(self._ensure_future, handler(event))

    async def on_created(self, event):
        if event.is_directory and self._is_dicom_folder(event):
            vida_case_id = event.src_path.split("/")[-2]
            logger.info("New VIDA case created - % s" % vida_case_id)
            await asyncio.sleep(5)
            dcm_file_path = os.path.join(event.src_path, os.listdir(event.src_path)[0])
            pid, acquisition_date = self._get_pid_and_acq_date(dcm_file_path)
            logger.debug(pid, acquisition_date)
            if self._is_dcm_header_valid(pid, acquisition_date):
                update_db_on_vida_import(pid, acquisition_date, vida_case_id)
            else:
                logger.warning(
                    f"New Vida case {vida_case_id} does not have valid dcm headers - pid: {pid}, acq_date: {acquisition_date}"
                )

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

    @staticmethod
    async def on_closed(event):
        pass


class DLSegmentationHandler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        # if event.is_directory:
        #     logger.info("directory event")
        #     return None
        if event.event_type == "created":
            logger.info("Watchdog received created event - % s." % event.src_path)
        elif event.event_type == "modified":
            logger.info("Watchdog received modified event - % s." % event.src_path)
        elif event.event_type == "moved":
            logger.info("Watchdog received moved event - % s." % event.src_path)
        elif event.event_type == "deleted":
            logger.info("Watchdog received deleted event - % s." % event.src_path)
        else:
            logger.info("Watchdog received closed event - % s." % event.src_path)


class VidaImportHandler2(FileSystemEventHandler):
    def _is_dicom_folder(self, event):
        return event.src_path.split("/")[-1] == "dicom"

    def _get_pid_and_acq_date(self, dicom_image_path):
        dcm = dcmread(dicom_image_path)
        return dcm.PatientID, dcm.AcquisitionDate

    async def on_any_event(self, event):
        if event.event_type == "created":
            if event.is_directory and self._is_dicom_folder(event):
                vida_case_id = event.src_path.split("/")[-2]
                logger.info(
                    "Watchdog received vida case created event - % s" % vida_case_id
                )
                await asyncio.sleep(10)
                pid, acquisition_date = self._get_pid_and_acq_date(
                    os.listdir(event.src_path)[0]
                )
                logger.debug(pid, acquisition_date)
        # elif event.event_type == "modified":
        #     logger.info("Watchdog received modified event - % s." % event.src_path)
        # elif event.event_type == "moved":
        #     logger.info("Watchdog received moved event - % s." % event.src_path)
        # elif event.event_type == "deleted":
        #     logger.info("Watchdog received deleted event - % s." % event.src_path)
        # else:
        #     logger.info("Watchdog received closed event - % s." % event.src_path)


class VidaProcessingHandler(FileSystemEventHandler):
    pass


VidaImportWatcher = VidaVisionWatcher(settings.VIDA_RESULT_PATH, VidaImportHandler)
