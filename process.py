import pandas as pd
import os
import xml.etree.ElementTree as ET
import xmltodict
import re
import csv

year_1=int(input("请输入起始年份："))
year_2=int(input("请输入终止年份："))
diseaseId=int(input("请输入疾病ID："))
foldername = str(diseaseId)
os.makedirs(foldername, exist_ok=True)
finaldf = pd.read_csv('template.csv', encoding='UTF-8', header=None)
# finaldf = finaldf.values.tolist()
for i in range(year_1, year_2 + 1):
    for j in range(1, 13):
        filename = str(i) + "-" + str(j) + ".xls"
        xml_data = open(os.path.join(foldername, filename), 'r', encoding='UTF-8').read()
        xml_file = os.path.join(foldername, filename)
        root = ET.parse(xml_file).getroot()
        data = []
        for worksheet in root.findall('{urn:schemas-microsoft-com:office:spreadsheet}Worksheet'):
            for table in worksheet.findall('{urn:schemas-microsoft-com:office:spreadsheet}Table'):
                for row in table.findall('{urn:schemas-microsoft-com:office:spreadsheet}Row'):
                    row_data = []
                    for cell in row.findall('{urn:schemas-microsoft-com:office:spreadsheet}Cell'):
                        data_element = cell.find('{urn:schemas-microsoft-com:office:spreadsheet}Data')
                        cell_data = data_element.text if data_element is not None else ''
                        row_data.append(cell_data)
                    data.append(row_data)
        df = pd.DataFrame(data)
        df1 = df.iloc[3:len(df) - 1, 1:]
        df1 = df1.reset_index(drop=True)
        df1 = df1.replace(r'^\s*$', '0', regex=True)
        df1 = df1.astype('float', errors='ignore')
        # df1.loc['sum']=df1.apply(lambda x: x.sum())
        # df2=df1.iloc[-1,:]

        # 非求和把上面那段注释掉
        # 加一列i 加一列j
        df2 = df1
        df2.loc[:,len(df2.columns)+1] = i
        df2.loc[:,len(df2.columns)+1] = j
        # df2 = df2.values.tolist()
        #df2与finaldf合并
        finaldf = pd.concat([finaldf, df2], axis=0, ignore_index=True)
finaldf = pd.DataFrame(finaldf)
finaldf.to_csv(os.path.join(foldername, 'final.csv'), index=False, header=False, encoding='gbk')
