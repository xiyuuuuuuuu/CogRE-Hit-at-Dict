#!/usr/bin/env bash
set -x

### ---------- General Environment ----------
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export PYTHONPATH=../../..:$PYTHONPATH

export WANDB_MODE=offline
export RAY_memory_usage_threshold=0.995
export RAY_TMPDIR=../../../ray_tmp
# Cleaner Hydra logs
export HYDRA_FULL_ERROR=0
export HYDRA_MAIN_INFO=none

### ---------- 8×A100 80G ----------
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7   # Use 8 GPUs

# Base model and cache path (modify as needed for your setup)
export BASE_MODEL='Qwen2.5-14B-Instruct'
export BASE_MODEL_PATH="../../../models/${BASE_MODEL}"   # If pulling directly from HF, you can also set it as ${BASE_MODEL}

### ---------- Data paths (modify as needed for your setup) ----------
read -p "Enter the path to the training parquet file: " train_files
read -p "Enter the path to the test parquet file: " test_files

read -p "Enter the project name for logging: " project_name
read -p "Enter the experiment name: " experiment_name

### ---------- Training parameters: scaled for 8 GPUs ----------
# Originally train_batch_size=192 (on 4 GPUs), now doubled to 384; val scaled similarly
# PPO mini/micro batches also scaled accordingly to balance memory usage and efficiency
python3 -m verl.trainer.main_ppo \
    algorithm.adv_estimator=grpo \
    data.train_files="$train_files" \
    data.val_files="$test_files" \
    data.train_batch_size=384 \
    data.val_batch_size=64 \
    data.max_prompt_length=1280 \
    data.max_response_length=256 \
    data.filter_overlong_prompts=False \
    data.truncation='error' \
    \
    actor_rollout_ref.model.path="${BASE_MODEL_PATH}" \
    actor_rollout_ref.model.use_remove_padding=True \
    actor_rollout_ref.model.enable_gradient_checkpointing=True \
    \
    actor_rollout_ref.actor.optim.lr=1e-6 \
    actor_rollout_ref.actor.ppo_mini_batch_size=144 \
    actor_rollout_ref.actor.ppo_micro_batch_size=48 \
    actor_rollout_ref.actor.use_kl_loss=True \
    actor_rollout_ref.actor.kl_loss_coef=0.01 \
    actor_rollout_ref.actor.kl_loss_type=low_var_kl \
    actor_rollout_ref.actor.entropy_coeff=0.001 \
    actor_rollout_ref.actor.fsdp_config.param_offload=True \
    actor_rollout_ref.actor.fsdp_config.optimizer_offload=True \
    \
    actor_rollout_ref.rollout.name=vllm \
    actor_rollout_ref.rollout.tensor_model_parallel_size=4 \
    actor_rollout_ref.rollout.gpu_memory_utilization=0.85 \
    actor_rollout_ref.rollout.log_prob_micro_batch_size=64 \
    actor_rollout_ref.rollout.n=1 \
    \
    actor_rollout_ref.ref.log_prob_micro_batch_size=64 \
    actor_rollout_ref.ref.fsdp_config.param_offload=True \
    \
    algorithm.use_kl_in_reward=True \
    trainer.critic_warmup=0 \
    \
    trainer.logger=['console','wandb'] \
    trainer.project_name="$project_name" \
    trainer.experiment_name="$experiment_name" \
    \
    trainer.n_gpus_per_node=8 \
    trainer.nnodes=1 \
    \
    trainer.save_freq=50 \
    trainer.test_freq=10000 \
    trainer.total_epochs=15 
