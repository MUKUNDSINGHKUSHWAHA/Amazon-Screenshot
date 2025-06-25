import os
import re
import datetime

def sanitize_filename(name):
    return re.sub(r'[\/:"*?<>|]+', '_', name)

def create_output_folder():
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = os.path.join("D:\\amazon_ss", now)
    os.makedirs(path, exist_ok=True)
    return path
