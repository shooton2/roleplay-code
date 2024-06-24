###role生成profile


import openai
from openai import OpenAI
import re
import json
api_key = ""
api_base = ""
role_jp_path = "./hutao/japan_profile.jsonl"
output_path = "./hutao/hutao_profile_jp.json"
role_eng_path = "./RoleBench/instruction-eng/role-specific-Abraham Lincoln.jsonl"
##加载jsonl文件
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


role_profiles = open_jsonl(role_eng_path)
profile = []
for i,role_profile in enumerate(role_profiles):
    profile.append((role_profile["instruction"],role_profile["answer"]))
    if i > 50 :
        break 



llm = OpenAI(api_key=api_key,base_url=api_base)
prompt_en = f"""
请根据给出的'角色介绍',其中'角色介绍'为英语,总结出角色的'Name', 'Birthday', 'Character', 'Career', 'Hobbies', 'Special Skills', 'Dreams', 'Relationships', 'Favorite Food', 'Nasty Food', , 'Other'。
最后输出为json格式，并且输出英语。


'角色介绍':
{profile}
"""

response = llm.chat.completions.create(messages=[{"role":"user","content":prompt_en}],model="gpt-3.5-turbo")
profile = response.choices[0].message.content
print(profile)
#with open(output_path,"w",encoding="utf-8") as w:
#    w.write(profile)

