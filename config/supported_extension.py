# The Master List of Supported Extensions
SUPPORTED_EXTENSIONS = [
    # Documents
    "pdf", "txt", "docx", "csv",
    # Video/Audio
    "mp4", "mkv", "avi", "mov", "mp3", "wav",
    # Images
    "jpg", "jpeg", "png", "webp", "gif", "tiff", "bmp", "ico"
]

# We dynamically join the list into a regex OR string: "pdf|txt|docx|..."
EXT_REGEX = "|".join(SUPPORTED_EXTENSIONS)