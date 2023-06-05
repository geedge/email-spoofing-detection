from parseEml import parseEml
import os

def read_spf(email_path):
    mail = parseEml(email_path)
    auth_result = mail.get_auth_results()
    if auth_result and "spf=" in auth_result:
        tmp_list = auth_result.split("spf=")
        spf_result=tmp_list[1].split(" ")[0]
    else:
        spf_result=None
    return spf_result

def spf_count(email_folder):
    spf_count_dict={}
    files = os.listdir(email_folder)
    print(email_folder+":\ntotal: "+str(len(files)))
    for file in files:  # 遍历文件夹
        if file == "duplicate":
            continue
        spf_result=read_spf(email_folder+"/"+file)
        if spf_result in spf_count_dict:
            spf_count_dict[spf_result]+=1
        else:
            spf_count_dict[spf_result]=1
    print(spf_count_dict)

def inter_domain_count(inter_domain_file):
    count_dict={}
    with open(inter_domain_file,"r",encoding="utf-8") as f:
        line = f.readline()
        while line:
            line=line.strip()
            if line in count_dict:
                count_dict[line]+=1
            else:
                count_dict[line]=1
            line = f.readline()
        a = sorted(count_dict.items(), key=lambda x: x[1], reverse=True)
        print(a)

if __name__ == "__main__":
    inter_domain_count("inter_domain.txt")