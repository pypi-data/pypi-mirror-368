import os
import pickle

def load_model(model_path):
    with open(model_path, 'rb') as f:
        return pickle.load(f)

def load_all_models(model_dir):
    models = {}
    for name in ['kmeans', 'lof', 'svm', 'dbscan', 'optics']:
        path = os.path.join(model_dir, f'{name}.pkl')
        models[name] = load_model(path)
    return models
