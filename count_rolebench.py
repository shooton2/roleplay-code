import json
import glob
import os
import numpy as np
import re
#file_path = "./japanese-Roleplay/japanese-Roleplay-2.jsonl"
#out_path = "./japanese-Roleplay/dialog_length2.txt"

#dialog_num = []
#with open(file_path,"r",encoding="utf-8") as r:
#    for line in r:
#        data = json.loads(line.strip())
#        dialog_num.append(len(data["posts"]))

#avg_dialog = sum(dialog_num)/len(dialog_num)
#with open(out_path,"w",encoding="utf-8") as w:
#    w.write(str(dialog_num))
#    w.write(f"\n平均对话轮次{avg_dialog}")




def read_jsonl_files(folder_path):
    # 查找文件夹下所有的JSONL文件
    jsonl_files = glob.glob(os.path.join(folder_path, '*.jsonl'))
    
    all_data = []
    
    # 遍历每个JSONL文件并读取数据
    for file_path in jsonl_files:
        jsonl_data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                jsonl_data.append(json.loads(line))

            all_data.append(jsonl_data)    
                
    return all_data


folder_path = "./RoleBench/profiles-eng/"
out_path = "./rolebench_dialog_num.txt"
##记录所有的对话轮次
dialog_num = []
all_data = read_jsonl_files(folder_path)

for data in all_data:
    dialog_num.append(len(data))
    print(len(data))


dialog_num = np.array(dialog_num)
avg_num = sum(dialog_num) / len(dialog_num)
with open(out_path,"w",encoding="utf-8") as w:
    w.write(f"总共对话文本个数{len(dialog_num)}\n")
    w.write("每个对话文本的对话轮次:\n") 
    w.write(str(dialog_num))
    w.write(f"\n平均对话轮次{avg_num}")
    w.write(f"\n对话轮次低于平均值的个数:{np.sum(dialog_num < avg_num)}")
    w.write(f"\n对话轮次高于平均值的个数:{np.sum(dialog_num > avg_num)}")




