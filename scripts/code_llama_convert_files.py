import config, csv
import os,time
import gradio as gr
import sys
import re
import torch
import json,stat,datetime,ast,pdb
from transformers import pipeline
import logging

log_file_path = "/data/code_convert/logs/code_convert.log"
logging.basicConfig(filename=log_file_path,filemode="a",level=logging.DEBUG,format='%(asctime)s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
logging.info("***************** Starting Code Convert Script **********************")
error_code_snippets = []

sas_code_keyword_pairs = [
        ("macro","mend"),
        ("proc sql","quit"),
        ("proc means","run"),
        ("proc rank","run"),
        ("proc freq","run"),
        ("proc transpose","run"),
        ("proc delete","run"),
        ("proc append","run"),
        ("proc sort","run"),
        ("PROC CONTENTS","RUN"),
        ("data","run"),
        ("proc import","run"),
        ("proc export","run"),
        ("proc format","quit"),
        ("proc datasets","quit"),
        ("proc logistic","run"),
        ("proc reg","quit"),
        ("proc glm","quit"),
        ("proc print","run"),
        ("proc report","run")
]
os.environ['TRANSFORMERS_CACHE']='/data/cache/'
#pipe = pipeline("text-generation", model="HuggingFaceH4/starchat-beta", torch_dtype=torch.bfloat16, device_map="auto")
pipe = pipeline("text-generation", model="/data/cache/models--codellama--CodeLlama-34b-Instruct-hf/snapshots/cebb11eacbeecb9189e910d57a8faeadb949978f/", torch_dtype=torch.bfloat16, device_map="auto")

def ensure_directory_path_exists(directory_path):
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            os.chmod(directory_path,stat.S_IRWXU)
            logging.info("Created directory path: %s"%(directory_path))
    except Exception as e:
        logging.info("Error in creating directory path")


def preprocess_sas_code(code_string):
    try:
        code_chunks = [] 
        pattern = re.compile('|'.join(fr'\b{re.escape(start)}\b(.*?)\b{re.escape(end)}\b.*?;' for start,end in sas_code_keyword_pairs),re.IGNORECASE|re.DOTALL)
        
        matches = pattern.finditer(code_string)
        
        for match in matches:
            #start_keyword = next((kw[0].upper() for kw in sas_code_keyword_pairs if kw[0].upper() in match.group()),None)
            #end_keyword = next((kw[1].upper() for kw in sas_code_keyword_pairs if kw[1].upper() in match.group()),None)
            code_chunks.append((match.group(0)))
        return code_chunks
    except:
        logging.info("Error in generating SAS code chunks for the code string: %s"%(code_string))

def generate_dynamic_prompt(chunk):
    '''if 'proc_sql' in chunk:
        return "Please convert the following SAS PROC SQL query into an equivalent Python script using Pandas.The goal is to perform the same data selection and aggregation in Python as this SAS query \n" + chunk
    elif 'proc frequency' in chunk:
        return "Translate this SAS frequency procedure into Python using Pandas \n" + chunk
    else:
        return "Translate this SAS code to Python code \n" + chunk'''
    try:
        logging.info("Entered generate dynamic prompt function")
        return "Convert the below SAS code to Python code using Pandas library \n" + chunk
    except:
        logging.info("Error in generate dynamic prompt function")


def convert_sas_python(message):
    try:
        logging.info("Inside convert SAS Python try block")
        #prompt_template = "<|system|>\n<|end|>\n<|user|>\n{query}<|end|>\n<|assistant|>"
        #prompt = prompt_template.format(query=message)
        prompt_template = "<s>[INST] \n  {query} \n [/INST]"
        prompt = prompt_template.format(query=message)

    except:
            logging.info("Error in setting up LLM parameters.Error is :%S"%(e))
    try:
        try:
            #outputs = pipe(prompt,max_new_tokens=16512,do_sample=True,temperature=0.2,top_k=50,top_p=0.95,eos_token_id=49155)
            #output_code = outputs[0]["generated_text"].split("<|assistant|>")[1]
            outputs = pipe(prompt,max_new_tokens=3000,do_sample=True,temperature=0.1,top_k=50,top_p=0.9)
            output_code = outputs[0]["generated_text"].split(message)[1]
            logging.info("LLM output generated successfully")
        except RuntimeError  as e:
            if "The size of tensor a (8192) must match the size of tensor b (8193) at non-singleton dimension 2" in str(e):
                logging.info("Inside convert SAS Python except block rerunning the code")
                outputs = pipe(prompt,max_new_tokens=4000,do_sample=True,temperature=0.1,top_k=50,top_p=0.9)
                output_code = outputs[0]["generated_text"].split(message)[1]
                logging.info("LLM output generated successfully after rerunning the code")
    except Exception as e:
            print("Error in LLM output. Error is %s"%(e))
    return output_code


def archive_processed_code(archive_dir,chunk_base_name,chunk_dir,extension):
    ensure_directory_path_exists(archive_dir)
    try:
        for base_name in chunk_base_name:
            original_file_path = os.path.join(chunk_dir,base_name + '.' + extension)
            archived_file_path = os.path.join(archive_dir,base_name + '.' + extension)
            if os.path.exists(original_file_path):
                os.rename(original_file_path,archived_file_path)
        logging.info("Successfully archived processed code chunks")
    except Exception as e:
        logging.info("Error in archiving code chunks. Error is %s"%(e))


        #ensure_directory_path_exists(path)


def process_code_snippet(country_dir, input_dir, code_snippet):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    preprocessed_dir = os.path.join(country_dir, 'preprocessed', code_snippet)
    postprocessed_dir = os.path.join(country_dir, 'postprocessed', code_snippet)
    preprocessed_chunks_dir = os.path.join(country_dir, 'preprocessed', code_snippet, 'chunks')
    postprocessed_chunks_dir = os.path.join(country_dir, 'postprocessed', code_snippet, 'chunks')
    preprocessed_archive_dir = os.path.join(country_dir, 'preprocessed', code_snippet, 'archive', timestamp)
    postprocessed_archive_dir = os.path.join(country_dir, 'postprocessed', code_snippet, 'archive', timestamp)
    global error_code_snippets

    if code_snippet.endswith('.sas'):
        output_file_python = code_snippet.replace('.sas', '.py')
        output_file_path = os.path.join(country_dir, 'output', output_file_python)

    for path in [preprocessed_dir, postprocessed_dir, preprocessed_chunks_dir, postprocessed_chunks_dir,
                 preprocessed_archive_dir, postprocessed_archive_dir]:
        ensure_directory_path_exists(path)
    if not code_snippet.endswith('.sas'):
        code_snippet += '.sas'

    file_path = os.path.join(input_dir,code_snippet)
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
            sas_code_string = file.read()
    except Exception as e:
        logging.info("Error in reading input SAS code file:%s" % (code_snippet))
        logging.info("Error is :%s" % (e))
        error_code_snippets.append(code_snippet)
    """try:
        code_chunks = preprocess_sas_code(sas_code_string)
    except Exception as e:
        logging.info("Error in preprocessing sas codes:%s" % (code_snippet))
        logging.info("Error is :%s" % (e))
        error_code_snippets.append(code_snippet)

    try:
        #combined_code_chunks = combine_code_chunks(code_chunks)
        combined_code_chunks = code_chunks
    except Exception as e:
        logging.info("Error in combining sas code chunks:%s" % (code_snippet))
        logging.info("Error is :%s" % (e))
        error_code_snippets.append(code_snippet)

    for i, chunk in enumerate(combined_code_chunks):
        logging.info("Starting code processing for chunk: %s in code snippet:%s" % (i, code_snippet))
        try:
            chunk_with_prompt = generate_dynamic_prompt(chunk)
        except:
            logging.info("Error in generating dynamic prompt")
        chunk_file_path = os.path.join(preprocessed_chunks_dir, f'chunk_{i}.sas')
        with open(chunk_file_path, 'w', encoding='utf-8', errors='replace') as chunk_file:
            chunk_file.write(chunk_with_prompt)

        time.sleep(2)
        try:
            logging.info("Calling LLM model try block")
            converted_chunk = convert_sas_python(chunk_with_prompt)
        except Exception as e:
            error_code_snippets.append(code_snippet)
            logging.info("Error in combining sas code chunks:%s in enumerate" % (code_snippet))
            logging.info("Error is :%s" % (e))

        converted_chunk_path = os.path.join(postprocessed_chunks_dir, f'chunk_{i}.py')

        with open(converted_chunk_path, 'w', encoding='utf-8', errors='replace') as converted_file:
            converted_file.write(converted_chunk)
        try:
            pattern = r'```(?:python)?\s*(.*?)\s*```'
            match = re.search(pattern, converted_chunk, re.DOTALL)
            if match:
                with open(output_file_path, "a", encoding='utf-8', errors='replace') as output_file:
                    output_file.write(match.group(1))
                    output_file.write("/n/n")
            # print("processing done for :", chunk)
        except Exception as e:
            error_code_snippets.append(code_snippet)
            logging.info("Error in writing output file:%s" % (code_snippet))
            logging.info("Error is :%s" % (e))
    archive_processed_code(preprocessed_archive_dir, [f'chunk_{i}' for i in range(len(code_chunks))],
                           preprocessed_chunks_dir, 'sas')
    archive_processed_code(postprocessed_archive_dir, [f'chunk_{i}' for i in range(len(code_chunks))],
                           postprocessed_chunks_dir, 'py')

    logging.info("Successfully archived processed code chunks")"""

    prompt = "Convert the below SAS code to Python code using Pandas library"
    sas_code_string = prompt + "\n" + sas_code_string
    try:
        logging.info("Calling LLM model try block")
        converted_python_code = convert_sas_python(sas_code_string)
    except Exception as e:
        error_code_snippets.append(code_snippet)
        logging.info("Error in combining sas code chunks:%s in enumerate" % (code_snippet))
        logging.info("Error is :%s" % (e))
    try:
        pattern = r'```(?:python)?\s*(.*?)\s*```'
        match = re.search(pattern, converted_python_code, re.DOTALL)
        if match:
            with open(output_file_path,"a",encoding='utf-8', errors='replace') as output_file:
                output_file.write(match.group(1))
                output_file.write("/n/n")
        logging.info("processing done for :%s"%(code_snippet))
    except Exception as e:
        error_code_snippets.append(code_snippet)
        logging.info("Error in writing output file:%s" % (code_snippet))
        logging.info("Error is :%s" % (e))

def main():
    start_time = time.time()
    success_code_snippets = []
    project_dir = "/data/code_convert"

    if sys.argv and len(sys.argv)>1:
        country_name = sys.argv[1]
    else:
        country_name = "not_applicable"
    
    if sys.argv and len(sys.argv)>2:
        user_name = sys.argv[2]
    else:
        user_name = "not_applicable"

    country_dir = os.path.join(project_dir, country_name)
    input_dir = os.path.join(country_dir, "input")
    input_dir = os.path.join(input_dir, "small_files")
    global error_code_snippets
    for code_snippet in os.listdir(input_dir):
        try:
            print(code_snippet)
            process_code_snippet(country_dir, input_dir, code_snippet)
            if code_snippet not in error_code_snippets:
                success_code_snippets.append(code_snippet)
                if os.path.isfile(os.path.join(input_dir, code_snippet)):
                    os.remove(os.path.join(input_dir, code_snippet))
                    logging.info("Processed input files are deleted")
                    logging.info("processing code snippet completed:%s" % (code_snippet))
                else:
                    logging.info(error_code_snippets)
        except:
            logging.info("Error in processing code snippet:%s" % (code_snippet))

    success_code_snippets = list(set(success_code_snippets))
    error_code_snippets = list(set(error_code_snippets))
    logging.info("******Logging Code Conversion Files for country:%s and user:%s*****"%(country_name,user_name))
    logging.info(success_code_snippets)
    logging.info("Successfully processed code snippets:%s" % (len(success_code_snippets)))
    logging.info("***********")
    logging.info(error_code_snippets)
    logging.info("Error code snippets:%s" % (len(error_code_snippets)))
    logging.info("*******************************************************")
    
    #header = ["file_type", "ountry_name", "user_name", "success_codes", "num_success", "error_codes", "num_errors"]
    with open("/data/code_convert/logs/cc_run_summary_log.csv","a",encoding="utf-8") as summary_log:
        data = ["small",country_name,user_name,str(success_code_snippets),len(success_code_snippets),str(error_code_snippets),len(error_code_snippets)]
        writer = csv.writer(summary_log)
    #    writer.writerow(header)
        writer.writerow(data)
        """summary_log.write("\n")
        summary_log.write("************************************")
        summary_log.write("\n")
        summary_log.write("Code Conversion files script log for country:%s and user name:%s"%(country_name,user_name))
        summary_log.write("\n")
        summary_log.write(str(success_code_snippets))
        summary_log.write("\n")
        summary_log.write("Successfully processed code snippets:%s"%(len(success_code_snippets)))
        summary_log.write("\n")
        summary_log.write(str(error_code_snippets))
        summary_log.write("\n")
        summary_log.write("Error code snippets:%s"%(len(error_code_snippets)))
        summary_log.write("\n")
        summary_log.write("************************************")
        summary_log.write("\n")"""

    end_time = time.time()
    print(end_time - start_time, "ended")


if __name__ == "__main__":
    main()
