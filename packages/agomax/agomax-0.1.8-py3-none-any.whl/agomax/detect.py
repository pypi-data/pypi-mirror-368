import pandas as pd
import os
import pkg_resources
from .preprocess import preprocess
from .phase import detect_phase
from .rules import RuleChecker
from .models import load_all_models

def get_resource_path(filename):
    """Get the path to a resource file included with the package."""
    # If it's an absolute path, return as-is
    if os.path.isabs(filename):
        return filename
        
    try:
        # Try pkg_resources first - this works for installed packages
        return pkg_resources.resource_filename('agomax', f'../{filename}')
    except:
        try:
            # Try looking in site-packages directory
            import agomax
            agomax_path = os.path.dirname(agomax.__file__)
            parent_dir = os.path.dirname(agomax_path)
            path = os.path.join(parent_dir, filename)
            if os.path.exists(path):
                return path
        except:
            pass
    
    try:
        # Try relative to package directory (for development)
        package_dir = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(package_dir, filename)
        if os.path.exists(path):
            return path
    except:
        pass
    
    # Fallback to filename as-is
    return filename

def agomax_detect(data_source, mode='offline', rules_path=None, model_dir=None):
    """
    Args:
        data_source: path to CSV (offline) or DataFrame (live)
        mode: 'offline' or 'live'
        rules_path: path to rules config file
        model_dir: path to models directory
    Returns:
        DataFrame with anomaly detection results
    """
    # Load data
    if mode == 'offline':
        # Try to resolve the path if it's a relative package path
        if data_source.startswith(('data/', 'configs/', 'models/')):
            data_source = get_resource_path(data_source)
        df = pd.read_csv(data_source)
    else:
        df = data_source

    # Preprocess
    df, features = preprocess(df)

    # Phase detection
    phases = detect_phase(df)

    # Resolve rules path
    if rules_path and rules_path.startswith(('data/', 'configs/', 'models/')):
        rules_path = get_resource_path(rules_path)

    # Rule checking (match prototype: count rules broken, not just names)
    rule_checker = RuleChecker(rules_path)
    broken_rules_count = []
    violated_rules_list = []
    suggestions_list = []
    for i, row in df.iterrows():
        phase = phases[i]
        violated = rule_checker.check_all(row, phase)
        broken_rules_count.append(len(violated))
        violated_rules_list.append([v[0] for v in violated])
        suggestions_list.append([v[1] for v in violated])

    # Resolve model directory path
    if model_dir and model_dir.startswith(('data/', 'configs/', 'models/')):
        model_dir = get_resource_path(model_dir)

    # ML ensemble (match prototype: use raw features, not scaled)
    models = load_all_models(model_dir)
    X = df[features].values
    kmeans_info = models['kmeans']
    kmeans = kmeans_info['model']
    centroids = kmeans_info['centroids']
    kmeans_clusters = kmeans.predict(X)
    mean = kmeans_info['mean']
    std = kmeans_info['std']
    threshold = mean + 3 * std
    kmeans_pred = []
    for i in range(len(X)):
        cluster = kmeans_clusters[i]
        centroid = centroids[cluster]
        # Match prototype: use np.sqrt(np.sum((x - centroid)**2))
        import numpy as np
        distance = np.sqrt(np.sum((X[i] - centroid) ** 2))
        if distance > threshold:
            kmeans_pred.append(-1)
        else:
            kmeans_pred.append(1)

    # Match prototype: run LOF and SVM on each point
    lof_pred = []
    for i in range(len(X)):
        pred = models['lof'].predict(X[i].reshape(1, -1))
        lof_pred.append(pred[0])
    svm_pred = []
    for i in range(len(X)):
        pred = models['svm'].predict(X[i].reshape(1, -1))
        svm_pred.append(pred[0])
    dbscan_pred = models['dbscan'].fit_predict(X)
    optics_pred = models['optics'].fit_predict(X)

    # Voting
    final_vote = []
    for i in range(len(df)):
        preds = [kmeans_pred[i], lof_pred[i], svm_pred[i], dbscan_pred[i], optics_pred[i]]
        vote = max(set(preds), key=preds.count)
        final_vote.append(vote)

    # Anomaly flag
    anomaly_flag = [(final_vote[i] < 0 or broken_rules_count[i] > 0) for i in range(len(df))]

    # Build result DataFrame
    result = pd.DataFrame({
        'timestamp': df.get('timestamp', df.index),
        'anomaly_flag': anomaly_flag,
        'broken_rules_count': broken_rules_count,
        'violated_rules_list': violated_rules_list,
        'suggested_actions': suggestions_list,
        'kmeans_pred': kmeans_pred,
        'lof_pred': lof_pred,
        'svm_pred': svm_pred,
        'dbscan_pred': dbscan_pred,
        'optics_pred': optics_pred,
        'final_vote': final_vote
    })
    return result
