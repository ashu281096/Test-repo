path= "/data/temp_scripts/Aius_pass_case.sas"
with open(path,"r",encoding="latin1") as file:
    file_details = file.read()
    print(file_details)

import gradio as gr
import sys

import torch
import os
import time
os.environ['TRANSFORMERS_CACHE']='/data/cache/'

from transformers import pipeline

pipe1 = pipeline("text-generation", model="codellama/CodeLlama-34b-Instruct-hf", torch_dtype=torch.bfloat16, device_map="auto")



def echo(message):
        prompt_template = "<s>[INST] \n  {query} \n [/INST]"
        query = message
        prompt1 = prompt_template.format(query=query)
        outputs1 = pipe1(prompt1,max_new_tokens=1100,do_sample=True,temperature=0.1,top_k=60,top_p=0.95)
        return outputs1[0]["generated_text"].split(message)[1]


t1 = time.time()
echo(file_details)
t2 = time.time()
print("Time taken to run the model was: ",t2-t1,"seconds")
