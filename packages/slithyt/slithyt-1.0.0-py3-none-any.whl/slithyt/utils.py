import gzip

def open_any(file_path: str):
    """
    Opens a file, transparently handling whether it is gzipped or plain text
    by checking for the gzip magic number.

    Args:
        file_path: The path to the file to open.

    Returns:
        A file handle ready for reading in text mode.
    """
    with open(file_path, 'rb') as f:
        is_gzipped = (f.read(2) == b'\x1f\x8b')
    
    # Return the correct file handle based on the check
    if is_gzipped:
        return gzip.open(file_path, 'rt', encoding="utf-8")
    else:
        return open(file_path, 'r', encoding="utf-8")