import pandas as pd
import os

raw = r'C:\Users\GEO\Desktop\IRise\data\raw'

for f in sorted(os.listdir(raw)):
    if not f.endswith('.csv'):
        continue
    path = os.path.join(raw, f)
    print('\n' + '='*70)
    print('FILE:', f)
    print('='*70)
    loaded = False
    for enc in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
        for skip in [0, 1, 2]:
            try:
                df = pd.read_csv(path, encoding=enc, skiprows=skip, nrows=5, on_bad_lines='skip')
                if df.shape[1] < 2:
                    continue
                print(f'Encoding={enc}, Skip={skip}, Shape={df.shape}')
                print('Columns:', list(df.columns))
                print(df.head(3).to_string())
                loaded = True
                break
            except Exception:
                continue
        if loaded:
            break
    if not loaded:
        print('FAILED TO PARSE')
