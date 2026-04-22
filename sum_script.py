import os

import pandas as pd


GROUP_COLUMNS = {
    'age': '年龄分组',
    'region': '地区',
}
NUMERIC_COLUMNS = ['发病数', '死亡数', '发病率(1/10万)', '死亡率(1/10万)']


def main() -> None:
    disease_id = int(input('请输入疾病ID：'))
    data_type = input('请输入汇总类型（age/region）：').strip().lower()
    if data_type not in GROUP_COLUMNS:
        raise ValueError('汇总类型必须是 age 或 region')

    foldername = str(disease_id)
    os.makedirs(foldername, exist_ok=True)

    source_file = os.path.join(foldername, 'final.csv')
    if not os.path.exists(source_file):
        raise FileNotFoundError(f'未找到汇总源文件：{source_file}')

    df = pd.read_csv(source_file, encoding='gbk')
    df.columns = [col.lstrip('\ufeff') if isinstance(col, str) else col for col in df.columns]

    group_col = GROUP_COLUMNS[data_type]
    required_columns = [group_col, '年份', *NUMERIC_COLUMNS]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise KeyError(
            f'当前 final.csv 缺少必要列：{", ".join(missing_columns)}；'
            '请确认文件表头是否正确，且 process.py 的处理类型与当前汇总类型一致。'
        )

    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df['年份'] = pd.to_numeric(df['年份'], errors='coerce')
    df = df.dropna(subset=['年份']).copy()
    df['年份'] = df['年份'].astype(int)

    yearly_df = (
        df.groupby([group_col, '年份'], as_index=False)
        .agg(
            发病数=('发病数', 'sum'),
            死亡数=('死亡数', 'sum'),
            **{'发病率(1/10万)': ('发病率(1/10万)', 'mean')},
            **{'死亡率(1/10万)': ('死亡率(1/10万)', 'mean')},
        )
        .sort_values([group_col, '年份'], ignore_index=True)
    )

    output_file = os.path.join(foldername, f'{group_col}_year_final.csv')
    yearly_df.to_csv(output_file, index=False, header=True, encoding='gbk')
    print(f'年度汇总完成：{output_file}')


if __name__ == '__main__':
    main()
