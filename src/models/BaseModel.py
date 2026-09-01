from helpers import get_settings

class BaseModel:
    def __init__(self, db_client: object):
        self.settings = get_settings()
        self.db_client = db_client