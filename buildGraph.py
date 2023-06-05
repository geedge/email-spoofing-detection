from parseEml import parseEml
import os
import re
from shutil import copyfile

def extract_node_edge(email_path):
    # 节点类型：0：sender domain；1：inter domain；2：IP；3：client
    # 边类型：0：sender domain-inter domain；1：inter domain-IP或者IP-inter domain;
    # 边类型：2:sender domain-message id domain; 3:sender domain-x_mailer; 4:sender domain-dkim domain
    # inter_node_list[每跳域名、IP为一个set]
    node_list=set()
    edge_list=[]
    mail=parseEml(email_path)
    raw_node_list=mail.get_from_host_list()
    raw_node_list.insert(0,mail.get_from())
    # print(raw_node_list)
    inter_node_list=[]
    sender_domain=None
    for node in raw_node_list:
        if '@' in node:
            node=node.split('@')[-1]
            if '>' in node:
                node=node.split(">")[0]
            if ')' in node:
                node = node.split(")")[0]
            if ',' in node:
                node=node.replace(","," ")
            sender_domain=node
            # if "kennadi" in sender_domain:
            #     print(email_path)
            node_list.add(node+",0")
        else:
            inter_domain_ip=set()
            inter_nodes=re.findall(r'[-a-zA-Z0-9]+\.[\.\w-]+',node)
            # inter_nodes=re.findall(r'\d+(\.\d+){1,}',node)
            if len(inter_nodes)!=0:
                for inter_node in inter_nodes:
                    if len(re.findall(r'[-a-zA-Z]',inter_node)):
                        domain_sets = inter_node.split(".")
                        if len(domain_sets) > 2:
                            inter_node = ".".join(domain_sets[1:])
                        if sender_domain:
                            edge_list.append(sender_domain+","+inter_node+",0")#发件域到中间域的边
                        inter_domain_ip.add(inter_node)
                        node_list.add(inter_node + ",1")
                    else:
                        inter_domain_ip.add(inter_node)
                        node_list.add(inter_node+",2")
            if len(inter_domain_ip):
                inter_node_list.append(inter_domain_ip)
    # print(node_list)
    print(sender_domain)
    print(inter_node_list)
    for domain_ip_set in inter_node_list:
        if len(domain_ip_set) > 1:
            domain_ip_list=list(domain_ip_set)
            for i in range(0,len(domain_ip_list)-1):
                for j in range(i+1,len(domain_ip_list)):
                    edge_list.append(domain_ip_list[i]+","+domain_ip_list[j]+",1")
    print(edge_list)
    return node_list,edge_list

def extract_sender_and_received(email_folder,node_file,edge_file):
    with open(node_file, 'a+') as f:
        f.write('index,name,type\n')
    with open(edge_file,'a+') as edge_f:
        edge_f.write('node1,node2,type\n')
    node_list=set()
    files = os.listdir(email_folder)
    for file in files:  # 遍历文件夹
        if file == "duplicate":
            continue
        nodes,edges=extract_node_edge(email_folder + "/" + file)
        node_list.update(nodes)
        with open(edge_file,'a+') as edge_f:
            for edge in edges:
                edge_f.write(edge+"\n")
    with open(node_file, 'a+',encoding="utf-8") as f:
        i=0
        for node in node_list:
            node=str(i)+','+node
            f.write(node+"\n")
            i+=1

def extract_domain_from_address(fromname):
    sender_domain=None
    if '@' in fromname:
        sender_domain = fromname.split('@')[-1]
        if '>' in sender_domain:
            sender_domain = sender_domain.split(">")[0]
        if ')' in sender_domain:
            sender_domain = sender_domain.split(")")[0]
        if ',' in sender_domain:
            sender_domain = sender_domain.replace(",", " ")
    return sender_domain

def add_message_id_edge(email_folder,edge_file):
    files = os.listdir(email_folder)
    for file in files:  # 遍历文件夹
        if file == "duplicate":
            continue
        mail = parseEml(email_folder+"/"+file)
        fromname = mail.get_from()
        message_id=mail.get_message_id()
        if '@' in fromname:
            sender_domain = fromname.split('@')[-1]
            if '>' in sender_domain:
                sender_domain = sender_domain.split(">")[0]
            if ')' in sender_domain:
                sender_domain = sender_domain.split(")")[0]
        if message_id != None:
            message_id_domain=message_id.split('@')[-1]
            message_id_domain=message_id_domain.split(">")[0]
            if sender_domain != message_id_domain and sender_domain:
                with open(edge_file, 'a+',encoding='utf-8') as edge_f:
                    edge_f.write(sender_domain+","+message_id_domain+",2\n")

