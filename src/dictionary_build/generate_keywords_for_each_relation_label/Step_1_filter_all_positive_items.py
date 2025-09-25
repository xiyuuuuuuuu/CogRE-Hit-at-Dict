import json

def read_data(path):
    """
    Read the data from the jsonl file.
    """
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            example = json.loads(line)
            data.append(example)
    return data

def write_to_jsonl(data, path):
    """
    Write the data to the jsonl file.
    """
    with open(path, "w", encoding="utf-8") as f:
        for example in data:
            json.dump(example, f, ensure_ascii=False)
            f.write("\n")

def filter_positive_items(data):
    """
    Filter all the positive items.
    """
    positive_data = [item for item in data if item['label']=='Yes']
    return positive_data



def main():
    input_file = input("Please enter the path to the input JSONL file: ").strip()
    original_data = read_data(input_file)
    positive_data = filter_positive_items(original_data)
    print(f"Total items: {len(original_data)}, Positive items: {len(positive_data)}")
    output_file = input("Please enter the path to save the positive items JSONL file: ").strip()
    write_to_jsonl(positive_data, output_file)


if __name__ == "__main__":
    main()
