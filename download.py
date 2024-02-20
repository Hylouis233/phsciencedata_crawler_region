import urllib
import requests
import os
year_1=input("请输入起始年份：")
year_2=input("请输入终止年份：")
diseaseId=input("请输入疾病ID：")
what=input("请输入age还是region？")
# year_1=2004
# year_2=2018
# diseaseId=14
foldername = str(diseaseId)
os.makedirs(foldername, exist_ok=True)
for i in range(int(year_1),int(year_2)+1):
    for j in range(1,13):
        url_age = "https://www.phsciencedata.cn/Share/frameset?__report=ReportAgeMonth.rptdesign&__title=&__showtitle=false&__toolbar=true&__navigationbar=true&&__format=xls&__locale=zh_CN&__clean=true&__filename=%E5%8D%A0%E4%BD%8D%E7%AC%A6&years="+str(i)+"&diseaseId="+str(diseaseId)+"&months="+str(j)+"&&__dpi=96&__asattachment=true&__overwrite=false"
        url_reigon="https://www.phsciencedata.cn/Share/frameset?__report=ReportZoneMonth.rptdesign&__title=&__showtitle=false&__toolbar=true&__navigationbar=true&&__format=xls&__locale=zh_CN&__clean=true&__filename=%E5%8D%A0%E4%BD%8D%E7%AC%A6&years="+str(i)+"&diseaseId="+str(diseaseId)+"&months="+str(j)+"&&__dpi=96&__asattachment=true&__overwrite=false"
        if what=="age":
            url=url_age
        else:
            url=url_reigon
        response = requests.get(url)
        if response.status_code == 200:
            data=response.content
            filename=str(i)+"-"+str(j)+".xls"
            filepath = os.path.join(foldername, filename)
            with open(filepath, "wb") as f:
                f.write(data)
                f.close()