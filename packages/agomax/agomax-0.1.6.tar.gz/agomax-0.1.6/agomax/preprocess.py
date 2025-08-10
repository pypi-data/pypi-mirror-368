import pandas as pd
from sklearn.preprocessing import StandardScaler

def preprocess(df):
    df = df.copy()
    df = df.fillna(0)
    if 'airspeed' in df.columns:
        df['airspeedchange'] = df['airspeed'] - df['airspeed'].shift(1)
        df['airspeedchange'] = df['airspeedchange'].fillna(0)
    features = ['roll', 'pitch', 'yaw', 'rollspeed', 'pitchspeed', 'yawspeed', 'airspeedchange']
    for feat in features:
        if feat not in df.columns:
            df[feat] = 0
    # Match prototype: do NOT scale features for scoring, use raw values
    return df, features