def add_x_mailer_edge(email_folder,edge_file):
    files = os.listdir(email_folder)
    for file in files:  # 遍历文件夹
        if file == "duplicate":
            continue
        mail = parseEml(email_folder+"/"+file)
        fromname = mail.get_from()
        x_mailer=mail.get_x_mailer()
        if x_mailer:
            x_mailer=x_mailer.replace("\n","")
            x_mailer=x_mailer.replace(",","")
        if '@' in fromname:
            sender_domain = fromname.split('@')[-1]
            if '>' in sender_domain:
                sender_domain = sender_domain.split(">")[0]
            if ')' in sender_domain:
                sender_domain = sender_domain.split(")")[0]
        if x_mailer != None and sender_domain:
            with open(edge_file, 'a+',encoding="utf-8") as edge_f:
                edge_f.write(sender_domain+","+x_mailer+",3\n")

def add_dkim_edge(email_folder,edge_file):
    files = os.listdir(email_folder)
    for file in files:  # 遍历文件夹
        if file == "duplicate":
            continue
        mail = parseEml(email_folder+"/"+file)
        fromname = mail.get_from()
        dkim_signature=mail.get_dkim()
        if dkim_signature:
            dkim_signature=dkim_signature.replace("\n\t","")
            dkim_domains=re.findall(r'd=(.+?);',dkim_signature)
            if len(dkim_domains)==0:
                # dkim_domain=dkim_domains[0]
                print(dkim_signature)
            else:
                dkim_domain=dkim_domains[0]
                if '@' in fromname:
                    sender_domain = fromname.split('@')[-1]
                    if '>' in sender_domain:
                        sender_domain = sender_domain.split(">")[0]
                    if ')' in sender_domain:
                        sender_domain = sender_domain.split(")")[0]
                if sender_domain and sender_domain != dkim_domain:
                    with open(edge_file, 'a+', encoding="utf-8") as edge_f:
                        edge_f.write(sender_domain + "," + dkim_domain + ",4\n")


import csv
def add_nodes(node_file,edge_file,new_node_file):
    nodes_set=set()
    # 逐行读取csv文件
    with open(node_file, 'r', encoding="utf-8") as csvfile:
        nodes = csv.DictReader(csvfile)
        for node in nodes:
            nodes_set.add(node["name"]+","+node["type"])
    with open(edge_file, 'r', encoding="utf-8") as edgefile:
        edges=csv.DictReader(edgefile)
        for edge in edges:
            if edge["type"]=='2' or edge["type"]=='4':
                nodes_set.add(edge["node2"]+","+str(1))
            else:
                nodes_set.add(edge["node2"]+","+str(3))
    with open(new_node_file, 'a+',encoding="utf-8") as f:
        f.write('index,name,type\n')
        i = 0
        for new_node in nodes_set:
            new_node = str(i) + ',' + new_node
            f.write(new_node + "\n")
            i += 1

def is_ip(str):
    domain_and_ip=re.findall(r'[-a-zA-Z0-9]+\.[\.\w-]+',str)
    domain=re.findall(r'[-a-zA-Z-]',str)
    if len(domain_and_ip) and (len(domain)==0):
        nums=str.split(".")
        if len(nums)==4:
            return True
    return False

import pandas as pd
def nodes_to_index(node_file,edge_file,new_edge_file):
    nodes=pd.read_csv(node_file,encoding='utf-8')
    edge_list=[]
    with open(edge_file, 'r', encoding="utf-8") as edgefile:
        edges = csv.DictReader(edgefile)
        for edge in edges:
            if edge['type']=='0':
                print("hi:"+edge['node1'])
                node1_index=nodes[(nodes['name']==edge['node1']) & (nodes['type']==0)].index.tolist()[0]
                node2_index=nodes[(nodes['name']==edge['node2']) & (nodes['type']==1)].index.tolist()[0]
            elif edge['type']=='1':#注意区分域名和IP
                if is_ip(edge['node1']):
                    node1_index=nodes[(nodes['name']==edge['node1']) & (nodes['type']==2)].index.tolist()[0]
                else:
                    print(edge["node1"])
                    node1_index=nodes[(nodes['name']==edge['node1']) & (nodes['type']==1)].index.tolist()[0]
                if is_ip(edge['node2']):
                    print(edge["node2"])
                    node2_index=nodes[(nodes['name']==edge['node2']) & (nodes['type']==2)].index.tolist()[0]
                else:
                    node2_index=nodes[(nodes['name']==edge['node2']) & (nodes['type']==1)].index.tolist()[0]
            elif edge['type']=='2' or edge['type'] == '4':
                node1_index = nodes[(nodes['name'] == edge['node1']) & (nodes['type'] == 0)].index.tolist()[0]
                node2_index = nodes[(nodes['name'] == edge['node2']) & (nodes['type'] == 1)].index.tolist()[0]
            elif edge['type']=='3':
                node1_index = nodes[(nodes['name'] == edge['node1']) & (nodes['type'] == 0)].index.tolist()[0]
                node2_index = nodes[(nodes['name'] == edge['node2']) & (nodes['type'] == 3)].index.tolist()[0]
            edge_list.append(str(node1_index)+","+str(node2_index)+","+str(edge['type']))
        with open(new_edge_file, 'a+', encoding="utf-8") as f:
            for new_edge in edge_list:
                f.write(new_edge + "\n")

