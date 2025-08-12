import json

from datetime import datetime
from loguru import logger

from .models import HistoryList, HistoryModel

class History:
    def __init__(self, history_path: str = "history.json", history_size: int = -1):
        self.history_path = history_path
        self.history_size = history_size
        self.new = HistoryModel(datetime=datetime.now())

    def load(self) -> HistoryList:
        try:
            f = open(self.history_path, "r")
            h = f.read()
            f.close()
            data = json.loads(h)
            return HistoryList(**data)
        except Exception as e:
            logger.warning(e)
            data = HistoryList(history=[HistoryModel(datetime=datetime.now())])
            f = open(self.history_path, "w")
            f.write(json.dumps(data.model_dump(mode="json")))
            f.close()
            return data

    def save(self) -> bool:
        history_data = self.load()
        history_data.history.append(self.new)
        try:
            f = open(self.history_path, "w")
            f.write(json.dumps(history_data.model_dump(mode="json")))
            f.close()
            self.new = HistoryModel(datetime=datetime.now())
            return True
        except Exception as e:
            logger.warning(e)
            return False
