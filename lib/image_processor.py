import subprocess
import os

def fetch_and_save_images(image_path, target_path):
    url = build_image_url(image_path)
    run(convert_command(url, target_path))

def build_image_url(date_str):
    url_base = os.environ['SATELLITE_IMAGE_URL_BASE']
    return url_base % date_str

def convert_args():
    return " -shave 20x20 -colorspace linear-gray"
    # colorspaces "linear-gray" are only available after ImageMagick 7.0.7-17

def convert_command(url, target_path):
    return f"convert {convert_args()} '{url}' '{target_path}'"

def run(cmd):
    subprocess.call(cmd, shell=True)
