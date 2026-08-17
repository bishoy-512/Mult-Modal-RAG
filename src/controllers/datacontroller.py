from controllers import BaseController
from fastapi import UploadFile
from .Enums import DataEnums

class DataController(BaseController):
    def __init__(self):
        super().__init__()
    
    def validate_file(self , file : UploadFile):
        if file.size > self.settings.FILE_MAXIMUM_SIZE:
            return DataEnums.FILE_EXCEED_MAXIMUM_SIZE.value , False
        if file.content_type not in self.settings.FILE_ALLOWED_TYPES:
            return DataEnums.FILE_TYPE_NOT_ALLOWED.value , False
        return DataEnums.FILE_VALIDATING_SUCCESSFULLY.value , True