def nodes_to_index_mes_id(node_file,edge_file,new_edge_file):
    nodes=pd.read_csv(node_file,encoding='utf-8')
    edge_list=[]
    with open(edge_file, 'r', encoding="utf-8") as edgefile:
        edges = csv.DictReader(edgefile)
        for edge in edges:
            print(edge["node1"])
            node1_index=nodes[(nodes['name']==edge['node1']) & (nodes['type']==0)].index.tolist()[0]
            if edge['type']=='2' or edge['type'] == '4':
                node2_index=nodes[(nodes['name']==edge['node2']) & (nodes['type']==1)].index.tolist()[0]
            elif edge['type']=='3':
                node2_index = nodes[(nodes['name'] == edge['node2']) & (nodes['type'] == 3)].index.tolist()[0]
            edge_list.append(str(node1_index)+","+str(node2_index)+","+str(edge['type']))
        with open(new_edge_file, 'w', encoding="utf-8") as f:
            for new_edge in edge_list:
                f.write(new_edge + "\n")

# 使用 graphviz创建元图.
# import pygraphviz as pgv
import json
def plot_graph(node_file,edge_file_fraud,edge_file_legi):
    ag = pgv.AGraph(strict=False, directed=False,rankdir="LR")
    with open(edge_file_fraud, 'r', encoding="utf-8") as edgefile_fraud:
        reader=csv.reader(edgefile_fraud)
        edges_fraud=[" ".join(row) for row in reader]
        edge_count_fraud=pd.value_counts(edges_fraud).to_dict()
    with open(edge_file_legi, 'r', encoding="utf-8") as edgefile_legi:
        reader1=csv.reader(edgefile_legi)
        edges_legi=[" ".join(row) for row in reader1]
        edge_count_legi=pd.value_counts(edges_legi).to_dict()
    with open(node_file, 'r', encoding="utf-8") as nodefile:
        nodes = csv.DictReader(nodefile)
        for node in nodes:
            if node["type"] == '0':
                ag.add_node(node["index"], label=node["name"], shape="box", color="blue")
                # ag.add_node(node["index"], shape="box",color="blue")
                # ag.add_node(node["index"], shape="point", color="blue")
            elif node["type"] == '1':
                ag.add_node(node["index"], label=node["name"], shape="ellipse")
                # ag.add_node(node["index"], shape="ellipse")
                # ag.add_node(node["index"], shape="point",color="green")
            elif node["type"] == '2':
                ag.add_node(node["index"], shape="point")
            else:
                ag.add_node(node["index"], label=node["name"], shape="diamond")
                # ag.add_node(node["index"], shape="diamond")
                # ag.add_node(node["index"], shape="point", color="purple")
    for key in edge_count_fraud:
        edge_param=key.split(" ")
        ag.add_edge(edge_param[0],edge_param[1],label=edge_count_fraud[key],color="red")
    for key in edge_count_legi:
        edge_param=key.split(" ")
        ag.add_edge(edge_param[0], edge_param[1], label=edge_count_legi[key])
    ag.layout('dot')
    ag.draw('graph_dot.svg')

def select_legi_emails(email_folder):
    files = os.listdir(email_folder)
    i=0
    for file in files:  # 遍历文件夹
        if i<2483:
            copyfile(email_folder + "/" + file,"datacon_1_legi_train/"+file)
        if i>=2483 and i < 3725:
            copyfile(email_folder + "/" + file,"datacon_1_legi_val/"+file)
        if i>=3725:
            copyfile(email_folder + "/" + file,"datacon_1_legi_test/"+file)
        i += 1

