from tqdm import tqdm
import json
import re



input_nosum_direct = """
Are the relations between "{paraphrased_sentence_subject}" and "{paraphrased_sentence_object}" in "{paraphrased_sentence}" and between "{test_sentence_subject}" and "{test_sentence_object}" in {test_sentence} similar? 
Directly answer Yes or No in a separate line.
---
IMPORTANT: MUST answer with just Yes or No.
"""

input_nosum_random_reasoning= """
Are the relations between "{paraphrased_sentence_subject}" and "{paraphrased_sentence_object}" in "{paraphrased_sentence}" and between "{test_sentence_subject}" and "{test_sentence_object}" in {test_sentence} similar? 
Generate the understanding process, followed by Yes or No in a separate line.
"""

input_sum_direct = """
You are given two sentences. Follow the three steps below to determine whether they express a similar relation.
---
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

Step 3: generate a question as: are the relations between "{paraphrased_sentence_subject}" and "{paraphrased_sentence_object}" in Relation_Summarization_1 and between "{test_sentence_subject}" and "{test_sentence_object}" in Relation_Summarization_2 similar? 

Step 4: directly answer the question with Yes or No in a separate line.
"""


input_sum_keywords_direct = """
You are given two sentences. Follow the three steps below to determine whether they express a similar relation.
---
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

Step 3: generate a question as: are the relations between "{paraphrased_sentence_subject}" and "{paraphrased_sentence_object}" in Relation_Summarization_1 and between "{test_sentence_subject}" and "{test_sentence_object}" in Relation_Summarization_2 similar? 

Step 4: Focus on the keywords in the Relation_Summarization_1 an Relation_Summarization_2 that convey relations, and directly answer the question with Yes or No in a separate line.
"""

input_sum_random_reasoning = """
You are given two sentences. Follow the three steps below to determine whether they express a similar relation.
---
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

Step 3: are the relations between "{paraphrased_sentence_subject}" and "{paraphrased_sentence_object}" in Relation_Summarization_1 and between "{test_sentence_subject}" and "{test_sentence_object}" in Relation_Summarization_2 similar?
Generate the understanding process, followed by Yes or No in a separate line.
"""


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

# ----
# IMPORTANT: Do not repeat steps just answer.

def prompt_set(paraphrased_sentence, test_sentence, paraphrased_sentence_subject, paraphrased_sentence_object, test_sentence_subject, test_sentence_object):
    
    if PROMPT_STRATEGY == 'input_nosum_direct':
        prompt = input_nosum_direct.format(
            paraphrased_sentence=paraphrased_sentence,
            test_sentence=test_sentence,
            paraphrased_sentence_subject=paraphrased_sentence_subject,
            paraphrased_sentence_object=paraphrased_sentence_object,
            test_sentence_subject=test_sentence_subject,
            test_sentence_object=test_sentence_object,
        )
    elif PROMPT_STRATEGY == 'input_nosum_random_reasoning':
        prompt = input_nosum_random_reasoning.format(
            paraphrased_sentence=paraphrased_sentence,
            test_sentence=test_sentence,
            paraphrased_sentence_subject=paraphrased_sentence_subject,
            paraphrased_sentence_object=paraphrased_sentence_object,
            test_sentence_subject=test_sentence_subject,
            test_sentence_object=test_sentence_object,
        )
    elif PROMPT_STRATEGY == 'input_sum_direct':
        prompt = input_sum_direct.format(
            paraphrased_sentence=paraphrased_sentence,
            test_sentence=test_sentence,
            paraphrased_sentence_subject=paraphrased_sentence_subject,
            paraphrased_sentence_object=paraphrased_sentence_object,
            test_sentence_subject=test_sentence_subject,
            test_sentence_object=test_sentence_object,
        )
    elif PROMPT_STRATEGY == 'input_sum_keywords_direct':
        prompt = input_sum_keywords_direct.format(
            paraphrased_sentence=paraphrased_sentence,
            test_sentence=test_sentence,
            paraphrased_sentence_subject=paraphrased_sentence_subject,
            paraphrased_sentence_object=paraphrased_sentence_object,
            test_sentence_subject=test_sentence_subject,
            test_sentence_object=test_sentence_object,
        )
    elif PROMPT_STRATEGY == 'input_sum_random_reasoning':
        prompt = input_sum_random_reasoning.format(
            paraphrased_sentence=paraphrased_sentence,
            test_sentence=test_sentence,
            paraphrased_sentence_subject=paraphrased_sentence_subject,
            paraphrased_sentence_object=paraphrased_sentence_object,
            test_sentence_subject=test_sentence_subject,
            test_sentence_object=test_sentence_object,
        )
    elif PROMPT_STRATEGY == 'input_sum_keywords_reasoning':
        prompt = input_sum_keywords_reasoning.format(
            paraphrased_sentence=paraphrased_sentence,
            test_sentence=test_sentence,
            paraphrased_sentence_subject=paraphrased_sentence_subject,
            paraphrased_sentence_object=paraphrased_sentence_object,
            test_sentence_subject=test_sentence_subject,
            test_sentence_object=test_sentence_object,
        )
    return prompt


def evaluation(val_file_path):
    # Step 2: Open the dev test file (train and val)
    val_data = []
    with open(val_file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            example = json.loads(line)
            val_data.append(example)

    # Step 3: Loop through all episodes. For each episode: read 5 items from train, and 3 times from val (5 items each time).
    num_train_item_1_episode = 5
    num_val_item_1_episode = 15
    number_episode = len(val_data) // num_val_item_1_episode
    id = 0
    all_prompt = []
    for i in tqdm(range(number_episode)):

        # Step 3.1: Read 5 train items, extract fields and embed them into the prompt template.
        start_train = i * num_train_item_1_episode
        end_train = start_train + num_train_item_1_episode

        # Step 3.2: Repeat 3 times, each time reading 5 val items.
        start_val = i * num_val_item_1_episode
        end_val = start_val + num_val_item_1_episode
        for j in range(3):
            start_val_current = start_val + j * num_train_item_1_episode # Each test sentence is matched with all train rules in this episode
            end_val_current = start_val_current + num_train_item_1_episode
            sample_test = val_data[start_val_current:end_val_current]
            for test_case in sample_test:
                prompt_ask = prompt_set(test_case['paraphrased_sentence'], test_case['test_sentence'], test_case['paraphrased_sentence_subject'], test_case['paraphrased_sentence_object'], test_case['test_sentence_subject'], test_case['test_sentence_object'])
                all_prompt.append({
                    "id": id,
                    "prompt": prompt_ask,
                    "paraphrased_sentence_subject" : test_case['paraphrased_sentence_subject'],
                    "paraphrased_sentence_object" : test_case['paraphrased_sentence_object'],
                    "test_sentence_subject" : test_case['test_sentence_subject'], 
                    "test_sentence_object" : test_case['test_sentence_object'],
                    "ss_relation": test_case["ss_relation"],
                    "ts_relation": test_case["ts_relation"],
                    "paraphrased_sentence": test_case["paraphrased_sentence"],
                    "test_sentence": test_case["test_sentence"],
                    "label": test_case['label'],
                })
                id += 1
    return all_prompt


if __name__ == '__main__': # Run for full test partition
    PROMPT_STRATEGY = 'input_sum_keywords_reasoning'
    DATASET = "NYT29"
    val_path = input("Please enter the path to the validation file: ").strip()
    out_path = input("Please enter the output path for the prompt chunks: ").strip()

    all_prompt = evaluation(val_path)
    with open(out_path, 'w', encoding='utf-8') as f:
        for item in all_prompt:
            f.write(json.dumps(item) + '\n')