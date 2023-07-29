from buildGraph import one_email_to_edges,is_ip
import csv
import os
import pandas as pd

def nodes_to_index(node_file,edge_file,new_edge_file):
    print(str(new_edge_file))
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
                    print(edge['node1'])
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
            edge_list.append(str(node1_index)+"\t"+str(node2_index))
        with open(new_edge_file, 'w', encoding="utf-8") as f:
            for new_edge in edge_list:
                f.writelines(new_edge + "\n")

def email_batch_to_subgraph(email_folder,node_file,graph_folder):
    # node_dict = {}
    # with open(node_file, 'r', encoding="utf-8") as csvfile:
    #     nodes = csv.DictReader(csvfile)
    #     for node in nodes:
    #         node_dict[node["name"]+","+node["type"]]=node["index"]
    files = os.listdir(email_folder)
    for file in files:  # 遍历文件夹
        if file == "duplicate":
            continue
        nodes, edges = one_email_to_edges(email_folder + "/" + file)
        with open(graph_folder+"/"+email_folder+"_"+file.replace(".eml",'')+".csv", 'w', encoding="utf-8") as edge_f:
            edge_f.write("node1,node2,type\n")
            for edge in edges:
                edge_f.write(edge + "\n")
        nodes_to_index(node_file,graph_folder+"/"+email_folder+"_"+file.replace(".eml",'')+".csv",graph_folder+"/"+email_folder+"_"+file.replace(".eml",''))
        os.remove(graph_folder+"/"+email_folder+"_"+file.replace(".eml",'')+".csv")

def find_differ_inter_domain(email_folder,inter_domain_file):
    files = os.listdir(email_folder)
    for file in files:  # 遍历文件夹
        if file == "duplicate":
            continue
        nodes, edges = one_email_to_edges(email_folder + "/" + file)
        for edge in edges:
            edge_part=edge.split(",")
            if(edge_part[2]==("0" or "2" or "4")):
                if(edge_part[0]!=edge_part[1]):
                    with open(inter_domain_file,'a+',encoding="utf-8") as f:
                        f.write(edge_part[1]+"\n");

if __name__=="__main__":
    find_differ_inter_domain("nazario_phishing_2021","inter_domain.txt")