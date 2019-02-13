import pickle
from skimage import io

THRESHOLD = -0.96

with open('./data/weather_nmf_nmf.pickle', 'rb') as fp:
    best_nmf = pickle.load(fp)

with open('./data/weather_nmf_svc.pickle', 'rb') as fp:
    best_svc = pickle.load(fp)

def evaluate_images(*raw_images):
    normalized_images = [image.ravel()/255. for image in raw_images]

    target_nmf = best_nmf.transform(normalized_images)
    confidence_scores = best_svc.decision_function(target_nmf) - THRESHOLD
    predictions = [True if score >= 0 else False for score in confidence_scores]
    return confidence_scores, predictions

def read_images(*target_paths):
    images = []
    for path in target_paths:
        images.append(io.imread(path))
    return images

