"""
Batch generate explanations/answers using local Qwen2.5-14B-Instruct with vLLM.
- Loads model/tokenizer locally (no HTTP)
- Uses tokenizer.apply_chat_template for chat formatting
- Batches prompts to llm.generate for speed
- Robust Yes/No extraction
"""

import os
import re
import json
from tqdm import tqdm
from collections import deque

# ------- Stable CUDA mapping (optional but recommended) -------
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
# Use only GPU 0; for multi-GPU, set tensor_parallel_size>1 and adjust visible devices accordingly
os.environ["CUDA_VISIBLE_DEVICES"] = "2"

# ------- Configs (edit to your environment) -------
MODEL_NAME = "Qwen2.5-14B-Instruct"
DATASET = "NYT29"

MODEL_PATH = input("Please enter the path to the model: ").strip()
TOKENIZER_PATH = input("Please enter the path to the tokenizer: ").strip()
INPUT_FILE = input("Please enter the path to the input JSONL file: ").strip()
OUT_DIR = input("Please enter the output directory: ").strip()
OUT_FILE = input("Please enter the output file name: ").strip()

BATCH_SIZE = 16                # Adjust according to available GPU memory
MAX_NEW_TOKENS = 500           # Prompt template is long with reasoning, reserve enough space
TEMPERATURE = 0.0
TOP_P = 1.0
MAX_MODEL_LEN = 2048           # 1024 may be too small; recommend 2k or higher (depends on memory/requirements)
GPU_MEM_UTIL = 0.80
KV_CACHE_DTYPE = "auto"        # "auto" is generally stable; fp8 depends on driver/hardware support

# ------- Prompt (consistent with your provided one) -------
input_sum_keywords_reasoning = """
You are given two sentences. Follow the three steps below to determine whether they express a similar relation.
---
Summarization: Focus on the main parts between subjects and objects in the sentences.
Summarization examples:

Summarize the relations between "Malcolm Peeler" and "“Pangburn”" in "Dr. Malcolm Peeler , grew in Pangburn, has continued the family tradition of practicing medicine in Jonesboro .".
Summarization: Malcolm Peeler came from Pangburn.

Summarize the relations between “Oceania” and "PECC" in "Oceania and the Western Hemisphere within the PECC region , as surplus food producers and exporters , confront unique consumer issues , such as lower food expenditure and higher caloric intake compared to Asia .".
Summarization: Oceania within region PECC.

Summarize the relations between "Global Climate Research Institute” and "GCRI" in "Climate change challenges remain a key concern at the annual summit. The outlook is concerning, according to the Global Climate Research Institute ( GCRI ), which coordinates the event each year.".
Summarization: Global Climate Research Institute is abbreviated as GCRI.

Summarize the relations between "Panasonic Corp" and "Tesla Inc" in "Tesla Inc. is a wholly-owned subsidiary of Panasonic Corp, focusing on energy storage solutions.".
Summarization: Panasonic Corp is a subsidiary of Tesla Inc.
---
Step 1: summarize the relations between "{paraphrased_sentence_subject}" and "{paraphrased_sentence_object}" in "{paraphrased_sentence}".
Label your result as: Relation_Summarization_1.

Step 2: summarize the relations between "{test_sentence_subject}" and "{test_sentence_object}" in "{test_sentence}".
Label your result as: Relation_Summarization_2.

Step 3: are the relations between "{paraphrased_sentence_subject}" and "{paraphrased_sentence_object}" in Relation_Summarization_1 and between "{test_sentence_subject}" and "{test_sentence_object}" in Relation_Summarization_2 similar? Focus on the keywords in the Relation_Summarization_1 an Relation_Summarization_2 that convey relations.
Generate the understanding process, followed by Yes or No in a separate line.
"""

def prompt_set(paraphrased_sentence, test_sentence,
               paraphrased_sentence_subject, paraphrased_sentence_object,
               test_sentence_subject, test_sentence_object):
    return input_sum_keywords_reasoning.format(
        paraphrased_sentence=paraphrased_sentence,
        test_sentence=test_sentence,
        paraphrased_sentence_subject=paraphrased_sentence_subject,
        paraphrased_sentence_object=paraphrased_sentence_object,
        test_sentence_subject=test_sentence_subject,
        test_sentence_object=test_sentence_object,
    )

# ------- IO helpers -------
def read_data(path):
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def ensure_dir(p):
    if not os.path.exists(p):
        os.makedirs(p)

# ------- vLLM + tokenizer -------
from transformers import AutoTokenizer
import torch
from vllm import LLM, SamplingParams

def load_tokenizer():
    try:
        tok = AutoTokenizer.from_pretrained(TOKENIZER_PATH, trust_remote_code=True)
    except Exception:
        tok = AutoTokenizer.from_pretrained(TOKENIZER_PATH, trust_remote_code=True, use_fast=False)
    return tok

def cuda_probe():
    print(f"CUDA_VISIBLE_DEVICES: {os.environ.get('CUDA_VISIBLE_DEVICES')}")
    try:
        if torch.cuda.is_available():
            print(f"torch sees {torch.cuda.device_count()} CUDA device(s)")
            print(f"torch current device: cuda:{torch.cuda.current_device()}")
            print(f"torch device 0 name: {torch.cuda.get_device_name(0)}")
        else:
            print("CUDA not available according to torch")
    except Exception as e:
        print(f"CUDA probe failed: {e}")

