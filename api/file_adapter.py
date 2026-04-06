from fastapi import FastAPI, UploadFile, File, HTTPException, Request

class FastAPIFileAdapter:
    """
    Adapt FastAPI UploadFile -> .name + .getbuffer() API
    """
    
    def __init__(self, upload_file:UploadFile):
        self.upload_file = upload_file
        self.name = upload_file.filename
        
    def getbuffer(self) -> bytes:
        self.upload_file.file.seek(0)
        return self.upload_file.file.read()