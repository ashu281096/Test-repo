from zipfile import ZipFile

import gradio as gr

import os
import shutil



def zip_files2(files):
    print(111)
    path = "/data/gradio_files/zip_files/"
    for idx, file in enumerate(files):
        shutil.copyfile(file.name, path+"gpu.py")
    return files[0]

demo = gr.Interface(zip_files2, gr.Files(file_count="multiple", file_types=[".zip", "zip", ".csv",".zip"]), "file",allow_flagging="never")


demo.launch(share=True,server_port=8091,show_error=True)

