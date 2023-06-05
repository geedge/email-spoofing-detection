import networkx as nx
import csv

def show_connected_subgraphs(edge_file):
    G = nx.Graph()
    edge_list=[]
    with open(edge_file, 'r', encoding="utf-8") as edgefile:
        edges = csv.DictReader(edgefile)
        for edge in edges:
            edge_list.append((edge['node1'],edge['node2']))
    G.add_edges_from(edge_list)

    largest = max(nx.connected_components(G),key=len)
    largest_connected_subgraph = G.subgraph(largest)
    node_num_list=[]
    edge_num_list=[]

    for c in sorted(nx.connected_components(G),key=len,reverse=True):
        subgraph=G.subgraph(c)
        node_num_list.append(nx.number_of_nodes(subgraph))
        edge_num_list.append(nx.number_of_edges(subgraph))
        # with open("subgraph_edges.txt", 'a+', encoding="utf-8") as f:
        #     f.write(str(subgraph.edges)+"\n")


    import matplotlib.pyplot as plt
    import numpy as np

    x = np.array(node_num_list)
    y = np.array(edge_num_list)

    plt.xlabel("nodes")
    plt.ylabel("edges")
    plt.scatter(x, y)
    plt.show()

def node_type_count(node_file):
    node_count_dict={}
    with open(node_file, 'r', encoding="utf-8") as nodefile:
        nodes = csv.DictReader(nodefile)
        for node in nodes:
            if node["type"] in node_count_dict:
                node_count_dict[node["type"]]+=1
            else:
                node_count_dict[node["type"]]=1
    print(node_count_dict)

import pandas as pd
def benign_fraud_count(node_file,subgraph_node_file):
    nodes = pd.read_csv(node_file, encoding='utf-8')
    fraud_count=0
    benign_count=0
    domain_count=0
    IP_count=0
    x_mailer_count=0
    with open(subgraph_node_file, 'r', encoding="utf-8") as f:
        line=f.readline().strip()
        line=line.replace("['","")
        line=line.replace("']","")
        sub_nodes=line.split("', '")
        # print(nodes['index'].dtypes)
        for sub_node in sub_nodes:
            # print(type(sub_node))
            node_index=nodes[(nodes['index']==int(sub_node))].index.tolist()[0]
            node_name=nodes.at[node_index,'name']
            node_type = nodes.at[node_index, 'type']
            if node_type==0:
                node_num=node_name[5:]
                if int(node_num) <= 6550 and int(node_num) >=6264:
                    fraud_count+=1
                else:
                    benign_count+=1
            else:

                if node_type==1 :
                    domain_count+=1
                elif node_type==2:
                    IP_count+=1
                else:
                    x_mailer_count+=1

    print("fraud: "+str(fraud_count))
    print("benign: "+str(benign_count))
    print("domain: "+str(domain_count))
    print("IP: "+str(IP_count))
    print("x-mailer: "+ str(x_mailer_count))
        #     node2_index = nodes[(nodes['name'] == edge['node2'])].index.tolist()[0]
        #     edge_list.append(str(node1_index)+","+str(node2_index))

def merge_meta_path(edge_file,meta_path_file):
    G = nx.Graph()
    edge_list=[]
    with open(edge_file, 'r', encoding="utf-8") as edgefile:
        edges = csv.DictReader(edgefile)
        for edge in edges:
            edge_list.append((edge['node1'],edge['node2']))
    G.add_edges_from(edge_list)

    # largest = max(nx.connected_components(G),key=len)
    # largest_connected_subgraph = G.subgraph(largest)
    subgraph_edges=list(G.edges)
    # print(subgraph_edges)
    meta_path_list=[]
    for i in range(0,len(subgraph_edges)):
        for j in range(0,len(subgraph_edges)):
            if subgraph_edges[i][1] == subgraph_edges[j][0]:
                meta_path_list.append((subgraph_edges[i][0],subgraph_edges[i][1],subgraph_edges[j][1]))
            elif subgraph_edges[i][1] == subgraph_edges[j][1]:
                meta_path_list.append((subgraph_edges[i][0],subgraph_edges[i][1],subgraph_edges[j][0]))
    print(meta_path_list)
    with open(meta_path_file, 'w', encoding="utf-8") as f:
        f.write("node1,path,node2\n")
        for meta_path in meta_path_list:
            f.write(meta_path[0]+","+meta_path[1]+","+meta_path[2]+"\n")

