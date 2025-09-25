import re

def extract_differ(line):
    """
    Check if the line contains 'differ' or 'different' (case insensitive).
    """
    pattern = re.compile(r'\bdiffer\w*\b', re.IGNORECASE)
    return bool(pattern.search(line))

def extract_solution(solution_str):
    """
    Extract 'Yes' or 'No' from the final line of model output .
    """
    last_answer = None
    is_differ_exited = False
    # If last_answer is None, traverse full_content backward to find the first Yes or No
    for line in reversed(solution_str.strip().splitlines()):
        # For each line, also extract the last Yes/No
        line = line.strip()
        # Skip if it's an empty line
        if not line:  
            continue
        # Traverse each word in the line in reverse order
        for word in reversed(line.split()):
            if word.lower() in ['yes', 'no']:
                last_answer = word.capitalize()
                is_differ_exited = extract_differ(line)
                break
        # If the answer is found, break the loop
        if last_answer is not None:
            break
    # If still not found, check whether "yes" or "no" exists in the string
    if last_answer is None:
        # Search "yes" or "no" in the full_content
        if 'yes' in solution_str.lower():
            last_answer = 'Yes'
        elif 'no' in solution_str.lower():
            last_answer = 'No'
    # If the last line contains 'differ' or 'different', then set last_answer='No'
    return last_answer, is_differ_exited

def compute_score(solution_str, ground_truth, format_score=0.0, score=1.0):
    """
    Compare extracted answer with ground truth. Return full score if match, partial score otherwise.
    """
    answer, is_differ_exited = extract_solution(solution_str=solution_str)

    # No answer given, assign 0 score
    if answer is None:
        return 0.0  

    # consistency test
    # if answer == "Yes" and is_differ_exited:
    #     return 0.0
    
    if answer == "Yes" and ground_truth == "Yes":   # correct_yes
        return 3.0
    elif answer == "Yes" and ground_truth == "No":  # wrong_yes
        return -3.0
    elif answer == "No" and ground_truth == "No":   # correct_no
        return 1.0
    elif answer == "No" and ground_truth == "Yes":  # wrong_no
        return -1.0
    else:
        # Fallback case (e.g., ground_truth is not Yes/No)
        return 0.0 