def merge_node(node_file1,node_file2,new_node_file):
    #合并两个node文件，统一索引
    nodes_set = set()
    # 逐行读取csv文件
    with open(node_file1, 'r', encoding="utf-8") as csvfile:
        nodes = csv.DictReader(csvfile)
        for node in nodes:
            nodes_set.add(node["name"] + "," + node["type"])
    with open(node_file2, 'r', encoding="utf-8") as nodefile2:
        nodes2 = csv.DictReader(nodefile2)
        for node2 in nodes2:
            nodes_set.add(node2["name"] + "," + node2["type"])
    with open(new_node_file, 'a+', encoding="utf-8") as f:
        f.write('index,name,type\n')
        i = 0
        for new_node in nodes_set:
            new_node = str(i) + ',' + new_node
            f.write(new_node + "\n")
            i += 1

import json

def _str2tuple(key):
    # 注意python切片 左开右闭 的性质
	fore = int(key[1:2])
	back = key[5: -2]
	return tuple([fore, back])


def one_email_to_graph(email_path,node_file,edge_file):
    with open(node_file, 'r',encoding='UTF-8') as node_f:
        node_dict = json.load(node_f)
        node_dict = json.loads(node_dict)
        node_dict = {_str2tuple(k): node_dict[k] for k in node_dict}
    edge_list = []
    mail = parseEml(email_path)
    raw_node_list = mail.get_from_host_list()
    raw_node_list.insert(0, mail.get_from())
    # print(raw_node_list)
    inter_node_list = []
    sender_domain = None
    for node in raw_node_list:
        if '@' in node:
            node = node.split('@')[-1]
            if '>' in node:
                node = node.split(">")[0]
            if ')' in node:
                node = node.split(")")[0]
            if ',' in node:
                node = node.replace(",", " ")
            sender_domain = node
            if "monkey.org\n" in sender_domain:
                print(email_path)
            if (0,node) not in node_dict:
                node_dict[(0,node)]=len(node_dict)
        else:
            inter_domain_ip = set()
            inter_nodes = re.findall(r'[-a-zA-Z0-9]+\.[\.\w-]+', node)
            # inter_nodes=re.findall(r'\d+(\.\d+){1,}',node)
            if len(inter_nodes) != 0:
                for inter_node in inter_nodes:
                    if len(re.findall(r'[-a-zA-Z]', inter_node)):
                        domain_sets = inter_node.split(".")
                        if len(domain_sets) > 2:
                            inter_node = ".".join(domain_sets[1:])
                        if (1, inter_node) not in node_dict:
                            node_dict[(1, inter_node)] = len(node_dict)
                        if sender_domain:
                            edge_list.append(str(node_dict[(0,sender_domain)]) + "," + str(node_dict[(1,inter_node)]) + ",0")  # 发件域到中间域的边
                        inter_domain_ip.add((1,inter_node))
                    else:
                        inter_domain_ip.add((2,inter_node))
                        if (2, inter_node) not in node_dict:
                            node_dict[(2, inter_node)] = len(node_dict)
            if len(inter_domain_ip):
                inter_node_list.append(inter_domain_ip)
    # print(node_list)
    # print(sender_domain)
    # print(inter_node_list)
    for domain_ip_set in inter_node_list:
        if len(domain_ip_set) > 1:
            domain_ip_list = list(domain_ip_set)
            for i in range(0, len(domain_ip_list) - 1):
                for j in range(i + 1, len(domain_ip_list)):
                    edge_list.append(str(node_dict[domain_ip_list[i]]) + "," + str(node_dict[domain_ip_list[j]]) + ",1")
    print(edge_list)

    #message-id
    message_id = mail.get_message_id()
    if message_id != None:
        message_id_domain = message_id.split('@')[-1]
        message_id_domain = message_id_domain.split(">")[0]
        if sender_domain != message_id_domain and sender_domain:
            if (1,message_id_domain ) not in node_dict:
                node_dict[(1, message_id_domain)] = len(node_dict)
            edge_list.append(str(node_dict[(0,sender_domain)]) + "," + str(node_dict[(1,message_id_domain)]) + ",2")

    #x-mailer
    x_mailer = mail.get_x_mailer()
    if x_mailer:
        x_mailer = x_mailer.replace("\n", "")
        x_mailer = x_mailer.replace(",", "")
    if x_mailer != None and sender_domain:
        if (3, x_mailer) not in node_dict:
            node_dict[(3, x_mailer)] = len(node_dict)
        edge_list.append(str(node_dict[(0, sender_domain)]) + "," + str(node_dict[(3, x_mailer)]) + ",3")

    #dkim-domain
    dkim_signature = mail.get_dkim()
    if dkim_signature:
        dkim_signature = dkim_signature.replace("\n\t", "")
        dkim_domains = re.findall(r'd=(.+?);', dkim_signature)
        if len(dkim_domains) == 0:
            # dkim_domain=dkim_domains[0]
            print(dkim_signature)
        else:
            dkim_domain = dkim_domains[0]
            if sender_domain and sender_domain != dkim_domain:
                if (1, dkim_domain) not in node_dict:
                    node_dict[(1, dkim_domain)] = len(node_dict)
                edge_list.append(str(node_dict[(0, sender_domain)]) + "," + str(node_dict[(1, dkim_domain)]) + ",4")

    with open(node_file, 'w', encoding="utf-8") as f:
        node_dict=json.dumps({str(k):node_dict[k] for k in node_dict})
        json.dump(node_dict,f)
    with open(edge_file,'a+',encoding="utf-8") as edge_f:
        for edge in edge_list:
            edge_f.writelines(edge)
            edge_f.writelines("\n")

