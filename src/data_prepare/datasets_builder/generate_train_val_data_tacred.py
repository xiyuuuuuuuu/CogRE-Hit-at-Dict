import json
import argparse
import os
import random
from collections import Counter, defaultdict


def get_sentence_with_subj_obj_from_tokenslist(line):
    final_sentence = ""
    final_subj = ""
    final_obj = ""
    for i, token in enumerate(line['tokens']):
        if line['subj_start'] <= i <= line['subj_end']:
            final_subj += token + " "
        elif line['obj_start'] <= i <= line['obj_end']:
            final_obj += token + " "
        final_sentence += token + " "
    precessed_sentence = {
        'sentence': final_sentence.strip(),
        'subj': final_subj.strip(),
        'obj': final_obj.strip(),
    }
    return precessed_sentence

def sample_1000_groups(all_lines):
    """
    Stratified sampling of 1000 episodes from TACRED validation set episode data,
    each episode represents a ts_relation, and save the results to the specified path.
    """

    # Input and output paths

    CANDIDATE_SIZE = 5
    SAMPLE_SIZE = 1000

    # Step 1: Split into one sentence and its 5 candidate sentences (every 5 lines)
    groups = [all_lines[i:i+CANDIDATE_SIZE] for i in range(0, len(all_lines), CANDIDATE_SIZE)]

    # Step 3: Choose a representative ts_relation for each group
    # Here we use the ts_relation from the first line of the group; alternatively, use the most frequent one
    group_labels = []
    label_to_group_indices = defaultdict(list)

    for idx, group in enumerate(groups):
        relations = []
        for line in group:
            relations.append(line['ts_relation'])
        if relations:
            # Use the first one as representative
            label = relations[0]
            group_labels.append(label)
            label_to_group_indices[label].append(idx)

    # Step 4: Calculate how many episodes to sample per ts_relation
    label_counter = Counter(group_labels)
    total_groups = len(groups)

    # Distribute sample counts proportionally
    label_sample_counts = {
        label: round((count / total_groups) * SAMPLE_SIZE)
        for label, count in label_counter.items()
    }

    # Prevent the sum from deviating from 1000 (rounding errors)
    # Adjust the count of the label with the most samples to control precisely
    diff = SAMPLE_SIZE - sum(label_sample_counts.values())
    if diff != 0:
        # Find the label with the most samples and adjust the difference
        max_label = max(label_sample_counts, key=label_sample_counts.get)
        label_sample_counts[max_label] += diff

    # Step 5: Stratified sampling
    sampled_indices = []
    for label, count in label_sample_counts.items():
        candidates = label_to_group_indices[label]
        if len(candidates) < count:
            raise ValueError(f"Not enough episodes for label '{label}' to sample {count}")
        sampled_indices.extend(random.sample(candidates, count))

    # Step 6: Write results
    sampled_lines = []
    for idx in sampled_indices:
        sampled_lines.extend(groups[idx])
    
    return sampled_lines

