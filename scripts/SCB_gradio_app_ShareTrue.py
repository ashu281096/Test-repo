import gradio as gr
import sys

import torch
import os

os.environ['TRANSFORMERS_CACHE']='/data/cache/'
from transformers import pipeline
#pipe1 = pipeline("text-generation", model="HuggingFaceH4/starchat-beta", torch_dtype=torch.bfloat16, device_map="auto")
pipe1 = pipeline("text-generation", model="HuggingFaceH4/starchat-beta", device_map="auto")

def echo(message,history):
        return message

def echo1(message,history):
        prompt_template1 = "<|system|>\n<|end|>\n<|user|>\n{query}<|end|>\n<|assistant|>"
        prompt1 = prompt_template1.format(query=message)
        outputs1 = pipe1(prompt1,max_new_tokens=16512,do_sample=True,temperature=0.2,top_k=50,top_p=0.95,eos_token_id=49155)
        return outputs1[0]["generated_text"].split("<|assistant|>")[1]


examples=["What's the meaning of life?", "How do you sort a list in Python?", "Code for CreditRisk Model in Python?", "How do I get current Date using Shell command?"]

image_path="/data/standard-chartered-bank-new-20211713.jpg"
cb_label=gr.Chatbot(label="SCB Code Buddy")
with gr.Blocks() as g_app:
    with gr.Row():
        gr.Image(image_path,show_label=False,show_download_button=False,scale=0,container=False)
        gr.Label("SCB Code Buddy",show_label=False,scale=1,container=False)
    gr.ChatInterface(fn=echo1,examples=examples,title="",chatbot=cb_label)
g_app.queue(concurrency_count=10)
g_app.launch(share=True,server_port=8093)
