# Copyright 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Preprocess the 1-shot-tacred-train dataset to parquet format
"""

import argparse
import os
import re
from datasets import Dataset
import json
import datasets

from verl.utils.hdfs_io import copy, makedirs


def extract_solution(solution_str):
    solution = re.search("#### (\\-?[0-9\\.\\,]+)", solution_str)
    assert solution is not None
    final_solution = solution.group(0)
    final_solution = final_solution.split("#### ")[1].replace(",", "")
    return final_solution


if __name__ == "__main__":
    # set args
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_data_source", default=None, help="Path to the training data JSONL file")
    parser.add_argument("--test_data_source", default=None, help="Path to the test data JSONL file")
    parser.add_argument("--local_dir", default=None, help="Directory to save parquet files")
    parser.add_argument("--hdfs_dir", default=None)
    args = parser.parse_args()
    if not args.train_data_source:
        args.train_data_source = input("Please enter the path to the training data JSONL file: ").strip()
    if not args.test_data_source:
        args.test_data_source = input("Please enter the path to the test data JSONL file: ").strip()
    if not args.local_dir:
        args.local_dir = input("Please enter the directory to save parquet files: ").strip()
    train_data_source = args.train_data_source
    test_data_source = args.test_data_source

    # load train set and test set
    train_dataset = []
    test_dataset = []
    # read train
    with open(train_data_source, 'r', encoding='utf-8') as f:
        train_data = [json.loads(line) for line in f]
    train_dataset = Dataset.from_list(train_data)
    # read test
    with open(test_data_source, 'r', encoding='utf-8') as f:
        test_data = [json.loads(line) for line in f]
    test_dataset = Dataset.from_list(test_data)



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
    IMPORTANT: DO NOT REPEAT SENTENCE OR QUESTION.
    """


    # add a row to each data item that represents a unique id
    def make_map_fn(split):
        def process_fn(example, idx):

            paraphrased_sentence_subject = example.pop("paraphrased_sentence_subject")
            paraphrased_sentence_object = example.pop("paraphrased_sentence_object")
            paraphrased_sentence = example.pop("paraphrased_sentence")
            test_sentence_subject = example.pop("test_sentence_subject")
            test_sentence_object = example.pop("test_sentence_object")
            test_sentence = example.pop("test_sentence")
            ts_relation = example.pop("ts_relation")
            ss_relation = example.pop("ss_relation")

            question = input_sum_keywords_reasoning.format(
                paraphrased_sentence_subject=paraphrased_sentence_subject,
                paraphrased_sentence_object=paraphrased_sentence_object,
                paraphrased_sentence=paraphrased_sentence,
                test_sentence_subject=test_sentence_subject,
                test_sentence_object=test_sentence_object,
                test_sentence=test_sentence,
            )


            solution = example.pop("label")

            # data_source = '1-shot-tacred-weighted_reward_with_keywords'
            data_source = '1-shot-tacred-train'

            data = {
                "data_source": data_source,
                "prompt": [
                    {
                        "role": "user",
                        "content": question,
                    }
                ],
                "ability": "sentence_pair_relation_matching",
                "reward_model": {"style": "rule", "ground_truth": solution},
                "extra_info": {
                    "split": split,
                    "index": idx,
                    # "ts_relation": ts_relation,
                    # "ss_relation": ss_relation,
                },
            }
            return data

        return process_fn

    train_dataset = train_dataset.map(function=make_map_fn("train"), with_indices=True)
    test_dataset = test_dataset.map(function=make_map_fn("test"), with_indices=True)

    local_dir = args.local_dir
    hdfs_dir = args.hdfs_dir

    train_dataset.to_parquet(os.path.join(local_dir, "train.parquet"))
    test_dataset.to_parquet(os.path.join(local_dir, "test.parquet"))

    if hdfs_dir is not None:
        makedirs(hdfs_dir)

        copy(src=local_dir, dst=hdfs_dir)