def new_index_to_subgraph(edge_file,subgraph_index_file,node_file):
    nodes = pd.read_csv(node_file, encoding='utf-8')
    G = nx.Graph()
    edge_list=[]
    with open(edge_file, 'r', encoding="utf-8") as edgefile:
        edges = csv.DictReader(edgefile)
        for edge in edges:
            edge_list.append((edge['node1'],edge['node2']))
    G.add_edges_from(edge_list)

    # largest = max(nx.connected_components(G),key=len)
    # largest_connected_subgraph = G.subgraph(largest)
    subgraph_edges=list(G.edges)
    with open(subgraph_index_file,'w',encoding='utf-8') as new_index_file:
        new_index_file.write("oldIndex,newIndex,label\n")
        index=1
        new_node_dict={}
        for edge in subgraph_edges:
            node_index = nodes[(nodes['index'] == int(edge[0]))].index.tolist()[0]
            node_name = nodes.at[node_index, 'name']
            node_type = nodes.at[node_index,'type']
            if node_type == 0:
                if node_name[5:] in new_node_dict:
                    continue
                else:
                    if int(node_name[5:])<2010:
                        new_node_dict[node_name[5:]]=str(index)
                        new_index_file.write(edge[0]+","+str(index)+",1\n")
                        index+=1
                    else:
                        new_node_dict[node_name[5:]] = str(index)
                        new_index_file.write(edge[0] + "," + str(index) + ",0\n")
                        index+=1
            node_index = nodes[(nodes['index'] == int(edge[1]))].index.tolist()[0]
            node_name = nodes.at[node_index, 'name']
            node_type = nodes.at[node_index, 'type']
            if node_type == 0:
                if node_name[5:] in new_node_dict:
                    continue
                else:
                    if int(node_name[5:]) < 2010:
                        new_node_dict[node_name[5:]] = str(index)
                        new_index_file.write(edge[1] + "," + str(index) + ",1\n")
                        index += 1
                    else:
                        new_node_dict[node_name[5:]] = str(index)
                        new_index_file.write(edge[1] + "," + str(index) + ",0\n")
                        index += 1


def split_meta_path(node_file,meta_path_file,index_file):
    nodes = pd.read_csv(node_file, encoding='utf-8')
    indexes = pd.read_csv(index_file,encoding='utf-8')
    EDE_list=[]
    EIE_list=[]
    EXE_list=[]
    with open(meta_path_file, 'r', encoding="utf-8") as f:
        paths=csv.DictReader(f)
        for path in paths:
            node_index=nodes[(nodes['index']==int(path['path']))].index.tolist()[0]
            node_type = nodes.at[node_index, 'type']
            if node_type == 1:
                EDE_list.append((path['node1'],path['node2']))
            elif node_type == 2:
                EIE_list.append((path['node1'],path['node2']))
            elif node_type == 3:
                EXE_list.append((path['node1'],path['node2']))
    with open("EDE_list.csv",'w',encoding="utf-8") as f:
        f.write("eml1,eml2\n")
        for ede in EDE_list:
            # node1_name = nodes.at[int(ede[0]),'name']
            # node1_num = node1_name[5:]
            new_node_index = indexes[(indexes['oldIndex'] == int(ede[0]))].index.tolist()[0]
            node1_num = indexes.at[new_node_index,'newIndex']
            # node2_name = nodes.at[int(ede[1]),'name']
            # node2_num = node2_name[5:]
            new_node_index = indexes[(indexes['oldIndex'] == int(ede[1]))].index.tolist()[0]
            node2_num = indexes.at[new_node_index, 'newIndex']
            f.write(str(node1_num)+","+str(node2_num)+"\n")
    with open("EIE_list.csv",'w',encoding="utf-8") as f:
        f.write("eml1,eml2\n")
        for eie in EIE_list:
            # node1_name = nodes.at[int(eie[0]), 'name']
            # node1_num = node1_name[5:]
            new_node_index = indexes[(indexes['oldIndex'] == int(eie[0]))].index.tolist()[0]
            node1_num = indexes.at[new_node_index, 'newIndex']
            # node2_name = nodes.at[int(eie[1]), 'name']
            # node2_num = node2_name[5:]
            new_node_index = indexes[(indexes['oldIndex'] == int(eie[1]))].index.tolist()[0]
            node2_num = indexes.at[new_node_index, 'newIndex']
            f.write(str(node1_num)+","+str(node2_num)+"\n")
    with open("EXE_list.csv",'w',encoding="utf-8") as f:
        f.write("eml1,eml2\n")
        for exe in EXE_list:
            # node1_name = nodes.at[int(exe[0]), 'name']
            # node1_num = node1_name[5:]
            new_node_index = indexes[(indexes['oldIndex'] == int(exe[0]))].index.tolist()[0]
            node1_num = indexes.at[new_node_index, 'newIndex']
            # node2_name = nodes.at[int(exe[1]), 'name']
            # node2_num = node2_name[5:]
            new_node_index = indexes[(indexes['oldIndex'] == int(exe[1]))].index.tolist()[0]
            node2_num = indexes.at[new_node_index, 'newIndex']
            f.write(str(node1_num) + "," + str(node2_num) + "\n")

