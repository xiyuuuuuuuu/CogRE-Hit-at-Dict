import json
import os
import time


def read_data(path):
    """
    Read the data from the jsonl file.
    """
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                example = json.loads(line)
                data.append(example)
            except json.JSONDecodeError as e:
                print(f"[JSONL Parse Error] line {idx}: {e}")
    return data

def write_to_jsonl(data, path):
    """
    Write the data to the jsonl file.
    """
    with open(path, "w", encoding="utf-8") as f:
        for example in data:
            json.dump(example, f, ensure_ascii=False)
            f.write("\n")



"""
OpenAI/compatible API call
"""
from openai import OpenAI


def ask_openai(
    message: str,
    *,
    max_tokens: int = 1500,
    temperature: float = 0.0,
    retries: int = 3,
    backoff: float = 1.5,
    timeout_sec: float = 60.0,
) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable")

    base_url = os.getenv("OPENAI_BASE_URL", "")
    model_name = os.getenv("OPENAI_MODEL", "MODEL_NAME")

    client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout_sec) if base_url else OpenAI(api_key=api_key, timeout=timeout_sec)

    last_err = None
    for attempt in range(1, retries + 1):
        try:
            if len(message) > 12000:
                print(f"[Warn] prompt is very long: {len(message)} chars")
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": message}],
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout_sec,
            )
            content = response.choices[0].message.content or ""
            return content.strip()
        except Exception as e:
            last_err = e
            # Simple backoff retry
            if attempt < retries:
                time.sleep(backoff ** attempt)
            else:
                print(f"[OpenAI API Error] {e}")
    return "Unknown"

def main():
    input_file = input("Please enter the path to the input JSONL file: ").strip()
    output_file = input("Please enter the path to save the output JSONL file (or leave empty to skip saving): ").strip()
    output_file = output_file if output_file else None

    prompts = read_data(input_file)
    results = []

    # To test with only one example, change to prompts[:1]
    for item in prompts[0:1]:
        prompt = item.get("prompt")
        if not isinstance(prompt, str):
            # Skip invalid or missing data entries
            continue
        answer = ask_openai(prompt)
        results.append({"prompt": prompt, "answer": answer})
        print(prompt)
        print(answer)

    if output_file:
        # Set a path here if you want to save results to file
        write_to_jsonl(results, output_file)

if __name__ == "__main__":
    main()

    
