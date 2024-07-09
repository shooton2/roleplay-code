# roleplay-code

1.previous step:

We use qwen2-7b-instruct model to generate role profile , multi round dialogue with sentiment and topic. 
Download RoleBench datasets and qwen model from huggingface.

https://huggingface.co/datasets/ZenMoore/RoleBench

setting your output directory from every .py file.

2.running role_profile_ge.py

example:Abraham Lincoln
This file is used to generate role profile.

3.running qa_answer_qwen_eng.py

example:Abraham Lincoln

This file is used to talking about the given question.
In this section,user should give the topic and sentiment.Then , qwen model will generate one question based on the role_profile and topic and reply with the given sentiment.
Then the model will generate multi round dialogue.

4.running rolebench_sentiment.py

This file is used to analyse the given dialogues(multi-numbers) how about the role's sentiment(emotion).

5.count_rolebench.py

record the number of dialogues.

