import csv
import pandas as pd

def edge_count(edge_file):
    with open(edge_file, 'r', encoding="utf-8") as edgefile:
        reader=csv.reader(edgefile)
        edges_fraud=[" ".join(row) for row in reader]
        edge_count_fraud=pd.value_counts(edges_fraud).to_dict()

def count_multi_set_nodes(node_file1,node_file2):
    # 合并两个node文件，统一索引
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
    print(len(nodes_set))

if __name__ == "__main__":
    count_multi_set_nodes("datacon_fraud_graph/nodes_all.csv","nazario_2021_graph/nodes_all.csv")