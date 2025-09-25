export PYTHONPATH=../../:$PYTHONPATH

# need to edit
project_name="re_one-shot-tacred-weighted-reward-20k-1-7-sum_keywords_reasoning"
experiment_name="Phi-4_re_grpo"
step="global_step_300"
actor_or_crtic="actor"
grpo_or_ppo="GRPO"
# no need edit
checkpoints_dir="../../checkpoints/NYT29"
save_dir="../../checkpoints/save_models/GRPO/NYT29"
# mkdir output file path
mkdir -p "$save_dir/$grpo_or_ppo/$project_name/$experiment_name/$step/$actor_or_crtic"

python ./model_merger.py merge \
    --backend fsdp \
    --local_dir $checkpoints_dir/$project_name/$experiment_name/$step/$actor_or_crtic \
    --target_dir $save_dir/$project_name/$experiment_name/$step/$actor_or_crtic