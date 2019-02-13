import subprocess

def fetch_and_save_images(image_path, target_path):
    url = build_image_url(image_path)
    run(convert_command(url, target_path))

def build_image_url(date_str):
    return f"https://storage.tenki.jp/archive/satellite/{date_str}/japan-near-small.jpg"

def convert_args():
    return " -shave 20x20 -colorspace linear-gray"
    # colorspaces "linear-gray" are only available after ImageMagick 7.0.7-17

def convert_command(url, target_path):
    return f"convert {convert_args()} '{url}' '{target_path}'"

def run(cmd):
    subprocess.call(cmd, shell=True)
