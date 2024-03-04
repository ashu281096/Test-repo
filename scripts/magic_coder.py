#/data/cache/models--HuggingFaceH4--starchat-beta/snapshots/b1bcda690655777373f57ea6614eb095ec2c886f

import torch
import os
os.environ['TRANSFORMERS_CACHE']='/data/cache/'
from transformers import pipeline
pipe = pipeline("text-generation", model="ise-uiuc/Magicoder-CL-7B", torch_dtype=torch.bfloat16, device_map="auto")

import time
t1= time.time()

prompt_template = "You are an intelligent coding assistant \n{query}"
prompt = prompt_template.format(query="How do I sort list in Python?")
print("before model start")
outputs = pipe(prompt,max_new_tokens=256,do_sample=True,temperature=0.2,top_k=50,top_p=0.95,eos_token_id=49155)
t2=time.time()

print(t2-t1)
print(outputs[0]["generated_text"].split("\n"))