def email_batch_to_graph(email_folder,node_file,edge_file):
    node_list = set()
    with open(node_file, 'r', encoding="utf-8") as csvfile:
        nodes = csv.DictReader(csvfile)
        for node in nodes:
            node_list.add(node["name"]+","+node["type"])
    files = os.listdir(email_folder)
    for file in files:  # 遍历文件夹
        if file == "duplicate":
            continue
        nodes, edges = one_email_to_edges(email_folder + "/" + file)
        node_list.update(nodes)
        with open(edge_file, 'a+', encoding="utf-8") as edge_f:
            for edge in edges:
                edge_f.write(edge + "\n")
    with open(node_file, 'w', encoding="utf-8") as f:
        f.write("index,name,type\n")
        i = 0
        for node in node_list:
            node = str(i) + ',' +node
            f.write(node + "\n")
            i += 1

def one_email_to_edges(email_path):
    node_set=set()
    edge_list = []
    mail = parseEml(email_path)
    raw_node_list = mail.get_from_host_list()
    if raw_node_list == None:
        raw_node_list=[]
    if mail.get_from() != None:
        # print(mail.get_from())
        raw_node_list.insert(0, mail.get_from())
    # print(raw_node_list)
    inter_node_list = []
    sender_domain = None
    for node in raw_node_list:
        if '@' in node:
            node = node.split('@')[-1]
            if '>' in node:
                node = node.split(">")[0]
            if ')' in node:
                node = node.split(")")[0]
            if ',' in node:
                node = node.replace(",", " ")
            if '\n' in node:
                node = node.replace("\n"," ")
            sender_domain = node
            # if "\n" in sender_domain:
            #     print(email_path)
            node_set.add(node+",0")
        else:
            inter_domain_ip = set()
            inter_nodes = re.findall(r'[-a-zA-Z0-9]+\.[\.\w-]+', node)
            # inter_nodes=re.findall(r'\d+(\.\d+){1,}',node)
            if len(inter_nodes) != 0:
                for inter_node in inter_nodes:
                    if len(re.findall(r'[-a-zA-Z]', inter_node)):
                        domain_sets = inter_node.split(".")
                        if len(domain_sets) > 2:
                            inter_node = ".".join(domain_sets[1:])
                        node_set.add(inter_node+",1")
                        if sender_domain:
                            edge_list.append(sender_domain + "," + inter_node + ",0")  # 发件域到中间域的边
                        inter_domain_ip.add((1,inter_node))
                    else:
                        inter_domain_ip.add((2,inter_node))
                        node_set.add(inter_node+",2")
            if len(inter_domain_ip):
                inter_node_list.append(inter_domain_ip)
    # print(node_list)
    # print(sender_domain)
    # print(inter_node_list)
    for domain_ip_set in inter_node_list:
        if len(domain_ip_set) > 1:
            domain_ip_list = list(domain_ip_set)
            for i in range(0, len(domain_ip_list) - 1):
                for j in range(i + 1, len(domain_ip_list)):
                    edge_list.append(domain_ip_list[i][1] + "," + domain_ip_list[j][1] + ",1")
    # print(edge_list)

    #message-id
    message_id = mail.get_message_id()
    if message_id != None:
        message_id_domain = message_id.split('@')[-1]
        message_id_domain = message_id_domain.split(">")[0]
        if sender_domain != message_id_domain and sender_domain:
            node_set.add(message_id_domain+",1")
            edge_list.append(sender_domain + "," + message_id_domain + ",2")

    #x-mailer
    x_mailer = mail.get_x_mailer()
    if x_mailer:
        x_mailer = x_mailer.replace("\n", "")
        x_mailer = x_mailer.replace(",", "")
    if x_mailer != None and sender_domain:
        node_set.add(x_mailer+",3")
        edge_list.append(sender_domain + "," + x_mailer + ",3")

    #dkim-domain
    dkim_signature = mail.get_dkim()
    if dkim_signature:
        dkim_signature = dkim_signature.replace("\n\t", "")
        dkim_domains = re.findall(r'd=(.+?);', dkim_signature)
        if len(dkim_domains) == 0:
            # dkim_domain=dkim_domains[0]
            print(dkim_signature)
        else:
            dkim_domain = dkim_domains[0]
            if sender_domain and sender_domain != dkim_domain:
                node_set.add(dkim_domain+",1")
                edge_list.append(sender_domain + "," + dkim_domain + ",4")
    return node_set,edge_list

