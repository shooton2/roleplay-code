from transformers import AutoModelForCausalLM, AutoTokenizer
import json
import re
import jsonlines
import random
import argparse
parser = argparse.ArgumentParser()

parser.add_argument("out_question_path",type=str,help="output multi round dialogue path")
parser.add_argument("profile_path",type=str,help="role profile path")
args = parser.parse_args() 

device = "cuda" # the device to load the model onto
out_question_path = "./output/multi_round_dialog/Andrew_Detmer.jsonl"##输出路径


# Now you do not need to add "trust_remote_code=True"
model = AutoModelForCausalLM.from_pretrained(
    "/maindata/data/shared/public/Common-Models/Qwen2-7B-Instruct",
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("/maindata/data/shared/public/Common-Models/Qwen2-7B-Instruct")

# Instead of using model.chat(), we directly use model.generate()
# But you need to use tokenizer.apply_chat_template() to format your inputs as shown below
topic_eng = ["Technology","Health and wellness","Travel and adventure","Food and drink","Art and culture","Science and innovation","Fashion and style","Relationships and dating"," Sports and fitness","Nature and the environment","Music and entertainment","Politics and current events","Education and learning","Money and finance","Work and career","Philosophy and ethics","History and nostalgia","Social media and communication","Creativity and inspiration","Personal growth and development","Spirituality and faith","Pop culture and trends","Beauty and self-care","Family and parenting","Entrepreneurship and business"," Literature and writing","Gaming and technology","Mindfulness and meditation","Diversity and inclusion","Travel and culture exchange"]
emotion_labels_eng = ["anger","happiness","sadness","surprise","neutral","disappointment","excitement","fear","care","comfort"]
sentiment_times = [1,3,1,2,2,1,3,1,3,3]



def qwen2_chat(model,tokenizer,prompt,device):
    messages = [
    {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(device)
    generated_ids = model.generate(
        model_inputs.input_ids,
        max_new_tokens=512
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    print(response)
    return response


profile_path = "./output/profile/role_profile_Andrew_Detmer.json"##角色profile生成的路径

def open_profile(profile_path):
    with open(profile_path,"r",encoding="utf-8") as r:
        profile = r.read()
        profile = json.loads(profile)
    return profile

profile = open_profile(args.profile_path)

###选择多个topics
def choose_topics(num_topics,model,tokenizer,device):
    ###生成多个topics的prompt
    prompt = f"""
    Select {num_topics} topics that matches the 'Role Introduction' from 'Topics for Selection'.
    Please only output these {num_topics} topics.

    'Role Introduction':
    {profile}

    'Topics for Selection':
    {topic_eng}
    """
    topics = qwen2_chat(model,tokenizer,prompt,device)
    topics = topics.strip().split("\n")
    topics = [re.sub(r'^\d+\.\s*', '', topic) for topic in topics]
    return topics



def generate_question(topic,model,tokenzier,device):

    prompt = f"""
    Generate one question related to the 'Topic' based on the given 'Role Instruction'.
    Please output the words less than 50.

    'Role Instruction':
    {profile}

    'Topic':
    {topic}
    """
    print(topic)
    question = qwen2_chat(model,tokenizer,prompt,device)
    return question

##topic生成
#topics_list = choose_topics(5,model,tokenizer,device)
#question_list = []
###question生成
#for topic in topics_list:
#    question = generate_question(topic,model,tokenizer,device)
#    question_list.append(question)



conversation_requirements = f"""
###The following are the requirements for the scenario dialogues:

Each round of dialogue must introduce new plot developments, sudden events, or scene changes, revealing new emotional conflicts, plot twists, and relationship developments to attract player interest through continuous drama scenarios.
Design open-ended storylines, avoiding guiding towards reconciliation or idealized scenarios between the '{profile["Name"]}' and 'user', and prohibit creating closed or perfect endings (e.g., goodbye, goodnight, farewell, reconciliation, etc.), avoiding final plot points or topics.

'The following are the speaking requirements for 'user' ':
Brief responses, passive, not initiating topics;
Prohibit the use of parentheses, avoiding parenthetical literature, and directly output dialogue content;
Keep each response brief, just a few words.


'The following are the speaking requirements for {profile["Name"]}':
{profile["Name"]}'s speech should be concise, clear, down-to-earth, avoiding stiff, clichéd, or pompous vocabulary, avoiding motivational, generic, or hollow platitudes, and not sounding like reading a script. Keep each sentence under 30 words to avoid verbosity.
{profile["Name"]}'s speech should be close to the dialogue style of the second dimension, using catchphrases, repetitive sentence patterns (e.g., "Bro~... hehe... um... give me some money to spend"), punctuation marks (e.g., "You! Say! Who! Beggar! Huh?!"), interjections (e.g., "ah", "oh", "uh"), and slang to add emotional depth and realism to the dialogue.
{profile["Name"]}'s speech should include both dialogue content and descriptive language, describing {profile["Name"]}'s body interaction or emotional response in parentheses, enriching the main details of the scene or transition techniques to enhance the story's visual and immersive feel.
Limit to one parenthetical description per sentence to avoid breaking up the dialogue with too many parentheses.
"""

##生成一个角色关于一个问题的多轮对话
def generate_eng_qa(out_question_path,question,topic,sentiment,profile,num_dialogues):
    with open(out_question_path,"a",encoding="utf-8") as w:
        writer = jsonlines.Writer(w)
        history = []
        prompt1 = f"""
        Play the role of the character in the 'Character Profile' and talk to the 'user' in the first person. 
        In the mood of {sentiment}, discuss the 'question' in English, and have a conversation with '{profile["Name"]}' and 'user'.The conversation should follow the 'Conversation Requirements'
        using json format,like:
        {{"role":{profile["Name"]},"content":""}}
        {{"role":"user","content":""}}

        'question':
        {question}

        'Character Profile':
        {profile}

        'Conversation Requirements':
        {conversation_requirements}
        """
        answer = qwen2_chat(model,tokenizer,prompt1,device)
        history.append(answer)

        for k in range(num_dialogues):####多轮对话的轮次
            prompt2 = f"""
            Play the role of the character in the 'Character Profile' and talk to the 'user' in the first person. 
            Please in the mood of {sentiment},Continue the conversation with 'user' according to the 'Conversation Information' and don't repeat it.
            using json format,like:
            {{"role":{profile["Name"]},"content":""}}
            {{"role":"user","content":""}}


            'Character Profile':
            {profile}

            'Conversation Information':
            {history[-1]}

            'Conversation Requirements':
            {conversation_requirements}

            """
            dialogue = qwen2_chat(model,tokenizer,prompt2,device)
            history.append(dialogue)

        prompt3 = f"""
        Play the role of the character in the 'Character Profile' and talk to the 'user' in the first person. 
        Please in the mood of {sentiment},ending the conversation with 'user' based on the 'Conversation Information'.
        using json format,like:
        {{"role":{profile["Name"]},"content":""}}

        'Character Profile':
        {profile}

        'Conversation Information':
        {history[-1]}

        'Conversation Requirements':
        {conversation_requirements}
        """
        dialogue = qwen2_chat(model,tokenizer,prompt3,device)
        history.append(dialogue)

        writer.write({"npc_name":profile["Name"],"question":question.strip(),"answer":history,"sentiment":sentiment,"topic":topic})
    writer.close()

#generate_eng_qa(out_question_path,question_list[0],topics_list[0],"happiness",profile,num_dialogues=20)
topics_list = choose_topics(5,model,tokenizer,device)
question_list = []
for topic in topics_list:
    question = generate_question(topic,model,tokenizer,device)
    question_list.append(question)

for i,question in enumerate(question_list):  ##
    for emotion in emotion_labels_eng:
        for times in sentiment_times:
            generate_eng_qa(args.out_question_path,question,topics_list[i],emotion,profile,num_dialogues=20)



















