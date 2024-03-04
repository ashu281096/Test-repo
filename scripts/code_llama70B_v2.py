from transformers import AutoTokenizer,AutoModelForCausalLM
import transformers
import torch
import os



model_id = "/data/cache/models--codellama--CodeLlama-34b-Instruct-hf"
tokenizer =AutoTokenizer.from_pretrained(model_id)
#pipeline = transformers.pipeline("text-generation",model=model_id,tourch_dtype=torch.float16,device_map="auto")
model = AutoModelForCausalLM.from_pretrained(model_id,torch_dtype=torch.float16,device_map="auto")


