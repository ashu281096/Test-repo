#/data/cache/models--HuggingFaceH4--starchat-beta/snapshots/b1bcda690655777373f57ea6614eb095ec2c886f

import torch
import os
os.environ['TRANSFORMERS_CACHE']='/data/cache/'
from transformers import pipeline
pipe = pipeline("text-generation", model="codellama/CodeLlama-70b-Instruct-hf", torch_dtype=torch.bfloat16, device_map="auto")

import time
t1= time.time()
#prompt_template = "<|system|>\n<|end|>\n<|user|>\n{query}<|end|>\n<|assistant|>"
prompt_template = "<s>Source: system \n\n You are a expert coding assistant at SAS to Python Conversion <step> Source: user \n\n {query} "
prompt_template = "<s>Source: system \n\n You are a expert coding assistant at SAS to Python Conversion <step> Source: user \n\n {query} <step> Source:assitant \n Destination: user"
query = "Convert PROC FREQ of SAS to Python"
prompt = prompt_template.format(query=query)

#prompt_template = "{query}"
#prompt = prompt_template.format(query="Convert PROC FREQ of SAS to Python")
print("before model start")
outputs = pipe(prompt,max_new_tokens=1500,do_sample=True,temperature=0.3,top_k=50,top_p=0.9)
t2=time.time()

print(t2-t1)
print(outputs[0]["generated_text"].split(query)[1])


