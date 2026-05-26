"""
Descarga y prepara datos de FBref (Premier League 2024-25) para el dashboard.
Ejecutar una sola vez — guarda los datos en data/players.csv

Tablas disponibles en soccerdata: standard, shooting, misc, keeper, playing_time
"""
import warnings
warnings.filterwarnings('ignore')

import soccerdata as sd
import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent / 'data'
DATA_DIR.mkdir(exist_ok=True)
OUTPUT = DATA_DIR / 'players.csv'

LEAGUE  = 'ENG-Premier League'
SEASON  = '2024-25'
MIN_MIN = 300


def flatten_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [
        '_'.join(str(c).strip() for c in col if str(c).strip() and c not in ('', 'nan'))
        if isinstance(col, tuple) else str(col)
        for col in df.columns
    ]
    return df


def download():
    print("Conectando a FBref...")
    fbref = sd.FBref(LEAGUE, SEASON)

    print("  Descargando standard stats...")
    std = fbref.read_player_season_stats('standard')

    print("  Descargando shooting stats...")
    sht = fbref.read_player_season_stats('shooting')

    print("  Descargando misc stats...")
    msc = fbref.read_player_season_stats('misc')

    return std, sht, msc


def build_df(std, sht, msc):
    std = flatten_cols(std.reset_index())
    sht = flatten_cols(sht.reset_index())
    msc = flatten_cols(msc.reset_index())

    print("\nColumnas standard:", [c for c in std.columns if 'Prg' in c or 'xG' in c or 'Gls' in c or 'Ast' in c or 'Min' in c])
    print("Columnas shooting:", [c for c in sht.columns if 'Sh' in c or 'xG' in c or 'Dist' in c])
    print("Columnas misc:", [c for c in msc.columns if any(k in c for k in ['Int','Tkl','Recov','Won','Fls','Fld'])])

    idx = ['league', 'season', 'team', 'player']

    def pick(df, candidates):
        available = [c for c in candidates if c in df.columns]
        return df[idx + available].copy()

    std_sel = pick(std, [
        'pos', 'age',
        'Playing Time_Min', 'Playing Time_90s',
        'Performance_Gls', 'Performance_Ast',
        'Expected_xG', 'Expected_xAG',
        'Progression_PrgC', 'Progression_PrgP', 'Progression_PrgR',
        'Per 90 Minutes_Gls', 'Per 90 Minutes_Ast',
        'Per 90 Minutes_xG', 'Per 90 Minutes_xAG',
    ])

    sht_sel = pick(sht, [
        'Standard_Sh', 'Standard_SoT', 'Standard_SoT%',
        'Standard_Sh/90', 'Standard_SoT/90',
        'Expected_xG', 'Expected_npxG',
        'Standard_G/Sh', 'Standard_Dist',
    ])

    msc_sel = pick(msc, [
        'Performance_Int', 'Performance_TklW',
        'Performance_Fls', 'Performance_Fld',
        'Performance_Recov',
        'Aerial Duels_Won', 'Aerial Duels_Lost', 'Aerial Duels_Won%',
        'Per 90_Int', 'Per 90_TklW', 'Per 90_Recov',
    ])

    df = std_sel.merge(sht_sel, on=idx, how='left', suffixes=('', '_sht'))
    df = df.merge(msc_sel, on=idx, how='left')

    # Filtrar por minutos
    min_col = 'Playing Time_Min'
    if min_col in df.columns:
        df = df[pd.to_numeric(df[min_col], errors='coerce') >= MIN_MIN].copy()

    # Limpiar posición
    if 'pos' in df.columns:
        df['pos'] = df['pos'].astype(str).str.split(',').str[0].str.upper()
        df = df[df['pos'].isin(['GK', 'DF', 'MF', 'FW'])].copy()

    # Calcular métricas por 90 que no vengan ya calculadas
    s90 = pd.to_numeric(df.get('Playing Time_90s', 1), errors='coerce').replace(0, np.nan)
    if 'Progression_PrgC' in df.columns:
        df['PrgC_p90'] = pd.to_numeric(df['Progression_PrgC'], errors='coerce') / s90
    if 'Progression_PrgP' in df.columns:
        df['PrgP_p90'] = pd.to_numeric(df['Progression_PrgP'], errors='coerce') / s90
    if 'Performance_Int' in df.columns:
        df['Int_p90'] = pd.to_numeric(df['Performance_Int'], errors='coerce') / s90
    if 'Performance_TklW' in df.columns:
        df['TklW_p90'] = pd.to_numeric(df['Performance_TklW'], errors='coerce') / s90
    if 'Performance_Recov' in df.columns:
        df['Recov_p90'] = pd.to_numeric(df['Performance_Recov'], errors='coerce') / s90

    df = df.reset_index(drop=True)
    print(f"\nJugadores con >= {MIN_MIN} min: {len(df)}")
    return df


def add_percentiles(df):
    skip = ['league', 'season', 'team', 'player', 'pos', 'age', 'born']
    for col in df.columns:
        if col in skip:
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            df[f'pct_{col}'] = df.groupby('pos')[col].rank(pct=True) * 100
            df[f'pct_{col}'] = df[f'pct_{col}'].round(1)
    return df


if __name__ == '__main__':
    if OUTPUT.exists():
        OUTPUT.unlink()

    std, sht, msc = download()
    df = build_df(std, sht, msc)
    df = add_percentiles(df)
    df.to_csv(OUTPUT, index=False)
    print(f"\nGuardado en {OUTPUT}")
    print(f"Shape: {df.shape}")
    print(df[['player', 'team', 'pos', 'Playing Time_Min', 'Performance_Gls']].head(8).to_string(index=False))
