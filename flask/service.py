import os
import lib

def do_evaluate(base_date):
    image_paths, local_paths = expand_image_paths(base_date)
    fetch_and_save_unless_exists(image_paths, local_paths)

    raw_images = lib.read_images(*local_paths)
    confidence_scores, predictions = lib.evaluate_images(*raw_images)
    return confidence_scores, predictions, local_paths

def expand_image_paths(base_date):
    image_paths, local_paths = [], []

    for i, hour in enumerate(['09', '21']):
        image_paths.append(build_image_path(base_date, hour))
        local_paths.append(build_local_path(image_paths[i]))
    return image_paths, local_paths

def fetch_and_save_unless_exists(image_paths, local_paths):
    for image_path, local_path in zip(image_paths, local_paths):
        if not os.path.exists(local_path):
            lib.fetch_and_save_images(image_path, local_path)

def build_image_path(target_date, hour):
    return target_date.strftime(f'%Y/%m/%d/{hour}/00/00')

def build_local_path(date_str):
    filename = date_str.replace('/','_')
    return f"static/{filename}.jpg"
