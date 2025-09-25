import os
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "2"
import json
import re
from transformers import AutoTokenizer
from transformers import logging
logging.set_verbosity_error()
import torch
from tqdm import tqdm
import sys
from collections import Counter
from transformers import logging
import os
# import requests
from vllm import LLM, SamplingParams
...
logging.set_verbosity_error()



# Specify your Qwen model path and name

MODEL_NAME = "Qwen2.5-14B-Instruct" # Qwen2.5-14B-Instruct  Phi-4
PROMPT_STRATEGY = 'input_sum_keywords_direct'
DATASET = 'NYT29'


val_file_name = input("Please enter the validation file name (without extension): ").strip()

MODEL_PATH = "../../../models/" + MODEL_NAME
TOKENIZER_PATH = "../../../models/" + MODEL_NAME


# ---- vLLM initialization (replace HTTP server usage) ----
# Prefer fast tokenizer; fall back to slow if tokenizer.json is incompatible
try:
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH, trust_remote_code=True)
except Exception:
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH, trust_remote_code=True, use_fast=False)

llm = LLM(
    model=MODEL_PATH,
    tokenizer=TOKENIZER_PATH,
    trust_remote_code=True,
    dtype="float16",          # Uses slightly less memory than bf16
    tensor_parallel_size=1,
    pipeline_parallel_size=1,
    max_model_len=1024,       # Start conservatively; increase gradually once it runs successfully
    kv_cache_dtype="fp8",
    gpu_memory_utilization=0.80,
    swap_space=8,             # Enable CPU swap space (GB)
)


# ---- vLLM chat templating & batch generation ----
def build_chat_prompt(user_text: str) -> str:
    messages = [{"role": "user", "content": user_text}]
    return tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=False
    )

def ask_llama_batch(messages):
    """
    messages: list[str] — already constructed pure user texts with prompt_set()
    Returns: list[(full_content, last_answer)]
    """
    prompts = [build_chat_prompt(m) for m in messages]

    sampling_params = SamplingParams(
        temperature=0.0,
        top_p=1.0,
        max_tokens=400 if PROMPT_STRATEGY == 'input_sum_direct' or PROMPT_STRATEGY == 'input_sum_keywords_direct' else \
        5 if PROMPT_STRATEGY == 'input_nosum_direct' else \
        500,
        stop_token_ids=[tokenizer.eos_token_id] if tokenizer.eos_token_id is not None else None,
    )

    outputs = llm.generate(prompts, sampling_params)
    results = []
    for out in outputs:
        text = out.outputs[0].text.strip()

        # Reuse original Yes/No extraction logic (searching backwards for the first Yes/No)
        last_answer = None
        for line in reversed(text.strip().splitlines()):
            line = line.strip()
            if not line:
                continue
            for word in reversed(line.split()):
                if word.lower() in ['yes', 'no']:
                    last_answer = word.capitalize()
                    break
            if last_answer is not None:
                break
        if last_answer is None:
            if 'yes' in text.lower():
                last_answer = 'Yes'
            elif 'no' in text.lower():
                last_answer = 'No'

        results.append((text, last_answer))
    return results


def load_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [json.loads(line) for line in file]

def save_jsonl(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for item in data:
            file.write(json.dumps(item) + '\n')


def evaluation(val_file_name):
    # input file
    val_file_path = input("Please enter the path to the validation JSONL file: ").strip()
    val_data = load_jsonl(val_file_path)

    # output file
    dir_path = input("Please enter the output directory for results: ").strip()
    if not dir_path.endswith('/'):
        dir_path += '/'
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    incremental_file = dir_path + val_file_name + '.jsonl'
    # if incremental_file doesn't exist, create it
    if not os.path.exists(incremental_file):
        with open(incremental_file, 'w') as f:
            pass
    current_result = load_jsonl(incremental_file)
    RESUME_ID = current_result[-1]['id'] + 1 if current_result else 0
    print(f"Resuming from ID {RESUME_ID}")
    id = RESUME_ID

    for i in tqdm(range(RESUME_ID, len(val_data), 5)):      # Step size = 5
        batch_items = val_data[i:i+5]         # Take 5 items (last batch may have fewer)
        batch_messages = []
        for item in batch_items:
            batch_messages.append(item['prompt'])
        
        batch_outputs = ask_llama_batch(batch_messages)
        for (content, answer), item in zip(batch_outputs, batch_items):
            with open(incremental_file, "a") as tmp_f:
                json.dump({
                    "id": id,
                    "ground_truth": item['label'],
                    "answer": answer,
                    "content": content,
                    "paraphrased_sentence_subject" : item['paraphrased_sentence_subject'],
                    "paraphrased_sentence_object" : item['paraphrased_sentence_object'],
                    "test_sentence_subject" : item['test_sentence_subject'],
                    "test_sentence_object" : item['test_sentence_object'],
                    "ss_relation": item["ss_relation"],
                    "ts_relation": item["ts_relation"],
                    "paraphrased_sentence": item["paraphrased_sentence"],
                    "test_sentence": item["test_sentence"],
                }, tmp_f)
                tmp_f.write("\n")
            id += 1



if __name__ == '__main__':
    evaluation(val_file_name)