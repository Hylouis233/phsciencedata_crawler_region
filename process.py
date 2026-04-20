import os
import xml.etree.ElementTree as ET

import pandas as pd


def parse_excel_xml(xml_file: str) -> pd.DataFrame:
    """Parse XML-based xls exported from phsciencedata into a DataFrame."""
    root = ET.parse(xml_file).getroot()
    ns = '{urn:schemas-microsoft-com:office:spreadsheet}'
    data = []

    for worksheet in root.findall(f'{ns}Worksheet'):
        for table in worksheet.findall(f'{ns}Table'):
            for row in table.findall(f'{ns}Row'):
                row_data = []
                for cell in row.findall(f'{ns}Cell'):
                    data_element = cell.find(f'{ns}Data')
                    cell_data = data_element.text if data_element is not None else ''
                    row_data.append(cell_data)
                data.append(row_data)

    df = pd.DataFrame(data)
    # 跳过标题和空白行，去掉最右侧汇总行
    df = df.iloc[3 : len(df) - 1, 1:]
    df = df.reset_index(drop=True)
    df = df.replace(r'^\s*$', '0', regex=True)
    return df.astype('float', errors='ignore')


def main() -> None:
    year_1 = int(input('请输入起始年份：'))
    year_2 = int(input('请输入终止年份：'))
    disease_id = int(input('请输入疾病ID：'))
    data_type = input('请输入处理类型（age/region）：').strip().lower()

    foldername = str(disease_id)
    os.makedirs(foldername, exist_ok=True)

    if data_type == 'age':
        template_file = 'template_age.csv'
    elif data_type == 'region':
        template_file = 'template_region.csv'
    else:
        raise ValueError('处理类型必须是 age 或 region')

    final_df = pd.read_csv(template_file, encoding='UTF-8', header=None)

    for year in range(year_1, year_2 + 1):
        for month in range(1, 13):
            filename = f'{year}-{month}.xls'
            xml_file = os.path.join(foldername, filename)
            if not os.path.exists(xml_file):
                print(f'警告：文件不存在，已跳过 -> {xml_file}')
                continue

            monthly_df = parse_excel_xml(xml_file)
            monthly_df.loc[:, len(monthly_df.columns) + 1] = year
            monthly_df.loc[:, len(monthly_df.columns) + 1] = month
            final_df = pd.concat([final_df, monthly_df], axis=0, ignore_index=True)

    output_file = os.path.join(foldername, 'final.csv')
    final_df.to_csv(output_file, index=False, header=False, encoding='gbk')
    print(f'处理完成：{output_file}')


if __name__ == '__main__':
    main()
