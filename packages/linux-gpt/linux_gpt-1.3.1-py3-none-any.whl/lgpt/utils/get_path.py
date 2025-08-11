import os

def get_path(file_name: str) -> str:
    base_path = os.path.dirname(__file__)
    path = os.path.join(base_path, file_name)
    
    return path