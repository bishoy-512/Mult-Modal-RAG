from helpers import get_settings
import os
import uuid

class BaseController:
    def __init__(self):
        self.settings = get_settings()
        self.base_dir = os.path.dirname(os.path.dirname(__file__)) # src
        self.files_dir = os.path.join(self.base_dir,"assets","files") # src/assets/files
    
    def generate_unique_file_path(self , file_name: str, project_path: str):
        unique_file_name = f"{uuid.uuid4()}_{file_name}"
        file_path = os.path.join(project_path, unique_file_name)
        
        while os.path.exists(file_path):
            unique_file_name = f"{uuid.uuid4()}_{file_name}"
            file_path = os.path.join(project_path, unique_file_name)
            
        return file_path , unique_file_name
