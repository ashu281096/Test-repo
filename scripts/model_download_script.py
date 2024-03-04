import torch
import os
os.environ['TRANSFORMERS_CACHE']='/data/cache/'
from transformers import pipeline
pipe = pipeline("text-generation", model="HuggingFaceH4/starchat-beta", torch_dtype=torch.bfloat16, device_map="auto")
