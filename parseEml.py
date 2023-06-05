#-*- encoding: gb2312 -*-
import email
import os
import re
import csv
import json

# def sort_key(received_header):
#     received_date = email.utils.parsedate_tz(received_header)
#     return received_date

class parseEml:

    def __init__(self, email_path):
        self.email_path=email_path
        self.msg=self.get_message()

    # 读取文件
    def read_mail(self):
        if os.path.exists(self.email_path):
            with open(self.email_path) as fp:
                for line in fp:
                    print(line)
        else:
            print('文件不存在!')

    # 创建消息对象
    def get_message(self):
        if os.path.exists(self.email_path):
            fp = open(self.email_path, 'r', encoding='UTF-8',errors='ignore')
            # print(self.email_path)
            return email.message_from_file(fp)
        else:
            print('文件不存在!')

        # 获取邮件的Received
    def get_received(self):
        if self.msg != None:
            received_array=self.msg.get_all('Received')
            return received_array
        else:
            print('msg is empty!')

    def get_message_id(self):
        if self.msg != None:
            return self.msg.get('Message-ID')
        else:
            print('msg is empty!')

    def get_from(self):
        if self.msg != None:
            return self.msg.get('From')
        else:
            print('msg is empty!')

    def get_to(self):
        if self.msg != None:
            return self.msg.get('To')
        else:
            print('msg is empty!')

    def get_x_mailer(self):
        if self.msg != None:
            return self.msg.get('X-Mailer')
        else:
            print('msg is empty!')

    def get_from_host_list(self):
        if self.msg != None:
            from_host_list=[]
            received_array=self.msg.get_all('Received')
            if received_array == None:
                return None
            for received in received_array:
                received = re.sub(r'\n\s*', " ", received)
                # print(received)
                if "from" in received and "by" in received:
                    from_host = received[received.find("from") + 5:received.find("by")].strip()
                    from_host_list.append(from_host)
                    # print(from_host)
            return from_host_list
        else:
            print('msg is empty!')

    def get_dkim(self):
        if self.msg != None:
            return self.msg.get('DKIM-Signature')
        else:
            print('msg is empty!')

    def get_auth_results(self):
        if self.msg != None:
            return self.msg.get('Authentication-Results')
        else:
            print('msg is empty!')

def list_to_file(alist,file_name):
    with open(file_name, 'a+') as f:
        for i in alist:
            f.write(i + '\n')

def list_to_csv(alist,file_name,file_num):
    with open(file_name, 'a+', newline='') as f:
        writer = csv.writer(f)
        for i in alist:
            writer.writerow([i,file_num])

def extract_from_host(folder_path,file_name):
    from_host_list=[]
    files = os.listdir(folder_path)  # 得到文件夹下的所有文件名称
    for file in files:  # 遍历文件夹
        received_array = parseEml(folder_path+"/"+ file).get_received()
        for received in received_array:
            received = re.sub(r'\n\s*', " ", received)
            # print(received)
            if "from" in received and "by" in received:
                from_host = received[received.find("from") + 5:received.find("by")].strip()
                # if from_host=="":
                #     print(received)
                from_host_list.append(from_host)
                # print(from_host)
    list_to_file(from_host_list,file_name)

def extract_message_id(folder_path,file_name):
    files = os.listdir(folder_path)  # 得到文件夹下的所有文件名称
    record_list=[]
    for file in files:  # 遍历文件夹
        if file == "duplicate":
            continue
        file_num = file.replace(".eml", "")
        mail=parseEml(folder_path+"/"+ file)
        message_id=mail.get_message_id()
        sender=mail.get_from()
        receiver=mail.get_to()
        record={"Message-ID":message_id,"From":sender,"To":receiver,"num:":file_num}
        record_list.append(record)
    with open(file_name, 'a+', newline='',encoding='utf-8') as f:
        json.dump(record_list,f)

def extract_x_mailer(folder_path,file_name):
    files = os.listdir(folder_path)  # 得到文件夹下的所有文件名称
    record_list = []
    for file in files:  # 遍历文件夹
        if file == "duplicate":
            continue
        file_num = file.replace(".eml", "")
        mail = parseEml(folder_path + "/" + file)
        x_mailer=mail.get_x_mailer()
        if x_mailer != None:
            message_id=mail.get_message_id()
            sender = mail.get_from()
            receiver = mail.get_to()
            record = {"Message-ID":message_id,"X-Mailer": x_mailer, "From": sender, "To": receiver, "num:": file_num}
            record_list.append(record)
    with open(file_name, 'a+', newline='', encoding='utf-8') as f:
        json.dump(record_list, f)

def extract_received_x_mailer(folder_path,file_name):
    files=os.listdir(folder_path)
    for file in files:  # 遍历文件夹
        record = ""
        if file == "duplicate":
            continue
        file_num = file.replace(".eml", "")
        mail = parseEml(folder_path + "/" + file)
        received_array=mail.get_received()
        x_mailer = mail.get_x_mailer()
        for received in received_array:
            received = re.sub(r'\n\s*', " ", received)
            received=received[:received.find(";")]
            record+="Received: "+received+"; "
        if x_mailer != None:
            record+="X-Mailer: "+x_mailer
        with open(file_name, 'a+', newline='', encoding='utf-8') as f:
            f.writelines(record)
            f.writelines("\n")

