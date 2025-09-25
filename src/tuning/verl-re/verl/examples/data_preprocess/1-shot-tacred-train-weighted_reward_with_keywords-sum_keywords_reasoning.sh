#!/bin/bash

export PYTHONPATH=../../..:$PYTHONPATH


# Run preprocessing script with all required arguments
python3 ./1-shot-tacred-train-weighted_reward_with_keywords-sum_keywords_reasoning.py \
  --train_data_source $(read -p "Enter the path to the training data JSONL file: " train_file && echo $train_file) \
  --test_data_source $(read -p "Enter the path to the test data JSONL file: " test_file && echo $test_file) \
  --local_dir $(read -p "Enter the local directory to save parquet files: " local_dir && echo $local_dir) \
