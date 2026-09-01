from fastapi import APIRouter , UploadFile , Response, status , Request
from helpers import get_settings
from controllers import DataController , ProjectController , BaseController , ProcessController
from fastapi.responses import JSONResponse
from controllers.Enums import DataEnums
from models import ProjectModel,ProjectModelEnums
import os

data_router = APIRouter()

@data_router.post("/file_upload/{project_id}")
async def upload_file(request : Request,file : UploadFile , project_id : str):
    settings = get_settings()
    msg , flag = DataController().validate_file(file = file)
    
    if not flag:
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = { "Response": msg }
        )
    project_controller = ProjectController()
    project_path = project_controller.create_project_path(project_id = project_id)
    
    file_path , file_id = BaseController().generate_unique_file_path(file_name = file.filename , project_path = project_path)
    
    project_model = ProjectModel(request.app.db_client)
    project = await project_model.create_new_project(project_id = project_id)
    
    if not project:
        if not flag:
            return JSONResponse(
                status_code = status.HTTP_400_BAD_REQUEST,
                content = { "Response": ProjectModelEnums.PROJECT_CREATE_FAILED.value }
            )
    
    try:
        with open(file_path, "wb") as f:
            while content := await file.read(settings.FILE_CHUNK_SIZE):
                f.write(content)
    except Exception as e:
        return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = {"Response" : DataEnums.FILE_UPLOAD_FAILED.value , "Error" : str(e)}
        )
    return JSONResponse(
        content = {"Response" : DataEnums.FILE_UPLOAD_SUCCESSFULLY.value,
                    "file_id" : file_id }
    )


@data_router.post("/processing/{project_id}")
async def process_file(project_id : str, file_id : str = None, chunk_size : int = 500, overlap_size : int = 50):
    project_controller = ProjectController()
    process_controller = ProcessController()
    project_path = project_controller.get_project_path(project_id = project_id)

    if not os.path.exists(project_path):
        return JSONResponse(status_code = status.HTTP_400_BAD_REQUEST,
                            content = {"Response" : DataEnums.PROJECT_NOT_EXIST.value})

    if file_id:
        file_path = os.path.join(project_path , file_id)
        if not os.path.exists(file_path):
            return JSONResponse(status_code = status.HTTP_400_BAD_REQUEST,
                                content = {"Response" : DataEnums.FILE_PATH_INCORRECT.value})
        
        content = process_controller.process_file(file_path = file_path , chunk_size = chunk_size, overlap_size = overlap_size)
        if content:
            formatted_content = [
                {
                    "page_content": document.page_content,
                    "metadata": document.metadata
                }
                for document in content
            ]
            return JSONResponse(
                content={
                    "Response": DataEnums.FILE_PROCESSING_SUCCESSFULLY.value,
                    "content": formatted_content
                }
            )
            
    else:
        files_content = []
        for file_name in os.listdir(project_path):
            file_path = os.path.join(project_path,file_name)

            if not os.path.isfile(file_path):
                continue

            content = process_controller.process_file(file_path=file_path,chunk_size=chunk_size,overlap_size=overlap_size)
            if content:
                formatted_content = [
                    {
                        "page_content": document.page_content,
                        "metadata": document.metadata
                    }
                    for document in content
                ]
                files_content.extend(formatted_content)

        if files_content:
            return JSONResponse(
                content={
                    "Response": DataEnums.FILE_PROCESSING_SUCCESSFULLY.value,
                    "content": files_content
                }
            )
        
    return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = {"Response" : DataEnums.FILE_PROCESSING_FAILED.value}
        )