import networkx as nx
import csv
import pandas as pd
import dgl

def read_graph_networkx(node_file,edge_file):
    G = nx.Graph()
    node_list=[]
    edge_list=[]
    with open(node_file, 'r', encoding="utf-8") as csvfile:
        nodes = csv.DictReader(csvfile)
        for node in nodes:
            node_list.append((node["index"],{"label":node["name"]}))
    G.add_nodes_from(node_list)
    with open(edge_file, 'r', encoding="utf-8") as edgefile:
        reader1 = csv.reader(edgefile)
        edges = [" ".join(row) for row in reader1]
        edge_count = pd.value_counts(edges).to_dict()
    for key in edge_count:
        edge_param=key.split(" ")
        edge_list.append((edge_param[0],edge_param[1]))
    G.add_edges_from(edge_list)
    print(G)

    # nx.draw(G,font_size=20)
    # plt.show()

    subgraphs=nx.connected_components(G)
    for c in sorted(subgraphs,key=len,reverse=True):
        if len(c)<=10:
            break
        print(G.subgraph(c))

# nx.draw(largest_connected_subgraph,with_labels=True)

def read_graph_dgl(node_file,edge_file_fraud,edge_file_legi):
    graph_dict={}
    node_dict={}
    with open(node_file, 'r', encoding="utf-8") as nodefile:
        nodes = csv.DictReader(nodefile)
        for node in nodes:
            if node["type"] == '0':
                node_dict[node["index"]]="sender_domain"
            elif node["type"] == '1':
                node_dict[node["index"]]="inter_domain"
            elif node["type"] == '2':
                node_dict[node["index"]]="IP"
            else:
                node_dict[node["index"]]="client"

    with open(edge_file_fraud, 'r', encoding="utf-8") as edgefile:
        reader1 = csv.reader(edgefile)
        edges = [" ".join(row) for row in reader1]
        edge_count = pd.value_counts(edges).to_dict()
    for key in edge_count:
        edge_param=key.split(" ")
        if graph_dict[(node_dict[edge_param[0]],"fraud",node_dict[edge_param[1]])]:
            graph_dict[(node_dict[edge_param[0]], "fraud", node_dict[edge_param[1]])].append((edge_param[0],edge_param[1]))
        else:
            graph_dict[(node_dict[edge_param[0]], "fraud", node_dict[edge_param[1]])]=[(edge_param[0],edge_param[1])]
    # 字典的每个值都是一个元组的列表。
    # 节点是从零开始的整数ID。 不同类型的节点ID具有单独的计数。
    ratings = dgl.heterograph(graph_dict)

import torch as th
def test():
    # 边 0->1, 0->2, 0->3, 1->3
    u, v = th.tensor(["qq.com","113.108.11.234","qq.com"]), th.tensor(["qq.com", "qq.com","127.0.0.1"])
    g = dgl.graph((u, v))
    print(g)  # 图中节点的数量是DGL通过给定的图的边列表中最大的点ID推断所得出的
    # 获取节点的ID
    print(g.nodes())
    # 获取边的对应端点
    print(g.edges())
    # 获取边的对应端点和边ID
    print(g.edges(form='all'))

if __name__=="__main__":
    # read_graph_dgl("all_nodes.csv","fraud_edges_index_only.csv","")
    # read_graph_networkx("all_nodes.csv","all_edges_index_only.csv")
    test()