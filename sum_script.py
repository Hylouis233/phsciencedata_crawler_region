import os

import pandas as pd


def main() -> None:
    disease_id = int(input('请输入疾病ID：'))
    data_type = input('请输入汇总类型（age/region）：').strip().lower()

    foldername = str(disease_id)
    os.makedirs(foldername, exist_ok=True)

    source_file = os.path.join(foldername, 'final.csv')
    if not os.path.exists(source_file):
        raise FileNotFoundError(f'未找到汇总源文件：{source_file}')

    df = pd.read_csv(source_file, encoding='gbk')

    if data_type == 'age':
        group_col = '年龄分组'
    elif data_type == 'region':
        group_col = '地区'
    else:
        raise ValueError('汇总类型必须是 age 或 region')

    if group_col not in df.columns:
        raise KeyError(f'当前 final.csv 不包含列：{group_col}，请确认 process.py 的处理类型是否一致')


    numeric_cols = ['发病数', '死亡数', '发病率(1/10万)', '死亡率(1/10万)']
    for col in numeric_cols:
        if col not in df.columns:
            raise KeyError(f'当前 final.csv 不包含列：{col}，请确认文件内容完整')
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    yearly_df = (
        df.groupby([group_col, '年份'], as_index=False)
        .agg(
            发病数=('发病数', 'sum'),
            死亡数=('死亡数', 'sum'),
            **{'发病率(1/10万)': ('发病率(1/10万)', 'mean')},
            **{'死亡率(1/10万)': ('死亡率(1/10万)', 'mean')},
        )
    )

    output_file = os.path.join(foldername, f'{group_col}_year_final.csv')
    yearly_df.to_csv(output_file, index=False, header=True, encoding='gbk')
    print(f'年度汇总完成：{output_file}')


if __name__ == '__main__':
    main()
