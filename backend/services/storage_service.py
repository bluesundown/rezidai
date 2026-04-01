import logging
import os
import uuid
from config import CONFIG

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.uploads_dir = CONFIG['images'].get('uploads_dir', './uploads')
    
    def generate_unique_filename(self, original_filename: str) -> str:
        ext = original_filename.split('.')[-1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        return unique_name
    
    def get_listing_upload_path(self, listing_id: str) -> str:
        return f"{self.uploads_dir}/{listing_id}"
    
    def delete_image(self, file_path: str) -> bool:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Image deleted: {file_path}")
                return True
            logger.warning(f"Image not found for deletion: {file_path}")
            return False
        except PermissionError as e:
            logger.error(f"Permission denied deleting image {file_path}: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Error deleting image {file_path}: {e}", exc_info=True)
            return False
    
    def delete_listing_images(self, listing_id: str) -> bool:
        try:
            listing_path = f"{self.uploads_dir}/{listing_id}"
            if os.path.exists(listing_path):
                count = 0
                for filename in os.listdir(listing_path):
                    file_path = os.path.join(listing_path, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        count += 1
                os.rmdir(listing_path)
                logger.info(f"Deleted {count} images for listing: {listing_id}")
                return True
            logger.warning(f"Listing images directory not found: {listing_path}")
            return True
        except PermissionError as e:
            logger.error(f"Permission denied deleting listing images {listing_id}: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Error deleting listing images for {listing_id}: {e}", exc_info=True)
            return False
    
    def get_file_size(self, file_path: str) -> int:
        try:
            return os.path.getsize(file_path)
        except Exception as e:
            logger.warning(f"Could not get file size for {file_path}: {e}")
            return 0

storage_service = StorageService()
