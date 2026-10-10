from pathlib import Path
from django.core.exceptions import ValidationError

MAX_IMAGE_SIZE_MB = 5
VALID_IMAGE_EXTENSTIONS = ['.jpeg', '.jpg', '.png', '.webp', '.gif']

def validate_image_size(image):
    if image.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise ValidationError(f'Image can\'t be more than {MAX_IMAGE_SIZE_MB}MB.')

def validate_image_entenstion(image):
    extension = Path(image.name).suffix.lower()
    if extension not in VALID_IMAGE_EXTENSTIONS:
        raise ValidationError(f'Unsupported image format. Use: {VALID_IMAGE_EXTENSTIONS}')