def sample_1000_episodes(all_lines):
    """
    Stratified sampling of 1000 episodes from TACRED validation set episode data,
    each episode represents a ts_relation, and save the results to the specified path.
    """

    EPISODE_SIZE = 15
    SAMPLE_SIZE = 1000

    # Step 2: Split into episodes (every 15 lines)
    episodes = [all_lines[i:i+EPISODE_SIZE] for i in range(0, len(all_lines), EPISODE_SIZE)]

    # Step 3: Choose a representative ts_relation for each episode
    # Here we use the ts_relation from the first line of the episode; alternatively, use the most frequent one
    episode_labels = []
    label_to_episode_indices = defaultdict(list)

    for idx, episode in enumerate(episodes):
        relations = []
        for line in episode:
            relations.append(line['ts_relation'])
        if relations:
            # Use the first one as representative
            label = relations[0]
            episode_labels.append(label)
            label_to_episode_indices[label].append(idx)

    # Step 4: Calculate how many episodes to sample per ts_relation
    label_counter = Counter(episode_labels)
    total_episodes = len(episodes)

    # Distribute sample counts proportionally
    label_sample_counts = {
        label: round((count / total_episodes) * SAMPLE_SIZE)
        for label, count in label_counter.items()
    }

    # Prevent the sum from deviating from 1000 (rounding errors)
    # Adjust the count of the label with the most samples to control precisely
    diff = SAMPLE_SIZE - sum(label_sample_counts.values())
    if diff != 0:
        # Find the label with the most samples and adjust the difference
        max_label = max(label_sample_counts, key=label_sample_counts.get)
        label_sample_counts[max_label] += diff

    # Step 5: Stratified sampling
    sampled_indices = []
    for label, count in label_sample_counts.items():
        candidates = label_to_episode_indices[label]
        if len(candidates) < count:
            raise ValueError(f"Not enough episodes for label '{label}' to sample {count}")
        sampled_indices.extend(random.sample(candidates, count))

    # Step 6: Write results
    sampled_lines = []
    for idx in sampled_indices:
        sampled_lines.extend(episodes[idx])
    
    return sampled_lines


def read_valdata(dev_test_path: str):
    """
    Load and process few-shot episode format data from the validation set (dev_path),
    return a structured list of samples, each being a rule-sentence paired instance with multiple feature fields.
    """

    print(f"Read valdata {dev_test_path}")
    val = []         # Used to save the final output sample list
    original_relation_labels_val = []  # Used to save original relation labels (if needed)
    # load (format: [episodes, selections, relations])
    with open(dev_test_path) as fin:
        val_data = json.load(fin)


    # Iterate through each episode (triplet parallel zip: episode, selections, relations)
    for episode, selections, relations in zip(val_data[0], val_data[1], val_data[2]):
        for ts in episode['meta_test']:  # Iterate through test samples in the target task (ts = test sentence)

            # Construct dictionary for meta_train (sentence entity annotation, rule matching)

            # Get all support sentences (ss) in 'meta_train'
            episode_ss = [y for x in episode['meta_train'] for y in x]
            # Perform entity annotation on all support sentences (ss)
            preprocess_episode_ss = [get_sentence_with_subj_obj_from_tokenslist(x) for x in episode_ss]


            # Extract true relations corresponding to support sentences (for supervision)
            ss_relations = [
                s['relation'] for s in episode_ss
            ]

            # Preprocess current test sentence (e.g., lowercase, dependency parsing, etc.)
            processed_episode_ts = get_sentence_with_subj_obj_from_tokenslist(ts)


            # Iterate through all rules to construct rule-sentence paired samples 
            for ss, ss_relation in zip(preprocess_episode_ss, ss_relations):
                # Construct a final sample (including various structured fields of rule and sentence)
                val.append({
                    'paraphrased_sentence': ss['sentence'],
                    'paraphrased_sentence_subject': ss['subj'],
                    'paraphrased_sentence_object': ss['obj'],
                    'test_sentence': processed_episode_ts['sentence'],
                    'test_sentence_subject': processed_episode_ts['subj'],
                    'test_sentence_object': processed_episode_ts['obj'],
                    'ss_relation': ss_relation,
                    'ts_relation': ts['relation'] if ts['relation'] in ss_relations else 'no_relation',
                    'label': 'Yes' if ss_relation == ts['relation'] else 'No',
                })
                original_relation_labels_val.append({
                    'paraphrased_sentence': ss['sentence'],
                    'paraphrased_sentence_subject': ss['subj'],
                    'paraphrased_sentence_object': ss['obj'],
                    'test_sentence': processed_episode_ts['sentence'],
                    'test_sentence_subject': processed_episode_ts['subj'],
                    'test_sentence_object': processed_episode_ts['obj'],
                    'ss_relation': ss_relation,
                    'ts_relation': ts['relation'],
                    'label': 'Yes' if ss_relation == ts['relation'] else 'No',
                })
    # Return
    return val, original_relation_labels_val

