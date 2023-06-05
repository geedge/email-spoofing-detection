from shutil import copyfile
from sys import exit
import os
import sys
import re

def split_datacon_eml():
    f = open("C:/Users/gisel/Desktop/datacon 2021/datacon_coremail/1_data/answer.txt")  # 返回一个文件对象
    line = f.readline()  # 调用文件的 readline()方法
    fraud_num_list=[]
    while line:
        fraud_num_list.append(line.strip())
        # print(line, end = '')# 在 Python 3 中使用
        line = f.readline()

    emails = os.listdir("C:/Users/gisel/Desktop/datacon 2021/datacon_coremail/1_data/data/")
    for email in emails:
        email_num=email.replace(".eml", "")
        if email_num not in fraud_num_list:
            continue
        source="C:/Users/gisel/Desktop/datacon 2021/datacon_coremail/1_data/data/"+email_num+".eml"
        target="C:/Users/gisel/Desktop/毕设/postPath/datacon_1_fraud/"+email_num+".eml"

        try:
            copyfile(source,target)
        except IOError as e:
            print("Unable to copy file. %s" % e)
            exit(1)
        except:
            print("Unexpected error:", sys.exc_info())
            exit(1)

        print("\nFile copy done!\n")

    f.close()

def nazario_file_to_eml(text_file,email_folder):
    f = open(text_file,'r',encoding='UTF-8',errors='ignore')  # 返回一个文件对象
    line = f.readline()  # 调用文件的 readline()方法
    num = 0
    while line:
        line_list = []
        while re.match("^From ", line) is None and line:
            line_list.append(line)
            # print(line)
            line = f.readline()
        # print(line_list)
        with open(email_folder + "/" + str(num) + ".eml", 'a+',encoding='utf-8') as f_new:
            for i in line_list:
                f_new.write(i)
        num += 1
        line = f.readline()

    f.close()

if __name__ == "__main__":
    nazario_file_to_eml("nazario_phishing_2015.txt","nazario_phishing_2015")