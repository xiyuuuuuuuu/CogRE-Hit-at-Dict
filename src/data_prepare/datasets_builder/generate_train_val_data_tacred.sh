#!/bin/bash



# TACRED train
python ./generate_train_val_data_tacred.py \
    --dev/test_dir_path $(read -p "Enter the path to TACRED raw dataset: " tacred_dir && echo $tacred_dir) \
    --output_path $(read -p "Enter the output path for TACRED dataset: " tacred_out && echo $tacred_out) \
    --dev/test/train train_episodes


# # NYT29
# python ./generate_train_val_data_tacred.py \
#     --dev/test_dir_path $(read -p "Enter the path to NYT29 raw dataset: " nyt29_dir && echo $nyt29_dir) \
#     --output_path $(read -p "Enter the output path for NYT29 dataset: " nyt29_out && echo $nyt29_out) \
#     --dev/test train_episodes