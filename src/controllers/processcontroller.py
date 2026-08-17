from controllers import BaseController
from .Enums import ExtensionsEnum
from langchain_community.document_loaders import TextLoader , PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from paddleocr import PaddleOCR

class ProcessController(BaseController):
    def __init__(self):
        super().__init__()
        self.ocr = PaddleOCR(lang = 'ar', enable_mkldnn=False)
        
    def process_file(self, file_path : str, chunk_size : int = 500, overlap_size : int = 50):
        file_ext = "." + file_path.split(".")[-1]
        
        if file_ext == ExtensionsEnum.TXT.value:
            loader = TextLoader(file_path = file_path , encoding = "utf-8")
            content = loader.load()
            chunks = self.process_file_content(content = content , chunk_size = chunk_size, overlap_size = overlap_size)
            return chunks

        if file_ext == ExtensionsEnum.PDF.value:
            loader = PyMuPDFLoader(file_path = file_path)
            content = loader.load()
            chunks = self.process_file_content(content = content , chunk_size = chunk_size, overlap_size = overlap_size)
            return chunks
        
        if file_ext in ExtensionsEnum.IMAGE.value:
            result = self.ocr.predict(file_path)
            
            extracted_text = []
            for res in result:
                extracted_text.extend(res["rec_texts"])
                
            text = "\n".join(extracted_text)
            
            content = [
                Document(
                    page_content=text,
                    metadata={
                        "source": file_path,
                        "type": "image",
                        "ocr": True
                    }
                )
            ]
            chunks = self.process_file_content(content = content, chunk_size = chunk_size, overlap_size = overlap_size)
            return chunks
        
        return None
    
    def process_file_content(self , content : list , chunk_size : int = 500 , overlap_size : int = 50):
        text_splitter_model = RecursiveCharacterTextSplitter(chunk_size = chunk_size, chunk_overlap = overlap_size)
        chunks = text_splitter_model.split_documents(content)
        return chunks
