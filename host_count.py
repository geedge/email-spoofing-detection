import pandas as pd
import numpy as np
df=pd.read_csv('datacon_legi_from_host.csv',header=None,sep=',') #filename可以直接从盘符开始，标明每一级的文件夹直到csv文件，header=None表示头部为空，sep=','表示数据间使用逗号作为分隔符
df.columns=["from_host","mail_num"]
# print(df.tail())
print(df["from_host"].value_counts().head(10))
df["from_host"].value_counts().to_csv("datacon_legi_from_host_count.csv")