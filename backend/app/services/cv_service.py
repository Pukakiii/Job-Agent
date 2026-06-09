from uuid import UUID, uuid4

import filetype

from app.core.config import Settings
from app.core.logger import get_logger
from app.exceptions import CVFileTooLarge, CVNotFound, EmptyCVFile, UnsupportedCVType
from app.integrations.s3 import S3
from app.models.cv import CV
from app.repositories.cv_repo import CVRepository

logger = get_logger("app.services.cv_service")

class CVService: 
    """Orchestrates CV file handling: validate the bytes, store them in S3, and
    keep the cvs metadata row in sync. HTTP-agnostic — raises domain exceptions."""

    def __init__(self, repo: CVRepository, s3: S3, settings: Settings):
        self.repo = repo
        self.s3 = s3
        self.settings = settings

    async def upload(self, user_id: UUID, original_filename: str, file_bytes: bytes) -> CV: 
        if not file_bytes: 
            raise EmptyCVFile("Uploaded CV file is empty.")
        if len(file_bytes) > self.settings.CV_MAX_BYTES: 
            raise CVFileTooLarge(f"File exceeds the {self.settings.CV_MAX_BYTES} byte limit.")
        
        kind = filetype.guess(file_bytes) # sniff magic bytes; ignore the filename
        if kind is None or kind.mime not in self.settings.CV_ALLOWED_MIME:
            raise UnsupportedCVType("Only PDF and DOCX files are accepted.")
        
        # Our own key - never the user's filename. 
        # S3 first, then the DB row, so a failure cant leave a row pointing at a missing object. 
        s3_key = f"cvs/{user_id}/{uuid4()}.{kind.extension}"
        await self.s3.upload_cv(s3_key, file_bytes, kind.mime)
        try: 
            return await self.repo.create(user_id, s3_key, original_filename, kind.mime)
        except Exception:
            await self.s3.delete_objects([s3_key]) # delete the orphan  
            raise

    async def get_download_url(self, user_id: UUID, cv_id: UUID) -> tuple[str, int]: 
        cv = await self.repo.get_by_id(cv_id)
        if cv is None or cv.user_id != user_id:
            raise CVNotFound("CV not found.") # 404 
        ttl = self.settings.CV_DOWNLOAD_URL_TTL_SECONDS
        url = await self.s3.presign_get(cv.s3_key, expires_in=ttl) 
        return url, ttl 

    async def delete(self, user_id: UUID, cv_id: UUID) -> None: 
        cv = await self.repo.get_by_id(cv_id)
        if cv is None or cv.user_id != user_id:
            raise CVNotFound("CV not found.") 
        await self.s3.delete_objects([cv.s3_key])
        await self.repo.delete(cv)
        
