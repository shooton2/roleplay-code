###role生成profile


import openai
from openai import OpenAI
import re
import json

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

data_list = open_jsonl(role_eng_path)
role = data_list

api_key = ""
api_base = ""


llm = OpenAI(api_key=api_key,base_url=api_base)
prompt_jp = f"""
请根据给出的'角色介绍',其中'角色介绍'为日本语,总结出角色的'名前'、'誕生日'、'キャラクター'、'経歴'、'趣味'、'特技'、'夢'、'人間関係'、'好きな食べ物'、'嫌いな食べ物'和'その他'。
最后输出为json格式，并且输出日本语。


'角色介绍':
{role}
"""

response = llm.chat.completions.create(messages=[{"role":"user","content":prompt_jp}],model="gpt-3.5-turbo")
profile = response.choices[0].message.content
print(profile)
#with open(output_path,"w",encoding="utf-8") as w:
#    w.write(profile)

