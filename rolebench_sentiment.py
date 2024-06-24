import openai
from openai import OpenAI
import re
import json
import glob
import os

api_key = ""
api_base = ""
folder_path = "./RoleBench/profiles-eng/"
output_folder = "./RoleBench/dialogue_sentiment/"
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


llm = OpenAI(api_key=api_key,base_url=api_base)
emotion_labels_eng = ["anger","happiness","sadness","surprise","neutral","disappointment","excitement","fear","care","comfort"]

emotion = []

all_jsonl = read_jsonl_files(folder_path)
for i,role_dialogues in enumerate(all_jsonl):   ##读取所有的jsonl文件
    for role_dialogue in role_dialogues:    ##单独的jsonl文件
        prompt = f"""
        在给定的英文对话中，分析角色说话时的情感。

        '情感分类':
        {emotion_labels_eng}

        请仔细阅读对话文本，根据其内容和语调判断出最显著的情感，并给出相应的分类并说明理由。
        1. 对话文本只做一个情感分类，并且只能在给定的'情感分类'中选择。
        2. 如果文本表达了多种情感，选择最为突出或主要的情感类型。
        3. 如果文本中的情感不明显或难以界定，请将其归类为'neutral'。
        4. 确保你的分类是基于文本内容而非你个人的感受或偏见。



        角色:
        {role_dialogue["role"]}        
        对话:
        {role_dialogue["content"]}
        """
        response = llm.chat.completions.create(messages=[{"role":"user","content":prompt}],model="gpt-3.5-turbo")
        response = response.choices[0].message.content
        print(response)
        tag = ""

        for emotions in emotion_labels_eng:
            if emotions in response:
                tag = emotions
                emotion.append(emotions)
                break
        ###情绪没有在给定的分类中，默认中立    
        if tag == "":
            emotion.append("neutral") 

    with open(f"{output_folder}dialogue_{i}.jsonl","w",encoding="utf-8") as w:
        for j,dialog in enumerate(role_dialogues):
            role = dialog["role"]
            content = dialog["content"]
            sentiment = emotion[j]
            dialog["sentiment"] = sentiment
            json.dump(dialog, w, ensure_ascii=False)
            w.write("\n")
