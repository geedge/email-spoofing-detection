import re
from parseEml import parseEml
import csv,os

def one_email_to_edges(email_path,email_num):
    node_set=set()
    edge_list = []
    mail = parseEml(email_path)
    raw_node_list = mail.get_from_host_list()
    if raw_node_list == None:
        raw_node_list=[]
    raw_node_list.append("email"+str(email_num))
    email_node="email"+str(email_num)
    node_set.add(email_node+",0")
    other_node_set=set()
    inter_node_list = []
    for node in raw_node_list:
        inter_nodes = re.findall(r'[-a-zA-Z0-9]+\.[\.\w-]+', node)
        # inter_nodes=re.findall(r'\d+(\.\d+){1,}',node)
        if len(inter_nodes) != 0:
            for inter_node in inter_nodes:
                if len(re.findall(r'[-a-zA-Z]', inter_node)):
                    domain_sets = inter_node.split(".")
                    if len(domain_sets) > 2:
                        inter_node = ".".join(domain_sets[1:])
                    node_set.add(inter_node+",1")
                    other_node_set.add(inter_node)
                else:
                    node_set.add(inter_node+",2")
                    other_node_set.add(inter_node)

    #message-id
    message_id = mail.get_message_id()
    if message_id != None:
        message_id_domain = message_id.split('@')[-1]
        message_id_domain = message_id_domain.split(">")[0]
        node_set.add(message_id_domain+",1")
        other_node_set.add(message_id_domain)

    #x-mailer
    x_mailer = mail.get_x_mailer()
    if x_mailer:
        x_mailer = x_mailer.replace("\n", "")
        x_mailer = x_mailer.replace(",", "")
    if x_mailer != None:
        node_set.add(x_mailer+",3")
        other_node_set.add(x_mailer)

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
            node_set.add(dkim_domain+",1")
            other_node_set.add(dkim_domain)
    for other_node in other_node_set:
        edge_list.append(email_node + "," + other_node)
    return node_set,edge_list

def email_batch_to_graph(email_folder,node_file,edge_file):
    node_list = set()
    with open(node_file, 'r', encoding="utf-8") as csvfile:
        nodes = csv.DictReader(csvfile)
        for node in nodes:
            node_list.add(node["name"]+","+node["type"])
    files = os.listdir(email_folder)
    email_num=2010
    for file in files:  # 遍历文件夹
        if file == "duplicate":
            continue
        nodes, edges = one_email_to_edges(email_folder + "/" + file,email_num)
        node_list.update(nodes)
        with open(edge_file, 'a+', encoding="utf-8") as edge_f:
            for edge in edges:
                edge_f.write(edge + "\n")
        email_num+=1
    with open(node_file, 'w', encoding="utf-8") as f:
        f.write("index,name,type\n")
        i = 0
        for node in node_list:
            node = str(i) + ',' +node
            f.write(node + "\n")
            i += 1

import pandas as pd
def nodes_to_index(node_file,edge_file,new_edge_file):
    nodes=pd.read_csv(node_file,encoding='utf-8')
    edge_list=[]
    with open(edge_file, 'r', encoding="utf-8") as edgefile:
        edges = csv.DictReader(edgefile)
        for edge in edges:
            node1_index=nodes[(nodes['name']==edge['node1'])].index.tolist()[0]
            node2_index = nodes[(nodes['name'] == edge['node2'])].index.tolist()[0]
            edge_list.append(str(node1_index)+","+str(node2_index))
        with open(new_edge_file, 'a+', encoding="utf-8") as f:
            for new_edge in edge_list:
                f.write(new_edge + "\n")

if __name__=="__main__":
    # email_batch_to_graph("datacon_1_legitimate","hunter_node.csv","hunter_edge.csv")
    nodes_to_index("hunter_node.csv","hunter_edge.csv","hunter_edge_index_only.csv")