def load_llm():
    llm = LLM(
        model=MODEL_PATH,
        tokenizer=TOKENIZER_PATH,
        trust_remote_code=True,
        dtype="float16",
        tensor_parallel_size=1,
        pipeline_parallel_size=1,
        max_model_len=MAX_MODEL_LEN,
        kv_cache_dtype=KV_CACHE_DTYPE,
        gpu_memory_utilization=GPU_MEM_UTIL,
        swap_space=8,   # GB
    )
    return llm

# ------- chat templating -------
def build_chat_prompt(tokenizer, user_text: str) -> str:
    messages = [{"role": "user", "content": user_text}]
    return tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=False
    )

# ------- robust Yes/No extraction -------
YESNO_REGEX = re.compile(r"\b(yes|no)\b", flags=re.IGNORECASE)

def extract_yes_no(text: str):
    matches = list(YESNO_REGEX.finditer(text))
    if not matches:
        return None
    return matches[-1].group(1).capitalize()

# ------- batch ask -------
def ask_llama_batch(llm, tokenizer, messages, max_new_tokens=MAX_NEW_TOKENS):
    """
    messages: list[str] — constructed user texts with prompt_set()
    Returns: list[(full_content, last_answer)]
    """
    prompts = [build_chat_prompt(tokenizer, m) for m in messages]
    sampling_params = SamplingParams(
        temperature=TEMPERATURE,
        top_p=TOP_P,
        max_tokens=max_new_tokens,
        # Usually no need to set stop_token_ids to avoid early cutoff; if issues arise, you can add tokenizer.eos_token_id
        # stop_token_ids=[tokenizer.eos_token_id] if tokenizer.eos_token_id is not None else None,
    )
    outputs = llm.generate(prompts, sampling_params)
    results = []
    for out in outputs:
        text = out.outputs[0].text.strip()
        last_answer = extract_yes_no(text)
        results.append((text, last_answer))
    return results

# ------- main generate loop (batched) -------
def llms_generate_explanations_batch(input_items, tokenizer, llm,
                                     out_path,
                                     batch_size=BATCH_SIZE):
    ensure_dir(os.path.dirname(out_path))
    # Use append mode so it can be interrupted and resumed
    with open(out_path, "a", encoding="utf-8") as tmp_f:
        # Use deque to form batches
        q = deque(input_items)
        pbar = tqdm(total=len(input_items), desc="Generating", ncols=100)
        while q:
            batch = []
            idxs = []   # record original indices for debugging/alignment
            for _ in range(min(batch_size, len(q))):
                item = q.popleft()
                batch.append(item)
            # Construct prompts
            user_texts = [
                prompt_set(
                    it['paraphrased_sentence'],
                    it['test_sentence'],
                    it['paraphrased_sentence_subject'],
                    it['paraphrased_sentence_object'],
                    it['test_sentence_subject'],
                    it['test_sentence_object'],
                )
                for it in batch
            ]
            # Batch generation
            try:
                batch_out = ask_llama_batch(llm, tokenizer, user_texts, MAX_NEW_TOKENS)
            except Exception as e:
                # If batch fails, fallback to single-item generation
                print(f"[BatchError] {e} — falling back to per-item generation for this batch.")
                batch_out = []
                for ut in user_texts:
                    try:
                        one = ask_llama_batch(llm, tokenizer, [ut], MAX_NEW_TOKENS)[0]
                    except Exception as e2:
                        print(f"[ItemError] {e2}")
                        one = ("", None)
                    batch_out.append(one)

            # Write results to file
            for it, (content, answer) in zip(batch, batch_out):
                try:
                    record = {
                        "ground_truth": it.get("label", None),
                        "answer": answer,
                        "content": content,
                        "paraphrased_sentence_subject": it['paraphrased_sentence_subject'],
                        "paraphrased_sentence_object": it['paraphrased_sentence_object'],
                        "test_sentence_subject": it['test_sentence_subject'],
                        "test_sentence_object": it['test_sentence_object'],
                        "ss_relation": it["ss_relation"],
                        "ts_relation": it["ts_relation"],
                        "paraphrased_sentence": it["paraphrased_sentence"],
                        "test_sentence": it["test_sentence"],
                    }
                    json.dump(record, tmp_f, ensure_ascii=False)
                    tmp_f.write("\n")
                except Exception as e:
                    print(f"[WriteError] {e}\nProblematic item: {it}")
                pbar.update(1)
        pbar.close()

def main():
    # Basic diagnostics
    cuda_probe()

    # Load tokenizer & llm
    tokenizer = load_tokenizer()
    llm = load_llm()

    # One-time warmup (trigger kernel initialization, CUDA graph capture, etc.)
    try:
        print("Running one-time warmup...", flush=True)
        _ = llm.generate(
            [build_chat_prompt(tokenizer, "Hello")],
            SamplingParams(max_tokens=1, temperature=0.0)
        )
        print("Warmup done.", flush=True)
    except Exception as e:
        print(f"Warmup failed (non-fatal): {e}")

    # Load input data
    data = read_data(INPUT_FILE)
    print(f"Loaded {len(data)} items from {INPUT_FILE}")

    # Batch generate and save
    out_path = os.path.join(OUT_DIR, OUT_FILE)
    llms_generate_explanations_batch(
        input_items=data,
        tokenizer=tokenizer,
        llm=llm,
        out_path=out_path,
        batch_size=BATCH_SIZE
    )
    print(f"Done. Results appended to: {out_path}")

if __name__ == "__main__":
    main()