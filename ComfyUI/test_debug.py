import os
import requests
import json
import subprocess
import time
import folder_paths
import pytest

def get_most_recent_image_file():
    output_dir = folder_paths.get_output_directory()
    files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
        
    if files:
        return max(files, key=os.path.getctime)
    return None

def generate_json(model_name,prompt_text):
    return json.loads('{"client_id":"123","number":0,"prompt":{"3":{"inputs":{"seed":0,"steps":20,"cfg":8,"sampler_name":"euler","scheduler":"normal","denoise":1,"model":["4",0],"positive":["6",0],"negative":["7",0],"latent_image":["5",0]},"class_type":"KSampler","_meta":{"title":"KSampler"}},"4":{"inputs":{"ckpt_name":"' + model_name + '"},"class_type":"CheckpointLoaderSimple","_meta":{"title":"Load Checkpoint"}},"5":{"inputs":{"width":512,"height":512,"batch_size":1},"class_type":"EmptyLatentImage","_meta":{"title":"Empty Latent Image"}},"6":{"inputs":{"text":"'+prompt_text+'","clip":["4",1]},"class_type":"CLIPTextEncode","_meta":{"title":"CLIP Text Encode (Prompt)"}},"7":{"inputs":{"text":"text, watermark","clip":["4",1]},"class_type":"CLIPTextEncode","_meta":{"title":"CLIP Text Encode (Prompt)"}},"8":{"inputs":{"samples":["3",0],"vae":["4",2]},"class_type":"VAEDecode","_meta":{"title":"VAE Decode"}},"9":{"inputs":{"filename_prefix":"ComfyUI","images":["8",0]},"class_type":"SaveImage","_meta":{"title":"Save Image"}}},"extra_data":{"extra_pnginfo":{"workflow":{"id":"","revision":0,"last_node_id":9,"last_link_id":9,"nodes":[{"id":7,"type":"CLIPTextEncode","pos":[413,389],"size":[425.27801513671875,180.6060791015625],"flags":{},"order":3,"mode":0,"inputs":[{"name":"clip","type":"CLIP","link":5}],"outputs":[{"name":"CONDITIONING","type":"CONDITIONING","slot_index":0,"links":[6]}],"properties":{"Node name for S&R":"CLIPTextEncode"},"widgets_values":["text, watermark"]},{"id":6,"type":"CLIPTextEncode","pos":[415,186],"size":[422.84503173828125,164.31304931640625],"flags":{},"order":2,"mode":0,"inputs":[{"name":"clip","type":"CLIP","link":3}],"outputs":[{"name":"CONDITIONING","type":"CONDITIONING","slot_index":0,"links":[4]}],"properties":{"Node name for S&R":"CLIPTextEncode"},"widgets_values":["beautiful scenery nature glass bottle landscape, , purple galaxy bottle,"]},{"id":5,"type":"EmptyLatentImage","pos":[473,609],"size":[315,106],"flags":{},"order":0,"mode":0,"inputs":[],"outputs":[{"name":"LATENT","type":"LATENT","slot_index":0,"links":[2]}],"properties":{"Node name for S&R":"EmptyLatentImage"},"widgets_values":[512,512,1]},{"id":8,"type":"VAEDecode","pos":[1209,188],"size":[210,46],"flags":{},"order":5,"mode":0,"inputs":[{"name":"samples","type":"LATENT","link":7},{"name":"vae","type":"VAE","link":8}],"outputs":[{"name":"IMAGE","type":"IMAGE","slot_index":0,"links":[9]}],"properties":{"Node name for S&R":"VAEDecode"},"widgets_values":[]},{"id":9,"type":"SaveImage","pos":[1451,189],"size":[210,58],"flags":{},"order":6,"mode":0,"inputs":[{"name":"images","type":"IMAGE","link":9}],"outputs":[],"properties":{},"widgets_values":["ComfyUI"]},{"id":4,"type":"CheckpointLoaderSimple","pos":[26,474],"size":[315,98],"flags":{},"order":1,"mode":0,"inputs":[],"outputs":[{"name":"MODEL","type":"MODEL","slot_index":0,"links":[1]},{"name":"CLIP","type":"CLIP","slot_index":1,"links":[3,5]},{"name":"VAE","type":"VAE","slot_index":2,"links":[8]}],"properties":{"Node name for S&R":"CheckpointLoaderSimple"},"widgets_values":["v15PrunedEmaonly_v15PrunedEmaonly.safetensors"]},{"id":3,"type":"KSampler","pos":[863,186],"size":[315,262],"flags":{},"order":4,"mode":0,"inputs":[{"name":"model","type":"MODEL","link":1},{"name":"positive","type":"CONDITIONING","link":4},{"name":"negative","type":"CONDITIONING","link":6},{"name":"latent_image","type":"LATENT","link":2}],"outputs":[{"name":"LATENT","type":"LATENT","slot_index":0,"links":[7]}],"properties":{"Node name for S&R":"KSampler"},"widgets_values":[0,"fixed",20,8,"euler","normal",1]}],"links":[[1,4,0,3,0,"MODEL"],[2,5,0,3,3,"LATENT"],[3,4,1,6,0,"CLIP"],[4,6,0,3,1,"CONDITIONING"],[5,4,1,7,0,"CLIP"],[6,7,0,3,2,"CONDITIONING"],[7,3,0,8,0,"LATENT"],[8,4,2,8,1,"VAE"],[9,8,0,9,0,"IMAGE"]],"groups":[],"config":{},"extra":{"ds":{"scale":0.9090909090909091,"offset":[36.85460937500025,-29.51679687500001]},"frontendVersion":"1.24.1"},"version":0.4}}}}')

def test_run_bash_script():
    result = subprocess.Popen(["python",'main.py'])
    # Wait 10 seconds for the service to come up.
    time.sleep(10)
    match_result = []

    try:
        model = 'v1-5-pruned-emaonly-fp16.safetensors'
        prompt_text = 'asdf'
        gen_sleep_time = 20
        json_content = generate_json(model_name=model,prompt_text=prompt_text)
        response = requests.post("http://localhost:8188/api/prompt", json=json_content)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        
        print("Initial POST request successful!")
        print("Response:", response.text)  # Print the response content
        # Wait gen_sleep_time seconds for this to generate...
        time.sleep(gen_sleep_time)
        # Alter the image
        file_name = get_most_recent_image_file()
        with open(file_name,'wb') as file:
            print(f'altering the existing image : {file_name}')
            file.write(b'\x00')
            file.flush()

        response = requests.get('http://localhost:8188/debug/reproduce')
        
        # Wait another gen_sleep_time seconds for this to generate...
        time.sleep(gen_sleep_time)
        print("Reproduce call successful!")
        match_result = response.json()
    except Exception as e:
        print("Error during POST request:", e)
    finally:
        result.kill()
    assert match_result['match'] == False