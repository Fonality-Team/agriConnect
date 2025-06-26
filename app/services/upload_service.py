from abc import ABC, abstractmethod
import os
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import current_app

class UploadService(ABC):
    @abstractmethod
    def upload_file(self, file: FileStorage, folder: str) -> str:
        """Upload a file and return its URL."""
        pass

class LocalFileUpload(UploadService):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    def __init__(self, upload_dir: str = 'static/uploads'):
        self.upload_dir = upload_dir

    def allowed_file(self, filename: str | None) -> bool:
        """Check if the file extension is allowed."""
        if filename is None:
            return False
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def upload_file(self, file: FileStorage, folder: str) -> str:
        """Upload a file to the specified folder and return its URL."""

        if not file or not self.allowed_file(file.filename):
            raise ValueError('Invalid file or file type not allowed')

        # Ensure the upload directory exists
        upload_path = os.path.join(current_app.root_path, self.upload_dir, folder)
        os.makedirs(upload_path, exist_ok=True)

        # Secure the filename and save the file
        filename = secure_filename(file.filename) # type: ignore
        file_path = os.path.join(upload_path, filename)
        file.save(file_path)

        # Generate the URL (relative to the static folder)
        url = f"/{self.upload_dir}/{folder}/{filename}"
        return url
