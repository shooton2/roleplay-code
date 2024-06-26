import openai
from openai import OpenAI
import re
import json
import glob
import os

api_key = "sk-HUoJ0dhvM080s0Z1sW6txqmaXMiUbiRzMorF67oqJXfs9ScO"
api_base = "https://api.chatanywhere.tech/v1"
folder_path = "./RoleBench/profiles-eng/"
output_folder = "./RoleBench/dialogue_sentiment/"
count = 0
count_dialogue = 0
list_3 = []
emotion_list = []

def open_jsonl(jsonl_file_path):
    data_list = []
    with open(jsonl_file_path,"r",encoding="utf-8") as r:
        for line in r:
        # 去除前后的空白字符
            line = line.strip()
        # 使用正则表达式移除无效的控制字符
            line = re.sub(r'[\x00-\x1F\x7F]', '', line)
            try:
            # 解析JSON对象
                data = json.loads(line)
                data_list.append(data)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e} - Line: {line}")
    return data_list


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

def process_dialogue(dialogue,three_dialogue):
    prompt = f""" 
        在给定的英文对话中，分析角色说话时的情感。

        '情感分类':
        {emotion_labels_eng}

        请仔细阅读'原始对话'，根据其内容和语调判断出'需要分析的对话'的情感，并给出相应的分类并说明理由。
        1. '需要分析的对话'只做一个情感分类，并且只能在给定的'情感分类'中选择。
        2. 如果表达了多种情感，选择最为突出或主要的情感类型。
        3. 如果文本中的情感不明显或难以界定，请将其归类为'neutral'。
        4. 确保你的分类是基于文本内容而非你个人的感受或偏见。



        '需要分析的对话':
        {dialogue}        
        '原始对话':
        {three_dialogue}
    """
    response = llm.chat.completions.create(messages=[{"role":"user","content":prompt}],model="gpt-3.5-turbo")
    response = response.choices[0].message.content
    print(response)
    tag = None

    for emotions in emotion_labels_eng:
        if emotions in response:
            tag = emotions
            emotion_list.append(emotions)
            break
        else:
            continue
        ###情绪没有在给定的分类中，默认中立    
    if tag == None:
        emotion_list.append("neutral")


llm = OpenAI(api_key=api_key,base_url=api_base)
emotion_labels_eng = ["anger","happiness","sadness","surprise","neutral","disappointment","excitement","fear","care","comfort","hope"]



all_jsonl = read_jsonl_files(folder_path)


for i,role_dialogues in enumerate(all_jsonl):   ##读取所有的jsonl文件
    print(f"role dialogues len:{len(role_dialogues)}")
    for role_dialogue in role_dialogues:    ##单独的jsonl文件
        if count < 3:
            list_3.append(role_dialogue["content"])
            count += 1
        elif count == 3:
            print(list_3)
            for k in range(len(list_3)):
                process_dialogue(list_3[k],list_3)
                print(emotion_list[count_dialogue])
                count_dialogue += 1
            count = 0
            list_3 = []
    if len(list_3) != 0:
        for k in range(len(list_3)):
            process_dialogue(list_3[k],list_3)

    
    print(f"emotion list size:{len(emotion_list)}")
            

    with open(f"{output_folder}dialogue_{i}.jsonl","w",encoding="utf-8") as w:
        for j,dialog in enumerate(role_dialogues):
            role = dialog["role"]
            content = dialog["content"]
            sentiment = emotion_list[j]
            dialog["sentiment"] = sentiment
            json.dump(dialog, w, ensure_ascii=False)
            w.write("\n")
    emotion_list = []




