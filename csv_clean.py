#!/usr/bin/env python3
# csv_clean.py
import pandas as pd
import sys
from pathlib import Path

def clean_csv(infile, outfile):
    infile = Path(infile)
    outfile = Path(outfile)

    # 試しにUTF-8で読み、ダメならShift_JISでリトライ（日本語CSV対策）
    try:
        df = pd.read_csv(infile, dtype=str, encoding='utf-8')
    except Exception:
        df = pd.read_csv(infile, dtype=str, encoding='cp932', errors='replace')

    # 不要列（Unnamed や FILLER系）を削除
    drop_cols = [c for c in df.columns if 'unnamed' in str(c).lower() or str(c).upper().startswith('FILLER')]
    if drop_cols:
        df.drop(columns=drop_cols, inplace=True, errors='ignore')

    # 日付っぽい列を 'YYYY-MM-DD' に整形
    for col in df.columns:
        if 'date' in str(col).lower() or '日付' in str(col):
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')

    # 数値っぽい列はカンマ削除して数値化（可能なら）
    for col in df.columns:
        if df[col].astype(str).str.contains(r'[0-9,]+\Z', na=False).any():
            df[col] = df[col].astype(str).str.replace(',', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 欠損は空文字に
    df.fillna('', inplace=True)

    # 出力（utf-8-sig で Excelで開けるように）
    outfile_parent = outfile.parent
    if not outfile_parent.exists():
        outfile_parent.mkdir(parents=True, exist_ok=True)

    if str(outfile).lower().endswith(('.xls', '.xlsx')):
        df.to_excel(outfile, index=False)
    else:
        df.to_csv(outfile, index=False, encoding='utf-8-sig')

    print(f"[OK] saved -> {outfile}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("usage: python csv_clean.py input.csv output.csv(or .xlsx)")
        sys.exit(1)
    clean_csv(sys.argv[1], sys.argv[2])
