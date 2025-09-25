import json
from collections import Counter, defaultdict
import random
import os
import math

relation_1_no_relation_num_needed = {
    "/business/company/founders": 500,
    "/business/company/place_founded": 500,
    "/business/person/company": 500,
    "/film/film_location/featured_in_films": 978,
    "/location/country/capital": 500,
    "/location/location/contains": 500,
    "/location/us_county/county_seat": 898,
    "/location/us_state/capital": 500,
    "/people/deceased_person/place_of_burial": 972,
    "/people/ethnicity/geographic_distribution": 500,
    "/people/person/children": 500,
    "/people/person/ethnicity": 850,
    "/people/person/nationality": 500,
    "/people/person/place_lived": 500,
    "/people/place_of_interment/interred_here": 962
}

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



def sample_1000_groups(all_lines):
    """
    Stratified sampling of 1000 episodes from the TACRED validation set episode data,
    each episode represents a ts_relation, and save the result to the specified path.
    """

    # Input and output paths

    CANDIDATE_SIZE = 5
    SAMPLE_SIZE = 1000

    # Step 1: Split into one sentence and its 5 candidate sentences (every 5 lines)
    groups = [all_lines[i:i+CANDIDATE_SIZE] for i in range(0, len(all_lines), CANDIDATE_SIZE)]

    # Step 3: Choose a representative ts_relation for each group
    # Here we use the ts_relation from the first line of the group; alternatively, the most frequent one
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

    # Prevent the total from not being exactly 1000 (due to rounding error)
    # Adjust the count of the largest label to control precisely
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
    Stratified sampling of 1000 episodes from the TACRED validation set episode data,
    each episode represents a ts_relation, and save the result to the specified path.
    """

    EPISODE_SIZE = 15
    SAMPLE_SIZE = 1000

    # Step 2: Split into episodes (every 15 lines)
    episodes = [all_lines[i:i+EPISODE_SIZE] for i in range(0, len(all_lines), EPISODE_SIZE)]

    # Step 3: Choose a representative ts_relation for each episode
    # Here we use the ts_relation from the first line of the episode; alternatively, the most frequent one
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

    # Prevent the total from not being exactly 1000 (due to rounding error)
    # Adjust the count of the largest label to control precisely
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

def sample(data, sample_size=1000):
    """
    Sample a specified number of items from data
    """
    if len(data) < sample_size:
        raise ValueError(f"Not enough data to sample {sample_size} items.")
    
    sampled_data = random.sample(data, sample_size)
    return sampled_data

def sample_1000_negative_and_positive_pairs(all_lines, SAMPLE_SIZE = 1000):
    """
    Sample 1000 positive and negative pairs from all_lines
    Ensure positive pairs per ts_relation are roughly balanced
    """
    REMAINING_SIZE_WITH_NO_RELATION = 5000
    REMAINING_SIZE_POSITIVE = int(SAMPLE_SIZE * 0.004)

    
    # Step 1: Split into positive and negative pairs
    original_positive_lines = [line for line in all_lines if line['label'] == 'Yes']
    original_negative_lines = [line for line in all_lines if line['label'] == 'No']
    print(f"Original positive lines: {len(original_positive_lines)}")
    print(f"Original negative lines: {len(original_negative_lines)}")

    # Step 2: Control the number of 'no_relation' in negative samples
    negative_lines_with_relation = [line for line in original_negative_lines if line['ts_relation'] != 'no_relation' and line['ss_relation'] != 'no_relation']
    print(f"negative_lines_with_relation: {len(negative_lines_with_relation)}")
    negative_lines_no_relation = [line for line in original_negative_lines if line['ts_relation'] == 'no_relation' or line['ss_relation'] == 'no_relation']
    print(f"negative_lines_with_no_relation: {len(negative_lines_no_relation)}")


    # Step 3: Collect negative samples
    final_positive_num = REMAINING_SIZE_POSITIVE
    final_negative_num = SAMPLE_SIZE - REMAINING_SIZE_POSITIVE
    REMAINING_SIZE_WITH_NO_RELATION = int(final_negative_num*0.5)
    final_sampled_negative_with_relation_num = min(len(negative_lines_with_relation), final_negative_num - REMAINING_SIZE_WITH_NO_RELATION)
    final_sampled_negative_no_relation_num = final_negative_num - final_sampled_negative_with_relation_num

    sampled_positive_lines = sample(original_positive_lines, final_positive_num)
    sampled_negative_lines_with_relation = sample(negative_lines_with_relation, final_sampled_negative_with_relation_num)
    sampled_negative_lines_no_relation = sample(negative_lines_no_relation, final_sampled_negative_no_relation_num)

    # Step 4: Merge sampled_positive_lines, sampled_negative_lines_with_relation, and sampled_negative_lines_no_relation
    # Print counts
    print(f"Original positive lines: {len(sampled_positive_lines)}")
    print(f"Sampled negative lines with relation: {len(sampled_negative_lines_with_relation)}")
    print(f"Sampled negative lines without relation: {len(sampled_negative_lines_no_relation)}")
    print(f"Total sampled negative lines: {len(sampled_negative_lines_with_relation) + len(sampled_negative_lines_no_relation)}")
    # Merge
    final_sampled_lines = sampled_positive_lines + sampled_negative_lines_with_relation + sampled_negative_lines_no_relation
    print(f"Total final sampled lines: {len(final_sampled_lines)}")
    # Shuffle order
    random.shuffle(final_sampled_lines)

    return final_sampled_lines

def sampled_by_labels(data):
    final_data = []
    # Step 1: Split into (relation_1, relation_1), (relation_1, no_relation), (relation_1, relation_2)
    data_relation_1_relation_1 = []
    data_relation_1_no_relation = [] # ss_relation cannot be no_relation, only ts_relation can be no_relation
    data_relation_1_relation_2 = []
    for item in data:
        ss_relation = item['ss_relation']
        ts_relation = item['ts_relation']
        if ss_relation == ts_relation:
            data_relation_1_relation_1.append(item)
        elif ts_relation == 'no_relation':
            data_relation_1_no_relation.append(item)
        else: # If ss_relation and ts_relation are different,
            data_relation_1_relation_2.append(item)
    print(f"The length of data_relation_1_relation_1: {len(data_relation_1_relation_1)}")
    print(f"The length of data_relation_1_no_relation: {len(data_relation_1_no_relation)}")
    print(f"The length of data_relation_1_relation_2: {len(data_relation_1_relation_2)}")

    # Step 2: Extract specific relations (remove from original data), sample 250 pairs, and add them along with the remaining data to final_data
    data_relation_1_relation_1_business_company_founders  = []
    data_relation_1_relation_1_business_company_place_founded = []
    data_relation_1_relation_1_business_person_company  = []
    data_relation_1_relation_1_location_country_capital  = []
    data_relation_1_relation_1_location_location_contains  = []
    data_relation_1_relation_1_location_us_state_capital  = []
    data_relation_1_relation_1_people_ethnicity_geographic_distribution  = []
    data_relation_1_relation_1_people_person_children  = []
    data_relation_1_relation_1_people_person_nationality  = []
    data_relation_1_relation_1_people_person_place_lived  = []
    data_relation_1_relation_1_rest = []
    for item in data_relation_1_relation_1:
        if item['ss_relation'] == '/business/company/founders':
            data_relation_1_relation_1_business_company_founders.append(item)
        elif item['ts_relation'] == '/business/company/place_founded':
            data_relation_1_relation_1_business_company_place_founded.append(item)
        elif item['ts_relation'] == '/business/person/company':
            data_relation_1_relation_1_business_person_company.append(item)
        elif item['ts_relation'] == '/location/country/capital':
            data_relation_1_relation_1_location_country_capital.append(item)
        elif item['ts_relation'] == '/location/location/contains':
            data_relation_1_relation_1_location_location_contains.append(item)
        elif item['ss_relation'] == '/location/us_state/capital':
            data_relation_1_relation_1_location_us_state_capital.append(item)
        elif item['ts_relation'] == '/people/ethnicity/geographic_distribution':
            data_relation_1_relation_1_people_ethnicity_geographic_distribution.append(item)
        elif item['ts_relation'] == '/people/person/children':
            data_relation_1_relation_1_people_person_children.append(item)
        elif item['ts_relation'] == '/people/person/nationality':
            data_relation_1_relation_1_people_person_nationality.append(item)
        elif item['ts_relation'] == '/people/person/place_lived':
            data_relation_1_relation_1_people_person_place_lived.append(item)
        else:
            data_relation_1_relation_1_rest.append(item)
    print(f"The length of the original data_relation_1_relation_1_business_company_founders: {len(data_relation_1_relation_1_business_company_founders)}")
    print(f"The length of the original data_relation_1_relation_1_business_company_place_founded: {len(data_relation_1_relation_1_business_company_place_founded)}")
    print(f"The length of the original data_relation_1_relation_1_business_person_company: {len(data_relation_1_relation_1_business_person_company)}")
    print(f"The length of the original data_relation_1_relation_1_location_country_capital: {len(data_relation_1_relation_1_location_country_capital)}")
    print(f"The length of the original data_relation_1_relation_1_location_location_contains: {len(data_relation_1_relation_1_location_location_contains)}")
    print(f"The length of the original data_relation_1_relation_1_location_us_state_capital: {len(data_relation_1_relation_1_location_us_state_capital)}")
    print(f"The length of the original data_relation_1_relation_1_people_ethnicity_geographic_distribution: {len(data_relation_1_relation_1_people_ethnicity_geographic_distribution)}")
    print(f"The length of the original data_relation_1_relation_1_people_person_children: {len(data_relation_1_relation_1_people_person_children)}")
    print(f"The length of the original data_relation_1_relation_1_people_person_nationality: {len(data_relation_1_relation_1_people_person_nationality)}")
    print(f"The length of the original data_relation_1_relation_1_people_person_place_lived: {len(data_relation_1_relation_1_people_person_place_lived)}")

    sampled_data_relation_1_relation_1_business_company_founders = sample(data_relation_1_relation_1_business_company_founders, 250)
    sampled_data_relation_1_relation_1_business_company_place_founded = sample(data_relation_1_relation_1_business_company_place_founded, 250)
    sampled_data_relation_1_relation_1_business_person_company = sample(data_relation_1_relation_1_business_person_company, 250)
    sampled_data_relation_1_relation_1_location_country_capital = sample(data_relation_1_relation_1_location_country_capital, 250)
    sampled_data_relation_1_relation_1_location_location_contains = sample(data_relation_1_relation_1_location_location_contains, 250)
    sampled_data_relation_1_relation_1_location_us_state_capital = sample(data_relation_1_relation_1_location_us_state_capital, 250)
    sampled_data_relation_1_relation_1_people_ethnicity_geographic_distribution = sample(data_relation_1_relation_1_people_ethnicity_geographic_distribution, 250)
    sampled_data_relation_1_relation_1_people_person_children = sample(data_relation_1_relation_1_people_person_children, 250)
    sampled_data_relation_1_relation_1_people_person_nationality = sample(data_relation_1_relation_1_people_person_nationality, 250)
    sampled_data_relation_1_relation_1_people_person_place_lived = sample(data_relation_1_relation_1_people_person_place_lived, 250)


    final_data = data_relation_1_relation_1_rest + sampled_data_relation_1_relation_1_business_company_founders + \
    sampled_data_relation_1_relation_1_business_company_place_founded + sampled_data_relation_1_relation_1_business_person_company + \
    sampled_data_relation_1_relation_1_location_country_capital + sampled_data_relation_1_relation_1_location_location_contains + \
    sampled_data_relation_1_relation_1_location_us_state_capital + sampled_data_relation_1_relation_1_people_ethnicity_geographic_distribution + \
    sampled_data_relation_1_relation_1_people_person_children + sampled_data_relation_1_relation_1_people_person_nationality + \
    sampled_data_relation_1_relation_1_people_person_place_lived

    print(f"The length of positive_pairs: {len(final_data)}")

    
    # Step 3: Group (relation_1, no_relation) by relation_1 (ss_relation);
    #         Sample pairs according to relation_1_no_relation_num_needed and add them to final_data
    data_relation_1_no_relation_dict = defaultdict(list)
    for item in data_relation_1_no_relation:
        ss_relation = item['ss_relation']
        data_relation_1_no_relation_dict[ss_relation].append(item)
    
    for ss_relation, num_needed in relation_1_no_relation_num_needed.items():
        if ss_relation not in data_relation_1_no_relation_dict:
            print(f"Warning: relation '{ss_relation}' not found in (relation_1, no_relation) data.")
            continue
        candidate_pairs = data_relation_1_no_relation_dict[ss_relation]
        if len(candidate_pairs) < num_needed:
            print(f"Warning: relation '{ss_relation}' only has {len(candidate_pairs)} candidates, "
                  f"but {num_needed} needed. Sampling all.")
            sampled_pairs = candidate_pairs
        else:
            sampled_pairs = sample(candidate_pairs, num_needed)
        final_data.extend(sampled_pairs)

    # Step 4: Sample 7670 pairs from (relation_1, relation_2), keeping relations as balanced as possible (random sampling keeps original distribution), and add to final_data
    sampled_data_relation_1_relation_2 = sample(data_relation_1_relation_2, 7670)
    counter_sampled_data_relation_1_relation_2 = Counter()
    for item in sampled_data_relation_1_relation_2:
        ss_relation = item['ss_relation']
        ts_relation = item['ts_relation']
        counter_sampled_data_relation_1_relation_2[ss_relation] += 1
        counter_sampled_data_relation_1_relation_2[ts_relation] += 1
    print("The distribution of the sampled_data_relation_1_relation_2: ")
    print(counter_sampled_data_relation_1_relation_2)
    final_data += sampled_data_relation_1_relation_2

    # Step 5: Print info of final_data
    print(f"The length of final_data: {len(final_data)}")
    final_data_positive = []
    final_data_negative = []
    for item in final_data:
        if item['label'] == 'Yes':
            final_data_positive.append(item)
        else:
            final_data_negative.append(item)
    print(f"The length of final_data_positiva: {len(final_data_positive)}")
    print(f"The length of final_data_negative: {len(final_data_negative)}")
    ratio_positive_negative = len(final_data_negative) / len(final_data_positive)
    print(f"Positive to Negative ratio: {ratio_positive_negative}:1")
    return final_data

        




if __name__ == "__main__":
    input_dir = input("Please enter the path to the NYT29 train_episodes directory: ").strip()
    output_file = input("Please enter the path to save the sampled output JSONL file: ").strip()
    data = []
    for i in range(5):
        input_file = os.path.join(input_dir, f'val/5_way_1_shots_10K_episodes_3q_seed_16029{i}.jsonl')
        data = data + read_data(input_file)
    sampled_data = sampled_by_labels(data)
    write_to_jsonl(sampled_data, output_file)

    