def to_count(folder_path):
    files=os.listdir(folder_path)
    receiver_list=[]
    for file in files:  # 遍历文件夹
        if file == "duplicate":
            continue
        mail=parseEml(folder_path + "/" + file)
        receiver=mail.get_to()
        receiver_list.append(receiver)
    dict = {}
    for key in receiver_list:
        dict[key] = dict.get(key, 0) + 1
    print(dict)
    print(max(set(receiver_list), key=receiver_list.count))

def extract_to(folder_path,file_name):
    files = os.listdir(folder_path)
    receiver_list = []
    for file in files:  # 遍历文件夹
        if file == "duplicate":
            continue
        mail = parseEml(folder_path + "/" + file)
        receiver = mail.get_to()
        if receiver != None:
            receiver_list.append(receiver)
    list_to_file(receiver_list,file_name)

def read_template(template_file):
    f = open(template_file)  # 返回一个文件对象
    line = f.readline()  # 调用文件的 readline()方法
    line_list = []
    while line:
        line1 = line.strip()
        if line1:
            line_list.append(line1)
        line = f.readline()
    f.close()
    return line_list

def extract_edge(email_path,template_list):
    mail=parseEml(email_path)
    received_array = mail.get_received()
    receiver=mail.get_to()
    if receiver:
        receiver=receiver.replace("\"","\\\"")
    else:
        receiver=""
    # print(received_array)
    edge_list = []
    from_host_list=[]
    for received in received_array:
        received = re.sub(r'\n\s*', " ", received)
        # print(received)
        if "from" in received and "by" in received:
            from_host = received[received.find("from") + 5:received.find("by")].strip()
            for template in template_list:
                if "<:*:>" in template:
                    template = template.replace("<:*:>", ".*")
                if "(" in template:
                    template = template.replace("(", "\(")
                if ")" in template:
                    template=template.replace(")","\)")
                if "[" in template:
                    template=template.replace("[","\[")
                if re.match(template, from_host):
                    from_host=template
                    break
            from_host=from_host.replace("\"","\\\"")
            from_host_list.append(from_host)
            # print(from_host)
    num=len(from_host_list)
    if num > 0:
        last_received=received_array[0]
        last_node=last_received[last_received.find("by")+3:last_received.find("with")].strip()
        edge_list.append("\""+last_node+"\" -> \""+receiver+"\"")
        edge_list.append("\""+from_host_list[0]+"\" -> \""+last_node+"\"")
        if num >=2:
            for i in range(0,num-2):
                edge_list.append("\""+from_host_list[i+1]+"\" -> \""+from_host_list[i]+"\"")
    return edge_list

def extract_path(email_path,email_num):
    mail = parseEml(email_path)
    received_array = mail.get_received()
    sender=mail.get_from()
    receiver = mail.get_to()
    from_host_list = []
    path=""
    for received in received_array:
        received = re.sub(r'\n\s*', " ", received)
        # print(received)
        if "from" in received and "by" in received:
            from_host = received[received.find("from") + 5:received.find("by")].strip()
            from_host_list.append(from_host)
            # print(from_host)
    num = len(from_host_list)
    if num > 0:
        last_received = received_array[0]
        last_node = last_received[last_received.find("by") + 3:last_received.find("with")].strip()
        if receiver:
            path= last_node + "," + receiver
        else:
            path=last_node+","
        path= from_host_list[0] + " -> " + path
        if num >= 2:
            for i in range(1, num):
                path=from_host_list[i] + " -> " + path
    path=sender+","+path
    path=email_num+ ","+ path
    return path

def extract_all_edges(email_folder,template_path,file_name):
    template_list = read_template(template_path)
    files = os.listdir(email_folder)
    for file in files:  # 遍历文件夹
        if file == "duplicate":
            continue
        mail_path = extract_edge(email_folder + "/" + file,template_list)
        with open(file_name, 'a+') as f:
            for i in mail_path:
                f.write(i + ' [color=red];\n')

def extract_all_paths(email_folder,file_name):
    with open(file_name, 'a+') as f:
        f.write('email_num,from,path,receiver\n')
    files = os.listdir(email_folder)
    for file in files:  # 遍历文件夹
        if file == "duplicate":
            continue
        mail_path = extract_path(email_folder + "/" + file,file.replace(".eml", ""))
        with open(file_name, 'a+') as f:
            f.write(mail_path + '\n')

def delete_once_node(edge_file):
    f = open(edge_file)  # 返回一个文件对象
    line = f.readline()  # 调用文件的 readline()方法
    line_list = []
    while line:
        line1 = line.strip()
        if line1:
            line_list.append(line1)
        line = f.readline()
    f.close()
    return line_list

if __name__=="__main__":
    extract_all_paths("nazario_phishing_2021","nazario_paths.csv")