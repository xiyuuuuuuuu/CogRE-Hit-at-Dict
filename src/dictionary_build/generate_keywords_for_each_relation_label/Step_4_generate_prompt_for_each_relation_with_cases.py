import json

prompt_template_1 = """
Relation: {relation}
Please extract the words or phrases that indicate trigger words or relation summaries from the following answers; the relation is {relation}.
Output a string list contain all the words.
output_case_1:
{content_1}
paraphrased_sentence: {paraphrased_sentence_1}
test_sentence: {test_sentence_1}

output_case_2:
{content_2}
paraphrased_sentence: {paraphrased_sentence_2}
test_sentence: {test_sentence_2}

output_case_3:
{content_3}
paraphrased_sentence: {paraphrased_sentence_3}
test_sentence: {test_sentence_3}

output_case_4:
{content_4}
paraphrased_sentence: {paraphrased_sentence_4}
test_sentence: {test_sentence_4}
"""

prompt_template_2 = """
Relation: {relation}
Please extract the words or phrases that indicate trigger words or relation summaries from the following answers; the relation is {relation}.
Output a string list contain all the words.
output_case_1:
{content_1}
paraphrased_sentence: {paraphrased_sentence_1}
test_sentence: {test_sentence_1}

output_case_2:
{content_2}
paraphrased_sentence: {paraphrased_sentence_2}
test_sentence: {test_sentence_2}

output_case_3:
{content_3}
paraphrased_sentence: {paraphrased_sentence_3}
test_sentence: {test_sentence_3}

output_case_4:
{content_4}
paraphrased_sentence: {paraphrased_sentence_4}
test_sentence: {test_sentence_4}

output_case_5:
{content_5}
paraphrased_sentence: {paraphrased_sentence_5}
test_sentence: {test_sentence_5}
"""




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

def main():
    input_file = input("Please enter the path to the input JSONL file: ").strip()
    relation_with_cases = read_data(input_file)
    prompt_list = []
    for item in relation_with_cases:
        label = item['relation']
        cases = item['cases']
        if len(cases) >= 5:
            case_1 = cases[0]
            case_2 = cases[1]
            case_3 = cases[2]
            case_4 = cases[3]
            case_5 = cases[4]
            prompt = prompt_template_2.format(
                relation=label,
                content_1=case_1['content'],
                paraphrased_sentence_1 = case_1['paraphrased_sentence'],
                test_sentence_1 = case_1['test_sentence'],
                paraphrased_sentence_subject_1=case_1['paraphrased_sentence_subject'],
                paraphrased_sentence_object_1=case_1['paraphrased_sentence_object'],
                test_sentence_subject_1=case_1['test_sentence_subject'],
                test_sentence_object_1=case_1['test_sentence_object'],
                content_2=case_2['content'],
                paraphrased_sentence_2 = case_2['paraphrased_sentence'],
                test_sentence_2 = case_2['test_sentence'],
                paraphrased_sentence_subject_2=case_2['paraphrased_sentence_subject'],
                paraphrased_sentence_object_2=case_2['paraphrased_sentence_object'],
                test_sentence_subject_2=case_2['test_sentence_subject'],
                test_sentence_object_2=case_2['test_sentence_object'],
                content_3=case_3['content'],
                paraphrased_sentence_3 = case_3['paraphrased_sentence'],
                test_sentence_3 = case_3['test_sentence'],
                paraphrased_sentence_subject_3=case_3['paraphrased_sentence_subject'],
                paraphrased_sentence_object_3=case_3['paraphrased_sentence_object'],
                test_sentence_subject_3=case_3['test_sentence_subject'],
                test_sentence_object_3=case_3['test_sentence_object'],
                content_4=case_4['content'],
                paraphrased_sentence_4 = case_4['paraphrased_sentence'],
                test_sentence_4 = case_4['test_sentence'],
                paraphrased_sentence_subject_4=case_4['paraphrased_sentence_subject'],
                paraphrased_sentence_object_4=case_4['paraphrased_sentence_object'],
                test_sentence_subject_4=case_4['test_sentence_subject'],
                test_sentence_object_4=case_4['test_sentence_object'],
                content_5=case_5['content'],
                paraphrased_sentence_5 = case_5['paraphrased_sentence'],
                test_sentence_5 = case_5['test_sentence'],
                paraphrased_sentence_subject_5=case_5['paraphrased_sentence_subject'],
                paraphrased_sentence_object_5=case_5['paraphrased_sentence_object'],
                test_sentence_subject_5=case_5['test_sentence_subject'],
                test_sentence_object_5=case_5['test_sentence_object']
            )
            prompt_list.append({
                'prompt': prompt
            })
        else:
            # case_1 = cases[0]
            # prompt = prompt_template_1.format(
            #     relation=label,
            #     content_1=case_1['content'],
            #     paraphrased_sentence_subject_1=case_1['paraphrased_sentence_subject'],
            #     paraphrased_sentence_object_1=case_1['paraphrased_sentence_object'],
            #     test_sentence_subject_1=case_1['test_sentence_subject'],
            #     test_sentence_object_1=case_1['test_sentence_object']
            # )
            case_1 = cases[0]
            case_2 = cases[1]
            case_3 = cases[2]
            case_4 = cases[3]
            prompt = prompt_template_1.format(
                relation=label,
                content_1=case_1['content'],
                paraphrased_sentence_1 = case_1['paraphrased_sentence'],
                test_sentence_1 = case_1['test_sentence'],
                paraphrased_sentence_subject_1=case_1['paraphrased_sentence_subject'],
                paraphrased_sentence_object_1=case_1['paraphrased_sentence_object'],
                test_sentence_subject_1=case_1['test_sentence_subject'],
                test_sentence_object_1=case_1['test_sentence_object'],
                content_2=case_2['content'],
                paraphrased_sentence_2 = case_2['paraphrased_sentence'],
                test_sentence_2 = case_2['test_sentence'],
                paraphrased_sentence_subject_2=case_2['paraphrased_sentence_subject'],
                paraphrased_sentence_object_2=case_2['paraphrased_sentence_object'],
                test_sentence_subject_2=case_2['test_sentence_subject'],
                test_sentence_object_2=case_2['test_sentence_object'],
                content_3=case_3['content'],
                paraphrased_sentence_3 = case_3['paraphrased_sentence'],
                test_sentence_3 = case_3['test_sentence'],
                paraphrased_sentence_subject_3=case_3['paraphrased_sentence_subject'],
                paraphrased_sentence_object_3=case_3['paraphrased_sentence_object'],
                test_sentence_subject_3=case_3['test_sentence_subject'],
                test_sentence_object_3=case_3['test_sentence_object'],
                content_4=case_4['content'],
                paraphrased_sentence_4 = case_4['paraphrased_sentence'],
                test_sentence_4 = case_4['test_sentence'],
                paraphrased_sentence_subject_4=case_4['paraphrased_sentence_subject'],
                paraphrased_sentence_object_4=case_4['paraphrased_sentence_object'],
                test_sentence_subject_4=case_4['test_sentence_subject'],
                test_sentence_object_4=case_4['test_sentence_object']
            )
            prompt_list.append({
                'prompt': prompt
            })
        # print(prompt)
        # print('\n'*3)
    out_path = input("Please enter the path to save the prompts JSONL file: ").strip()
    write_to_jsonl(prompt_list, out_path)

if __name__ == "__main__":
    main()
