from fastapi import APIRouter , UploadFile , Response, status , Request
from helpers import get_settings
from controllers import DataController , ProjectController , BaseController , ProcessController
from fastapi.responses import JSONResponse
from controllers.Enums import DataEnums
from models import ProjectModel,ProjectModelEnums,ChunkModel
from models.db_schemes import Chunk
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
async def process_file(request : Request, project_id : str, file_id : str = None, chunk_size : int = 500, overlap_size : int = 50, do_reset : bool = False):
    project_controller = ProjectController()
    process_controller = ProcessController()
    
    project_path = project_controller.get_project_path(project_id = project_id)
    project_model = ProjectModel(request.app.db_client)
    project = await project_model.get_exist_project(project_id=project_id)

    chunk_model = ChunkModel(request.app.db_client)

    if (not os.path.exists(project_path)) or (not project):
        return JSONResponse(status_code = status.HTTP_400_BAD_REQUEST,
                            content = {"Response" : DataEnums.PROJECT_NOT_EXIST.value})


    if file_id:
        file_path = os.path.join(project_path , file_id)
        
        if not os.path.exists(file_path):
            return JSONResponse(status_code = status.HTTP_400_BAD_REQUEST,
                                content = {"Response" : DataEnums.FILE_PATH_INCORRECT.value})
        if do_reset:
            no_rows_deleted = await chunk_model.delete_chunks_by_project_id(project_id=project_id)
        
        content = process_controller.process_file(file_path = file_path , chunk_size = chunk_size, overlap_size = overlap_size)
        if content:
            start = await chunk_model.get_max_chunk_order(project_id=project_id)
            chunks = [
                Chunk(
                    chunk_project_id = project_id,
                    chunk_text = chunk.page_content,
                    chunk_metadata = chunk.metadata,
                    chunk_order = start + i + 1,
                ) 
                for i, chunk in enumerate(content)
                ]
            for chunk in chunks:
                await chunk_model.create_chunk(chunk=chunk)
            
            return JSONResponse(
                content={
                    "Response": DataEnums.FILE_PROCESSING_SUCCESSFULLY.value,
                }
            )
            
    else:
        if do_reset:
            no_rows_deleted = await chunk_model.delete_chunks_by_project_id(project_id=project_id)
            
        for file_name in os.listdir(project_path):
            file_path = os.path.join(project_path,file_name)

            if not os.path.isfile(file_path):
                continue

            content = process_controller.process_file(file_path=file_path,chunk_size=chunk_size,overlap_size=overlap_size)
            if content:
                start = await chunk_model.get_max_chunk_order(project_id=project_id)
                chunks = [
                    Chunk(
                        chunk_project_id = project_id,
                        chunk_text = chunk.page_content,
                        chunk_metadata = chunk.metadata,
                        chunk_order = start + i + 1,
                    ) 
                    for i, chunk in enumerate(content)
                    ]
                for chunk in chunks:
                    await chunk_model.create_chunk(chunk=chunk)

        return JSONResponse(
            content={
                "Response": DataEnums.FILE_PROCESSING_SUCCESSFULLY.value,
            }
        )
        
    return JSONResponse(
            status_code = status.HTTP_400_BAD_REQUEST,
            content = {"Response" : DataEnums.FILE_PROCESSING_FAILED.value}
        )