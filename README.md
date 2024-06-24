# roleplay-code

1.previous step:
We use gpt-3.5-turbo model to generate role profile , question and answer , multi-numbers dialogues with sentiment. 
Download RoleBench datasets and input api_key or base_url.

https://huggingface.co/datasets/ZenMoore/RoleBench

setting your output directory from every .py file.

2.running role_profile_ge.py
example:Abraham Lincoln
This file is used to generate role profile.

3.running question_answer_ge.py
example:Abraham Lincoln
This file is used to generate a given question and answer.
In this section,user should give the topic and sentiment.Then , gpt-3.5 will generate one question based on the role_profile and topic and reply with the given sentiment.

4.running rolebench_sentiment.py
This file is used to analyse the given dialogues(multi-numbers) how about the role's sentiment(emotion).

