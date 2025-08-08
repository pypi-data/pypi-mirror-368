import base64

def image_to_base64(image_path: str) -> str:
    """Reads an image file and returns it as a Base64 encoded string."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        raise FileNotFoundError(f"Image file not found at path: {image_path}")