def split_training_nodes(node_file,edge_file):
    node_dataframe_all=pd.read_csv(node_file,encoding="utf-8")
    edge_dataframe_all=pd.read_csv(edge_file,encoding="utf-8")
    nodes_list=edge_dataframe_all["node1"].tolist()
    nodes_list+=edge_dataframe_all["node2"].tolist()
    nodes_set=set(nodes_list)
    print(len(nodes_set))
    training_nodes=node_dataframe_all[node_dataframe_all["index"].isin(nodes_list)]
    # training_nodes.to_csv("training_nodes.csv",index=False)

def add_testing_nodes(node_file1,node_file2,added_nodes_file):
    nodes_set = set()
    new_node_dict={}
    # 逐行读取csv文件
    with open(node_file1, 'r', encoding="utf-8") as nodefile1:
        nodes = csv.DictReader(nodefile1)
        for node in nodes:
            training_node=node["name"] + "," + node["type"]
            # if training_node in nodes_set:
            #     print(training_node)
            nodes_set.add(training_node)
    with open(node_file2, 'r', encoding="utf-8") as nodefile2:
        nodes2 = csv.DictReader(nodefile2)
        for node2 in nodes2:
            test_node=node2["name"]+","+node2["type"]
            if test_node in nodes_set:
                continue
            new_node_dict[len(nodes_set)]=test_node
            nodes_set.add(test_node)
    with open(added_nodes_file, 'w', encoding="utf-8") as f:
        f.write("index,name,type\n")
        for key in new_node_dict:
            node = str(key) + ',' +new_node_dict[key]
            f.write(node + "\n")

if __name__ == "__main__":
    # select_legi_emails("datacon_1_legitimate")
    # extract_sender_and_received("datacon_1_fraud","datacon_fraud_graph/nodes.csv","datacon_fraud_graph/edges.csv")
    # add_message_id_edge("datacon_1_fraud","datacon_fraud_graph/edges_other.csv")
    # add_x_mailer_edge("datacon_1_fraud","datacon_fraud_graph/edges_other.csv")
    # add_dkim_edge("datacon_1_fraud","datacon_fraud_graph/edges_other.csv")
    # add_nodes("datacon_fraud_graph/nodes.csv","datacon_fraud_graph/edges_other.csv","datacon_fraud_graph/nodes_all.csv")
    # merge_node("datacon_legitimate_graph/nodes_all.csv","all_nodes.csv","all_nodes1.csv")
    # nodes_to_index("all_nodes.csv","legi_edges_testing.csv","legi_edges_testing_index_only.csv")
    # nodes_to_index_mes_id("all_nodes.csv","datacon_legitimate_graph/edges_other.csv","datacon_legitimate_graph/edges_index_only.csv")
    # plot_graph("all_nodes.csv","fraud_edges_index_only.csv","datacon_legitimate_graph/legi_edges_index_only.csv")
    # one_email_to_graph("nazario_phishing_2020/2.eml","all_nodes.json","all_edges.csv")
    email_batch_to_graph("benign_emails","all_nodes1.csv","benign_edges.csv")
    # split_training_nodes("all_nodes.csv","edges_training_index_only.csv")
    # add_testing_nodes("training_nodes1.csv","testing_nodes.csv","indexed_testing_nodes.csv")