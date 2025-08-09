import datetime
import logging
import os


class LogManager:
    """Signleton class only one istance"""

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def config_logger(self, verbose, dir):
        params = {}
        levels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
        level = levels[min(len(levels) - 1, verbose)]
        params["format"] = "[%(asctime)s][%(levelname)7s][%(name)6s] %(message)s"
        params["level"] = level
        params["datefmt"] = "%Y-%m-%d %H:%M:%S"
        if dir:
            now = datetime.datetime.now()
            os.makedirs(f"{dir}/{now.year:4}-{now.month:2}-{now.day:2}", exist_ok=True)

            filename: str = (
                f"{dir}/{now.year:4}-{now.month:2}-{now.day:2}/{now.hour:2}_{now.minute:2}_{now.second:2}.txt"
            )
            params["filename"] = filename
        logging.basicConfig(**params)


if __name__ == "__main__":
    manager = LogManager()
    manager.config_logger(
        3,
        "/home/alan/tmp",
    )
    logger = logging.getLogger("rstsdr")
    logger.debug("This is debug")
    logger.info("This is info")
    logger.warning("This is warning")
    logger.error("This is error")
