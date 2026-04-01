import logging
from PIL import Image, ImageEnhance, ImageFilter
import io
import os
from config import CONFIG

logger = logging.getLogger(__name__)

class ImageService:
    def __init__(self):
        self.uploads_dir = CONFIG['images'].get('uploads_dir', './uploads')
        self.max_file_size = CONFIG['images'].get('max_file_size_mb', 20) * 1024 * 1024
        self.allowed_formats = CONFIG['images'].get('allowed_formats', ['jpg', 'jpeg', 'png', 'webp'])
        self.thumbnail_size = CONFIG['images'].get('thumbnail_size', 300)
    
    def is_valid_format(self, filename: str) -> bool:
        ext = filename.split('.')[-1].lower()
        return ext in self.allowed_formats
    
    def save_image(self, image_data: bytes, listing_id: str, filename: str) -> dict:
        try:
            os.makedirs(f"{self.uploads_dir}/{listing_id}", exist_ok=True)
            
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            
            original_filename = f"{listing_id}/{filename}"
            file_path = f"{self.uploads_dir}/{original_filename}"
            
            image.save(file_path)
            
            thumbnail_filename = f"thumb_{filename}"
            thumbnail_path = f"{self.uploads_dir}/{listing_id}/{thumbnail_filename}"
            
            thumbnail = image.copy()
            thumbnail.thumbnail((self.thumbnail_size, self.thumbnail_size), Image.Resampling.LANCZOS)
            thumbnail.save(thumbnail_path)
            
            logger.info(f"Image saved: {filename} for listing {listing_id} ({width}x{height})")
            
            return {
                "original_filename": filename,
                "stored_filename": filename,
                "file_path": f"/uploads/{original_filename}",
                "thumbnail_path": f"/uploads/{listing_id}/{thumbnail_filename}",
                "width": width,
                "height": height,
                "file_size": len(image_data)
            }
        except Exception as e:
            logger.error(f"Error saving image {filename} for listing {listing_id}: {e}", exc_info=True)
            return None
    
    def enhance_image(self, image_path: str) -> str:
        try:
            image = Image.open(image_path)
            
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.1)
            
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.05)
            
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.1)
            
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)
            
            enhanced_path = image_path.replace('.', '_enhanced.')
            image.save(enhanced_path)
            
            logger.info(f"Image enhanced: {image_path} -> {enhanced_path}")
            
            return enhanced_path
        except Exception as e:
            logger.error(f"Error enhancing image {image_path}: {e}", exc_info=True)
            return image_path
    
    def get_image_info(self, image_path: str) -> dict:
        try:
            with Image.open(image_path) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode
                }
        except Exception as e:
            logger.error(f"Error getting image info for {image_path}: {e}", exc_info=True)
            return None

image_service = ImageService()
