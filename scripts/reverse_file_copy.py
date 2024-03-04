from zipfile import ZipFile

import gradio as gr

import os
import shutil



def zip_files3(files):
    return gr.File(files)

demo = gr.Interface(zip_files3,"text", "file",allow_flagging="never")


demo.launch(share=True,server_port=8092,show_error=True)