import numpy as np
def meta_path_to_matrix(meta_path_file):
    num = [[0 for i in range(0, 6975)] for j in range(0, 6975)]
    with open(meta_path_file, 'r') as f:
        cols = csv.DictReader(f)
        for col in cols:
            num[int(col["eml1"])-1][int(col["eml2"])-1]=1
            num[int(col["eml2"])-1][int(col["eml1"])-1] = 1
    for i in range(0,6975):
        num[i][i] = 1
    arr = np.array(num)
    return arr

def extract_label(label_file):
    num = [[0 for i in range(0, 2)] for j in range(0, 6975)]
    with open(label_file, 'r') as f:
        cols = csv.DictReader(f)
        for col in cols:
            if int(col["label"]) == 1:
                num[int(col["newIndex"])-1][0] = 1
            elif int(col["label"]) ==0:
                num[int(col["newIndex"])-1][1] =1
    arr = np.array(num)
    return arr

import random
def generate_features():
    features = [[0 for i in range(0, 8)] for j in range(0, 6975)]
    for i in range(0,6975):
        length=random.randint(1,8)
        for j in range(0,length):
            loc = random.randint(0,7)
            features[i][loc]=1
    features = np.array(features)
    return features

from scipy.io import savemat
def save_data(EDE_file,EIE_file,EXE_file,label_file,mat_file):
    shuffled_index = np.random.permutation(6975)
    split_index1 = int(6975 * 0.6)
    split_index2 = int(6975*0.8)
    train_index = shuffled_index[:split_index1]
    train_idx = np.array([train_index])
    val_index = shuffled_index[split_index1:split_index2]
    val_idx = np.array([val_index])
    test_index = shuffled_index[split_index2:]
    test_idx = np.array([test_index])
    label = extract_label(label_file)
    EDE = meta_path_to_matrix(EDE_file)
    EIE = meta_path_to_matrix(EIE_file)
    EXE = meta_path_to_matrix(EXE_file)
    features = generate_features()
    savemat(mat_file,{'EIE':EIE,'EDE':EDE,'EXE':EXE,'features':features,'label':label,'train_idx':train_idx,'val_idx':val_idx,'test_idx':test_idx})



if __name__ =="__main__":
    # benign_fraud_count("hunter_node.csv","first_subgraph_nodes1.txt")
    # node_type_count("hunter_node.csv")
    # show_connected_subgraphs("hunter_edge_index_only.csv")
    # merge_meta_path("hunter_edge_index_only.csv","meta_path_original.csv")
    # split_meta_path("hunter_node.csv","meta_path_original.csv","subgraph_index.csv")
    # meta_path_to_matrix("EDE_list.csv")
    # new_index_to_subgraph("hunter_edge_index_only.csv","subgraph_index.csv","hunter_node.csv")
    # extract_label("subgraph_index.csv")
    save_data("EDE_list.csv","EIE_list.csv","EXE_list.csv","subgraph_index.csv","SG_dataset.mat")
    # generate_features()