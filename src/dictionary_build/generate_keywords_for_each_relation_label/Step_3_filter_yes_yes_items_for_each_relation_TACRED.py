import json

relation_labels = [
    "org:alternate_names",
    "org:city_of_headquarters",
    "org:dissolved",
    "org:members",
    "org:number_of_employees/members",
    "org:political/religious_affiliation",
    "org:shareholders",
    "org:stateorprovince_of_headquarters",
    "org:subsidiaries",
    "org:website",
    "per:cause_of_death",
    "per:charges",
    "per:cities_of_residence",
    "per:city_of_birth",
    "per:countries_of_residence",
    "per:country_of_birth",
    "per:country_of_death",
    "per:date_of_death",
    "per:employee_of",
    "per:other_family",
    "per:parents",
    "per:religion",
    "per:spouse",
    "per:stateorprovince_of_birth",
    "per:title",
    "no_relation"
]

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

def filter_yes_yes_items(data):
    """
    Filter all the items with answer "Yes".
    """
    yes_yes_data = [item for item in data if item['answer']=='Yes']
    return yes_yes_data

def devide_yes_yes_items_by_relation(yes_yes_data):
    """
    Devide the yes_yes items by relation.
    """
    relation_dict = {}
    for item in yes_yes_data:
        relation = item['ts_relation']
        if relation not in relation_dict:
            relation_dict[relation] = []
        relation_dict[relation].append(item)
    # print the number of items for each relation
    for relation, items in relation_dict.items():
        print(f"Relation: {relation}, Number of items: {len(items)}")
    # each relation remain two items
    relation_with_answer_cases = []
    for relation, items in relation_dict.items():
        if len(items) >= 2:
            relation_with_answer_cases.append({
                "relation": relation,
                "cases": items[:2]
            })
        else:
            relation_with_answer_cases.append({
                "relation": relation,
                "cases": items
            })
    return relation_with_answer_cases



def main():
    input_file = input("Please enter the path to the input JSONL file: ").strip()
    positive_data = read_data(input_file)
    yes_yes_data = filter_yes_yes_items(positive_data)
    print(f"Positive items: {len(positive_data)}, Yes_Yes items: {len(yes_yes_data)}")
    relation_with_answer_cases = devide_yes_yes_items_by_relation(yes_yes_data)
    output_file = input("Please enter the path to save the relation cases JSONL file: ").strip()
    write_to_jsonl(relation_with_answer_cases, output_file)


if __name__ == "__main__":
    main()
