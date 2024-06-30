import openai
import json
import re
from openai import OpenAI
import jsonlines
import random

api_key = "sk-HUoJ0dhvM080s0Z1sW6txqmaXMiUbiRzMorF67oqJXfs9ScO"
api_base = "https://api.chatanywhere.tech/v1"
file_path = "./hutao/japan_profile.jsonl"
profile_path = "./output/profile/role_profile_Alvy_Singer.json"##角色profile生成的路径

out_question_path = "./output/multi_round_dialog/lincoln.jsonl"##输出路径
role_eng_path = "./RoleBench/instructions-eng/role-specific-Alvy Singer.jsonl" ##输入路径
num_question = 10  ##生成问题和回答的轮次

#用户指定
sentiment = "happiness"


###读取第一阶段生成的role profile
def open_profile(profile_path):
    with open(profile_path,"r",encoding="utf-8") as r:
        profile = r.read()
        profile = json.loads(profile)
    return profile



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



#role_profiles = open_jsonl(role_eng_path)
#profile_list = []
#for i,role_profile in enumerate(role_profiles):
#    profile_list.append((role_profile["instruction"],role_profile["answer"]))
#    if i > 50 :
#        break 
profile = open_profile(profile_path)


###情感分类
emotion_labels_jp = ["怒り", "喜び", "悲しみ", "驚き", "中立", "落胆", "興奮", "恐れ", "関心","慰め"]
emotion_labels_eng = ["anger","happiness","sadness","surprise","neutral","disappointment","excitement","fear","care","comfort"]

##讨论话题分类
topic_eng = ["Technology","Health and wellness","Travel and adventure","Food and drink","Art and culture","Science and innovation","Fashion and style","Relationships and dating"," Sports and fitness","Nature and the environment","Music and entertainment","Politics and current events","Education and learning","Money and finance","Work and career","Philosophy and ethics","History and nostalgia","Social media and communication","Creativity and inspiration","Personal growth and development","Spirituality and faith","Pop culture and trends","Beauty and self-care","Family and parenting","Entrepreneurship and business"," Literature and writing","Gaming and technology","Mindfulness and meditation","Diversity and inclusion","Travel and culture exchange"]

##随机生成情绪和话题
random_emo = random.randint(0,9)
random_topic = random.randint(0,29)

###随机生成话题和情绪
#topic = topic_eng[random_topic]
#sentiment = emotion_labels_eng[random_emo]


###生成英文的qa问答
def generate_english_question_answer(out_question_path,topic,sentiment):

    with open(out_question_path,"a",encoding="utf-8") as w:
        writer = jsonlines.Writer(w)
        for i in range(num_question):
            prompt1 = f"""
            请根据给出的'角色介绍'，用英语生成1个与{topic}相关的问题。只输出问题本身。
            '角色介绍':
            {profile}
            """
            llm = OpenAI(api_key=api_key,base_url=api_base)
            response = llm.chat.completions.create(messages=[{"role":"user","content":prompt1}],model="gpt-3.5-turbo")
            instruction = response.choices[0].message.content
            print(instruction)
            ##生成5轮对话
            prompt2 = f"""
            请'ai'扮演"{profile["Name"]}",以{sentiment}的心情,使用英语讨论'问题'，"ai"和'user'分别对话5次，分别根据对方的回答进行回复，使用json格式:
            ["role":"ai","content":"","role":"user","content":""]

            '问题':
            {instruction}
            '角色介绍':
            {profile}
            """
            answer = llm.chat.completions.create(messages=[{"role":"user","content":prompt2}],model="gpt-3.5-turbo")
            answer = answer.choices[0].message.content
            print(answer)
            writer.write({"question":instruction.strip(),"answer":answer.strip()})
        writer.close()

#for topics in topic_eng:
#    generate_english_question_answer(out_question_path,topics,sentiment)

###去除重复的问题
def remove_same_question(out_question_path):
    with open(out_question_path, 'r', encoding='utf-8') as file:
        data_lines = file.readlines()
    unique_questions = {}
    for line in data_lines:
        data = json.loads(line)
        question = data['question']
        if question not in unique_questions:
            unique_questions[question] = data
    with open(out_question_path, 'w', encoding='utf-8') as file:
        for data in unique_questions.values():
            file.write(json.dumps(data) + '\n')
    print(f"去重后的数据已写入 {out_question_path}")

remove_same_question(out_question_path)