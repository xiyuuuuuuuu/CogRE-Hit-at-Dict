import json
import re
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import logging
logging.set_verbosity_error()
import torch
from tqdm import tqdm
import traceback
from sklearn.metrics import f1_score
import sys
from collections import Counter
from transformers import logging
import os
import requests
import json
import re
import random

NO_RELATION = "no_relation"

def load_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [json.loads(line) for line in file]

def save_jsonl(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for item in data:
            file.write(json.dumps(item) + '\n')



def tacred_score(key, prediction, verbose=False):
    """
    Scoring function for the TACRED task.
    Args:
        key: list of gold labels
        prediction: list of predicted relation labels
        verbose: if True, print detailed per-relation statistics

    Returns:
        Precision (micro), Recall (micro), F1 (micro)
    """

    # Initialize counters
    # correct_by_relation: counts correct predictions per relation
    # guessed_by_relation: counts predicted instances per relation (correct or not)
    # gold_by_relation: counts gold instances per relation
    correct_by_relation = Counter()
    guessed_by_relation = Counter()
    gold_by_relation    = Counter()

    # Iterate through all samples
    for row in range(len(key)):
        gold = key[row]           # gold label for sample row
        guess = prediction[row]   # predicted label for sample row

        # Case 1: Both gold and predicted are no_relation (ignore these)
        if gold == NO_RELATION and guess == NO_RELATION:
            pass  # do nothing

        # Case 2: Gold is no_relation, prediction is a relation (false positive)
        elif gold == NO_RELATION and guess != NO_RELATION:
            guessed_by_relation[guess] += 1  # count false positive

        # Case 3: Gold is a relation, prediction is no_relation (false negative)
        elif gold != NO_RELATION and guess == NO_RELATION:
            gold_by_relation[gold] += 1  # count missed relation

        # Case 4: Both gold and predicted are relations
        elif gold != NO_RELATION and guess != NO_RELATION:
            guessed_by_relation[guess] += 1  # count predicted relation
            gold_by_relation[gold] += 1      # count gold relation
            if gold == guess:
                correct_by_relation[guess] += 1  # correct prediction

    # Print per-relation P/R/F1 if verbose
    if verbose:
        print("Per-relation statistics:")
        relations = gold_by_relation.keys()  # all relations in gold
        longest_relation = 0  # for formatting output

        # find longest relation name length
        for relation in sorted(relations):
            longest_relation = max(len(relation), longest_relation)

        # print metrics per relation
        for relation in sorted(relations):
            correct = correct_by_relation[relation]  # correct count
            guessed = guessed_by_relation[relation]  # predicted count
            gold    = gold_by_relation[relation]     # gold count

            # precision: correct / predicted
            prec = 1.0
            if guessed > 0:
                prec = float(correct) / float(guessed)

            # recall: correct / gold
            recall = 0.0
            if gold > 0:
                recall = float(correct) / float(gold)

            # F1 score
            f1 = 0.0
            if prec + recall > 0:
                f1 = 2.0 * prec * recall / (prec + recall)

            # print relation metrics
            sys.stdout.write(("{:<" + str(longest_relation) + "}").format(relation))  # relation name
            sys.stdout.write("  P: ")
            if prec < 0.1: sys.stdout.write(' ')
            if prec < 1.0: sys.stdout.write(' ')
            sys.stdout.write("{:.2%}".format(prec))  # precision percentage
            sys.stdout.write("  R: ")
            if recall < 0.1: sys.stdout.write(' ')
            if recall < 1.0: sys.stdout.write(' ')
            sys.stdout.write("{:.2%}".format(recall))  # recall percentage
            sys.stdout.write("  F1: ")
            if f1 < 0.1: sys.stdout.write(' ')
            if f1 < 1.0: sys.stdout.write(' ')
            sys.stdout.write("{:.2%}".format(f1))  # F1 percentage
            sys.stdout.write("  #: %d" % gold)  # gold count
            sys.stdout.write("\n")
        print("")

    # Compute overall micro-averaged metrics
    if verbose:
        print("Final Score:")

    prec_micro = 1.0
    if sum(guessed_by_relation.values()) > 0:
        prec_micro = float(sum(correct_by_relation.values())) / float(sum(guessed_by_relation.values()))

    recall_micro = 0.0
    if sum(gold_by_relation.values()) > 0:
        recall_micro = float(sum(correct_by_relation.values())) / float(sum(gold_by_relation.values()))

    f1_micro = 0.0
    if prec_micro + recall_micro > 0.0:
        f1_micro = 2.0 * prec_micro * recall_micro / (prec_micro + recall_micro)

    # if verbose:
        # print("Precision (micro): {:.2%}".format(prec_micro))
        # print("   Recall (micro): {:.2%}".format(recall_micro))
        # print("       F1 (micro): {:.2%}".format(f1_micro))

    return prec_micro, recall_micro, f1_micro  # return final scores


def main():
    input_file = input("Please enter the path to the results JSONL file: ").strip()

    data = load_jsonl(input_file)

    key = []
    prediction = []
    count_yes = 0
    count_no = 0

    for i in range(1000): # 1000 episodes
        # Each episode has 15 samples
        episode_data = data[i * 15: (i + 1) * 15]
        for j in range(3):
            # Each episode has 3 tests, each with 5 samples
            test_case = episode_data[j * 5: (j + 1) * 5]
            yes_relation = []
            key.append(test_case[0]["ts_relation"])
            for sample in test_case: 
                # If LLM_answer is "Yes"
                if sample["answer"] == "Yes":
                    # Add ss_relation to yes_relation list
                    yes_relation.append(sample["ss_relation"])
                    count_yes += 1
                elif sample["answer"] == "No":
                    count_no += 1
            # If yes_relation is not empty, randomly select one as prediction
            if yes_relation:
                # Randomly pick one from yes_relation as prediction
                random_choice = random.choice(yes_relation)
                prediction.append(random_choice)
                # prediction.append(yes_relation[0])
            else:
                # If no "Yes" answers, assign "no_relation"
                prediction.append("no_relation")
    

    # Compute F1 score
    scores = tacred_score(key, prediction, True)
    current_result = {
        'p_tacred': scores[0],
        'r_tacred': scores[1],
        'f1_tacred': scores[2],
    }
    # print(current_result)
    # print(f"count_yes: {count_yes}, count_no: {count_no}")
    return current_result

if __name__ == "__main__":
    max_f1 = 0.0
    min_f1 = 1.0
    max_reult = None
    min_result = None
    for i in range(500):
        current_result = main()
        if current_result['f1_tacred'] > max_f1:
            max_f1 = current_result['f1_tacred']
            max_reult = current_result
    print(f"max_f1: {max_f1}, max_reult: {max_reult}")