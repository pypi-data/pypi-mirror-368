def detect_phase(df):
    if 'PHASE' in df.columns:
        return df['PHASE']
    else:
        return ['ON MISSION'] * len(df)
