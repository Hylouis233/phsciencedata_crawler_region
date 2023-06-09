import pandas as pd
import os
import xml.etree.ElementTree as ET
import xmltodict
import re
import csv
diseaseId=int(input("请输入疾病ID："))
foldername = str(diseaseId)
os.makedirs(foldername, exist_ok=True)
finaldf = pd.read_csv("D:/github/phsciencedata_crawler/final.csv",encoding='gbk')
df=finaldf
df_year = pd.DataFrame()
a="年龄分组"
# a="地区"
what=str(a)
for region in df[what].unique():
    # 筛选出该地区的数据
    df_region = df[df[what] == region]
    # 对每年进行循环
    for year in df_region["年份"].unique():
        # 筛选出该年的数据
        df_year_region = df_region[df_region["年份"] == year]
        # 计算该年的发病数和死亡数的总和
        sum_cases = df_year_region["发病数"].sum()
        sum_deaths = df_year_region["死亡数"].sum()
        # 计算该年的发病率和死亡率的平均值
        mean_incidence = df_year_region["发病率(1/10万)"].mean()
        mean_mortality = df_year_region["死亡率(1/10万)"].mean()
        # 创建一个新的数据行，包含该地区该年的数据
        new_row = {what: region, "发病数": sum_cases, "死亡数": sum_deaths, "发病率(1/10万)": mean_incidence, "死亡率(1/10万)": mean_mortality, "年份": year}
        # 将新的数据行添加到每年的数据框中
        df_year = df_year.append(new_row, ignore_index=True)
df_year.to_csv(what+'_year_final.csv', index=True, header=True, encoding='gbk')
