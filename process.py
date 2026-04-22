import os
import xml.etree.ElementTree as ET

import pandas as pd


METRIC_COLUMNS = ['发病数', '死亡数', '发病率(1/10万)', '死亡率(1/10万)']
DATE_COLUMNS = ['年份', '月份']
DIMENSION_LABELS = {
    'age': '年龄分组',
    'region': '地区',
}


def parse_excel_xml(xml_file: str) -> pd.DataFrame:
    """Parse XML-based xls exported from phsciencedata into a DataFrame."""
    root = ET.parse(xml_file).getroot()
    ns = '{urn:schemas-microsoft-com:office:spreadsheet}'
    data = []

    for worksheet in root.findall(f'{ns}Worksheet'):
        for table in worksheet.findall(f'{ns}Table'):
            for row in table.findall(f'{ns}Row'):
                row_data = []
                col_idx = 0
                for cell in row.findall(f'{ns}Cell'):
                    index_attr = cell.attrib.get(f'{ns}Index')
                    if index_attr:
                        target_col = int(index_attr) - 1
                        while col_idx < target_col:
                            row_data.append('')
                            col_idx += 1

                    data_element = cell.find(f'{ns}Data')
                    cell_data = data_element.text if data_element is not None else ''
                    row_data.append(cell_data)
                    col_idx += 1

                    merge_across = int(cell.attrib.get(f'{ns}MergeAcross', 0))
                    for _ in range(merge_across):
                        row_data.append('')
                        col_idx += 1

                data.append(row_data)

    max_cols = max((len(row) for row in data), default=0)
    normalized_data = [row + [''] * (max_cols - len(row)) for row in data]
    df = pd.DataFrame(normalized_data)
    # 跳过标题和空白行，去掉最右侧汇总行。
    df = df.iloc[3 : len(df) - 1, 1:]
    df = df.reset_index(drop=True)
    df.columns = range(df.shape[1])
    df = df.replace(r'^\s*$', '0', regex=True)
    return df.astype('float', errors='ignore')


def load_template_columns(template_file: str, dimension_col: str) -> list[str]:
    """Load header labels and normalize historical template files to the current schema."""
    template_values = (
        pd.read_csv(template_file, encoding='utf-8-sig', header=None)
        .iloc[0]
        .dropna()
        .astype(str)
        .tolist()
    )
    expected_columns = [dimension_col, *METRIC_COLUMNS, *DATE_COLUMNS]

    if len(template_values) == len(expected_columns):
        return [dimension_col, *template_values[1:]]

    if len(template_values) > len(expected_columns):
        return [dimension_col, *template_values[1 : 1 + len(METRIC_COLUMNS)], *template_values[-2:]]

    raise ValueError(
        f'模板文件列数不足：{template_file}，'
        f'期望至少 {len(expected_columns)} 列，实际只有 {len(template_values)} 列。'
    )


def main() -> None:
    year_1 = int(input('请输入起始年份：'))
    year_2 = int(input('请输入终止年份：'))
    if year_1 > year_2:
        raise ValueError('起始年份不能大于终止年份')

    disease_id = int(input('请输入疾病ID：'))
    data_type = input('请输入处理类型（age/region）：').strip().lower()
    if data_type not in DIMENSION_LABELS:
        raise ValueError('处理类型必须是 age 或 region')

    foldername = str(disease_id)
    os.makedirs(foldername, exist_ok=True)

    template_file = f'template_{data_type}.csv'
    template_columns = load_template_columns(template_file, DIMENSION_LABELS[data_type])
    expected_monthly_columns = len(template_columns) - len(DATE_COLUMNS)
    final_df = pd.DataFrame(columns=template_columns)

    for year in range(year_1, year_2 + 1):
        for month in range(1, 13):
            filename = f'{year}-{month}.xls'
            xml_file = os.path.join(foldername, filename)
            if not os.path.exists(xml_file):
                print(f'警告：文件不存在，已跳过 -> {xml_file}')
                continue

            monthly_df = parse_excel_xml(xml_file)
            if monthly_df.shape[1] != expected_monthly_columns:
                raise ValueError(
                    f'{xml_file} 列数异常：'
                    f'期望 {expected_monthly_columns} 列，实际 {monthly_df.shape[1]} 列。'
                )

            monthly_df.columns = template_columns[:-2]
            monthly_df['年份'] = year
            monthly_df['月份'] = month
            final_df = pd.concat([final_df, monthly_df], axis=0, ignore_index=True)

    output_file = os.path.join(foldername, 'final.csv')
    final_df.to_csv(output_file, index=False, encoding='gbk')
    print(f'处理完成：{output_file}')


if __name__ == '__main__':
    main()
