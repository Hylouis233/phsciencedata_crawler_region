import os

import pandas as pd

from schema import METRIC_COLUMNS, get_dimension_column, get_required_columns


def main() -> None:
    disease_id = int(input('请输入疾病ID：'))
    data_type = input('请输入汇总类型（age/region）：').strip().lower()
    group_col = get_dimension_column(data_type)

    foldername = str(disease_id)
    os.makedirs(foldername, exist_ok=True)

    source_file = os.path.join(foldername, 'final.csv')
    if not os.path.exists(source_file):
        raise FileNotFoundError(f'未找到汇总源文件：{source_file}')

    df = pd.read_csv(source_file, encoding='gbk')
    df.columns = [col.lstrip('\ufeff') if isinstance(col, str) else col for col in df.columns]

    required_columns = get_required_columns(data_type)
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise KeyError(
            f'当前 final.csv 缺少必要列：{", ".join(missing_columns)}；'
            '请确认文件表头是否正确，且 process.py 的处理类型与当前汇总类型一致。'
        )

    for col in METRIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df['年份'] = pd.to_numeric(df['年份'], errors='coerce')
    df = df.dropna(subset=['年份']).copy()
    df['年份'] = df['年份'].astype(int)

    cases_col, deaths_col, incidence_col, mortality_col = METRIC_COLUMNS
    yearly_df = (
        df.groupby([group_col, '年份'], as_index=False)
        .agg(
            **{
                cases_col: (cases_col, 'sum'),
                deaths_col: (deaths_col, 'sum'),
                incidence_col: (incidence_col, 'mean'),
                mortality_col: (mortality_col, 'mean'),
            }
        )
        .sort_values([group_col, '年份'], ignore_index=True)
    )

    output_file = os.path.join(foldername, f'{group_col}_year_final.csv')
    yearly_df.to_csv(output_file, index=False, header=True, encoding='gbk')
    print(f'年度汇总完成：{output_file}')


if __name__ == '__main__':
    main()