def write_to_jsonl(data, output_path):
    """
    Write data to JSONL file.
    Each element is written as one line in the file.
    """
    with open(output_path, 'w') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')
    print(f"Data written to {output_path}")


def generate_data(args):
    """
    Used to load and preprocess validation datasets.
    
    Workflow:
    - Read rules
    - Load validation data from each dev_path (read_valdata)
    - Tokenize validation data (using model's tokenizer)
    - Return a list, each element is a tokenized HuggingFace Dataset
    """


    # Compose input and output paths
    type_episodes = args['dev/test/train']
    input_dir_path = args['dev/test_dir_path']
    output_dir_path = args['output_path']
    input_path = input_dir_path + type_episodes + "/"
    output_path = output_dir_path + type_episodes + "/"
    

    # file name prefix
    file_name_prefix = "5_way_1_shots_10K_episodes_3q_seed_16029"

    # Iterate through each dev_path (each path is an episodic JSON file)
    for i in range(5):
        # Construct full input and output paths
        input_file_path = input_path + file_name_prefix + str(i) + ".json"
        output_val_file_path = output_path + "/val/"+ file_name_prefix + str(i) + ".jsonl"
        output_val_file_path_original_relation_labels = output_path + "/val_original_relation_labels/"+ file_name_prefix + str(i) + ".jsonl"
        output_val_file_path_sampled_episodes = output_path + "/val_sampled_1000_episodes/" + file_name_prefix + str(i) + ".jsonl"
        output_val_file_path_sampled_groups = output_path + "/val_sampled_1000_groups/" + file_name_prefix + str(i) + ".jsonl"
        # Create output directories if they do not exist
        os.makedirs(os.path.dirname(output_path + "/val/"), exist_ok=True)
        os.makedirs(os.path.dirname(output_path + "/val_original_relation_labels/"), exist_ok=True)
        
        # Load original validation data with rules using read_valdata()
        val, original_relation_labels_val = read_valdata(input_file_path)
        # Sample 1000 episodes
        val_sampled_episodes = sample_1000_episodes(val)
        # Sample 1000 groups
        val_sampled_groups = sample_1000_groups(val)
        # Output val and train to JSON files
        write_to_jsonl(val, output_val_file_path)
        if type_episodes == "train_episodes":
            write_to_jsonl(original_relation_labels_val, output_val_file_path_original_relation_labels)
        else:
            os.makedirs(os.path.dirname(output_path + "/val_sampled_1000_episodes/"), exist_ok=True)
            os.makedirs(os.path.dirname(output_path + "/val_sampled_1000_groups/"), exist_ok=True)
            write_to_jsonl(val_sampled_episodes, output_val_file_path_sampled_episodes)
            write_to_jsonl(val_sampled_groups, output_val_file_path_sampled_groups)
        



# Main entry point
if __name__ == "__main__":
    # Set up command line argument parser
    parser = argparse.ArgumentParser()

    # Load dev/test data paths
    parser.add_argument("--dev/test_dir_path", type=str, required=False, help="Path to raw TACRED data directory")
    parser.add_argument("--output_path", type=str, required=False, help="Path to save processed dataset")
    parser.add_argument("--dev/test/train", type=str, required=False, default="test_episodes", help="Type of episodes (train/test)")

    # Parse command line arguments into dictionary
    args = vars(parser.parse_args())
    print(args)

    if not args["dev/test_dir_path"]:
        args["dev/test_dir_path"] = input("Please enter the path to the TACRED raw dataset directory: ").strip()
    if not args["output_path"]:
        args["output_path"] = input("Please enter the output path for processed datasets: ").strip()

    # Call main function with argument dictionary
    # Generate data
    generate_data(args)
