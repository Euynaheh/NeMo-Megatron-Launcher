from omegaconf import OmegaConf


class TestTrainingmT5Config:
    def test_training_mt5_config_170m(self):
        conf = OmegaConf.load('conf/training/mt5/170m.yaml')
        s = """
run:
  name: mt5_170m
  results_dir: ${base_results_dir}/${.name}
  time_limit: "7-00:00:00"
  dependency: "singleton"
  preprocessed_dir: ${data_dir}/mc4/preprocessed # used for auto data blending
  blending_alpha: 0.7 # blending ratio across different languages; language sampling ratio ~L^alpha

name: megatron_mt5
restore_from_path: null # used when starting from a .nemo file

trainer:
  num_nodes: 4
  devices: 8
  accelerator: gpu
  precision: bf16
  logger: False # logger provided by exp_manager
  enable_checkpointing: False
  replace_sampler_ddp: False
  max_epochs: null
  max_steps: 1000000 # consumed_samples = global_step * global_batch_size
  max_time: "06:23:30:00"
  log_every_n_steps: 10
  val_check_interval: 2000
  limit_val_batches: 50
  limit_test_batches: 500
  accumulate_grad_batches: 1
  gradient_clip_val: 1.0


exp_manager:
  explicit_log_dir: ${training.run.results_dir}/results
  exp_dir: null
  name: megatron_mt5
  create_wandb_logger: False
  wandb_logger_kwargs:
    project: nemo_mt5
    name: ${training.run.name}
  resume_if_exists: True
  resume_ignore_no_checkpoint: True
  create_checkpoint_callback: True
  checkpoint_callback_params:
    monitor: val_loss
    save_top_k: 10
    mode: min
    always_save_nemo: False # saves nemo file during validation, not implemented for model parallel
    save_nemo_on_train_end: False # not recommended when training large models on clusters with short time limits
    filename: 'megatron_mt5--{val_loss:.2f}-{step}-{consumed_samples}'
    model_parallel_size: ${multiply:${training.model.tensor_model_parallel_size}, ${training.model.pipeline_model_parallel_size}}
  log_step_timing: True
  step_timing_kwargs:
    sync_cuda: True
    buffer_size: 5

model:
  # model parallelism
  micro_batch_size: 64
  global_batch_size: 2048 # will use more micro batches to reach global batch size
  tensor_model_parallel_size: 1
  pipeline_model_parallel_size: 1
  resume_from_checkpoint: null # manually set the checkpoint file to load from
  pipeline_model_parallel_split_rank: ${divide_floor:${.pipeline_model_parallel_size}, 2}

  # model architecture
  make_vocab_size_divisible_by: 128 # Pad the vocab size to be divisible by this value for computation efficiency.
  pre_process: True # add embedding
  post_process: True # add pooler

  megatron_amp_O2: True # use AMP with O2 style mixed precision instead of native amp on-the-fly weight autocasting.
  grad_allreduce_chunk_size_mb: 125
  gradient_as_bucket_view: True # Allocate gradients in a contiguous bucket to save memory (less fragmentation and buffer memory)

  seq_length: 512
  max_position_embeddings: ${.seq_length}

  encoder:
    num_layers: 8
    hidden_size: 512
    ffn_hidden_size: 1024  # Transformer FFN hidden size. 4 * hidden_size.
    num_attention_heads: 6
    kv_channels: 64  # Projection weights dimension in multi-head attention. Set to hidden_size // num_attention_heads if null
    init_method_std: 0.015  # Standard deviation of the zero mean normal distribution used for weight initialization.')
    hidden_dropout: 0.1  # Dropout probability for hidden state transformer.
    attention_dropout: 0.1 # Dropout probability in the attention layer.
    position_embedding_type: 'learned_absolute' # Position embedding type. Options ['learned_absolute', 'relative']
    relative_attention_num_buckets: 32 # Relative position number of buckets for computing the bias
    relative_attention_max_distance: 128 # max_distance to keep relative distance in the attention_num_buckets.
    relative_position_bias_self_attention_only: True # Whether to only use relative position bias for self attention only.
    apply_query_key_layer_scaling: True # scale Q * K^T by 1 / layer-number.
    layernorm_epsilon: 1e-5
    persist_layer_norm: True # Use of persistent fused layer norm kernel.
    bias_activation_fusion: True # Use a kernel that fuses the bias addition from weight matrices with the subsequent activation function.
    grad_div_ar_fusion: True # Fuse grad division into torch.distributed.all_reduce
    masked_softmax_fusion: True # Use a kernel that fuses the attention softmax with it's mask.
    bias_dropout_add_fusion: True # Use a kernel that fuses the bias addition, dropout and residual connection addition.
    bias: True # Whether to use bias terms in all weight matrices.
    normalization: 'layernorm' # Normalization layer to use. Options are 'layernorm', 'rmsnorm'
    arch: 'transformer' # Options: ['transformer', 'perceiver']
    activation: 'geglu' # Options ['gelu', 'geglu', 'swiglu', 'reglu']
    headscale: False # Whether to learn extra parameters that scale the output of the each self-attention head.
    transformer_block_type: 'pre_ln' # Options ['pre_ln', 'post_ln', 'normformer']
    openai_gelu: False # Use OpenAI's GELU instead of the default GeLU
    # miscellaneous
    onnx_safe: False # Use work-arounds for known problems with Torch ONNX exporter.
    fp32_residual_connection: False # Use FP32 for residual connections.
    # activations checkpointing
    activations_checkpoint_method: null # 'uniform', 'block'
    activations_checkpoint_num_layers: 0

  decoder:
    num_layers: 8
    hidden_size: 512
    ffn_hidden_size: 1024  # Transformer FFN hidden size. 4 * hidden_size.
    num_attention_heads: 6
    kv_channels: 64  # Projection weights dimension in multi-head attention. Set to hidden_size // num_attention_heads if null
    init_method_std: 0.015 # Standard deviation of the zero mean normal distribution used for weight initialization.')
    hidden_dropout: 0.1 # Dropout probability for hidden state transformer.
    attention_dropout: 0.1 # Dropout probability in the attention layer.
    position_embedding_type: 'learned_absolute' # Position embedding type. Options ['learned_absolute', 'relative']
    relative_attention_num_buckets: 32 # Relative position number of buckets for computing the bias
    relative_attention_max_distance: 128 # max_distance to keep relative distance in the attention_num_buckets.
    relative_position_bias_self_attention_only: True # Whether to only use relative position bias for self attention only.
    apply_query_key_layer_scaling: True # scale Q * K^T by 1 / layer-number.
    layernorm_epsilon: 1e-5
    persist_layer_norm: True # Use of persistent fused layer norm kernel.
    bias_activation_fusion: True # Use a kernel that fuses the bias addition from weight matrices with the subsequent activation function.
    grad_div_ar_fusion: True # Fuse grad division into torch.distributed.all_reduce
    masked_softmax_fusion: True # Use a kernel that fuses the attention softmax with it's mask.
    bias_dropout_add_fusion: True # Use a kernel that fuses the bias addition, dropout and residual connection addition.
    bias: True # Whether to use bias terms in all weight matrices.
    normalization: 'layernorm' # Normalization layer to use. Options are 'layernorm', 'rmsnorm'
    arch: 'transformer' # Options: ['transformer', 'perceiver']
    activation: 'geglu' # Options ['gelu', 'geglu', 'swiglu', 'reglu']
    headscale: False # Whether to learn extra parameters that scale the output of the each self-attention head.
    transformer_block_type: 'pre_ln' # Options ['pre_ln', 'post_ln', 'normformer']
    openai_gelu: False # Use OpenAI's GELU instead of the default GeLU
    # miscellaneous
    onnx_safe: False # Use work-arounds for known problems with Torch ONNX exporter.
    fp32_residual_connection: False # Use FP32 for residual connections.
    # activations checkpointing
    activations_checkpoint_method: null # 'uniform', 'block'
    activations_checkpoint_num_layers: 0

  tokenizer:
    library: 'sentencepiece'
    type: null
    model: ${data_dir}/mc4/bpe/mt5_tokenizer.model
    vocab_file: null
    merge_file: null
    num_sentinel_tokens: 100

  # precision
  native_amp_init_scale: 4294967296 # 2 ** 32
  native_amp_growth_interval: 1000
  fp16_lm_cross_entropy: False # Move the cross entropy unreduced loss calculation for lm head to fp16

  # miscellaneous
  seed: 1234
  use_cpu_initialization: False # Init weights on the CPU (slow for large models)
  apex_transformer_log_level: 30 # Python logging level displays logs with severity greater than or equal to this


  # embedding sharing
  share_token_embeddings: True # If True share encoder/decoder embeddings
  share_decoder_tokens_head_embeddings: True # If True share decoder embeddings and decoder projection to logits

  nsys_profile:
    enabled: False
    trace: [nvtx,cuda]
    start_step: 10  # Global batch to start profiling
    end_step: 10 # Global batch to end profiling
    ranks: [0] # Global rank IDs to profile
    gen_shape: False # Generate model and kernel details including input shapes

  optim:
    name: distributed_fused_adam
    bucket_cap_mb: ${training.model.grad_allreduce_chunk_size_mb}
    lr: 0.0001
    betas:
      - 0.9
      - 0.999
    eps: 1e-8
    weight_decay: 0.01
    sched:
      name: WarmupAnnealing
      min_lr: 0.00001
      last_epoch: -1
      warmup_ratio: 0.01


  data:
    data_impl: mmap
    splits_string: "999892,99,9"
    seq_length: 512
    seq_length_dec: 128
    skip_warmup: True
    num_workers: 8
    dataloader_type: single # cyclic
    masked_lm_prob: 0.15
    dataset_type: 't5'
    short_seq_prob: 0.0
    max_ngram_size: 10
    mean_ngram_size: null
    geometric_dist: True
    permutation: False
    whole_word_masking: False
    favor_longer_ngrams: False
    respect_document_boundaries: True # If true, a single training exampl cannot cross document boundaries, increasing the fraction of <pad> tokens within a batch.
    index_mapping_dir: null # path to save index mapping .npy files, by default will save in the same location as data_prefix
    data_prefix: null # Should be weight path weight path... for a blended dataset. If null will automatically blend all language files in mC4_dir.
        """
        expected = OmegaConf.create(s)
        assert expected == conf, f"conf/training/mt5/170m.yaml must be set to {expected} but it currently is {conf}."

    def test_training_mt5_config_390m(self):
        conf = OmegaConf.load('conf/training/mt5/390m.yaml')
        s = """
run:
  name: mt5_390m
  results_dir: ${base_results_dir}/${.name}
  time_limit: "7-00:00:00"
  dependency: "singleton"
  preprocessed_dir: ${data_dir}/mc4/preprocessed # used for auto data blending
  blending_alpha: 0.7 # blending ratio across different languages; language sampling ratio ~L^alpha

name: megatron_mt5
restore_from_path: null # used when starting from a .nemo file

trainer:
  num_nodes: 8
  devices: 8
  accelerator: gpu
  precision: bf16
  logger: False # logger provided by exp_manager
  enable_checkpointing: False
  replace_sampler_ddp: False
  max_epochs: null
  max_steps: 1000000 # consumed_samples = global_step * global_batch_size
  max_time: "06:23:30:00"
  log_every_n_steps: 10
  val_check_interval: 2000
  limit_val_batches: 50
  limit_test_batches: 500
  accumulate_grad_batches: 1
  gradient_clip_val: 1.0


exp_manager:
  explicit_log_dir: ${training.run.results_dir}/results
  exp_dir: null
  name: megatron_mt5
  create_wandb_logger: False
  wandb_logger_kwargs:
    project: nemo_mt5
    name: ${training.run.name}
  resume_if_exists: True
  resume_ignore_no_checkpoint: True
  create_checkpoint_callback: True
  checkpoint_callback_params:
    monitor: val_loss
    save_top_k: 10
    mode: min
    always_save_nemo: False # saves nemo file during validation, not implemented for model parallel
    save_nemo_on_train_end: False # not recommended when training large models on clusters with short time limits
    filename: 'megatron_mt5--{val_loss:.2f}-{step}-{consumed_samples}'
    model_parallel_size: ${multiply:${training.model.tensor_model_parallel_size}, ${training.model.pipeline_model_parallel_size}}
  log_step_timing: True
  step_timing_kwargs:
    sync_cuda: True
    buffer_size: 5

model:
  # model parallelism
  micro_batch_size: 32
  global_batch_size: 2048 # will use more micro batches to reach global batch size
  tensor_model_parallel_size: 1
  pipeline_model_parallel_size: 1
  resume_from_checkpoint: null # manually set the checkpoint file to load from
  pipeline_model_parallel_split_rank: ${divide_floor:${.pipeline_model_parallel_size}, 2}

  # model architecture
  make_vocab_size_divisible_by: 128 # Pad the vocab size to be divisible by this value for computation efficiency.
  pre_process: True # add embedding
  post_process: True # add pooler

  megatron_amp_O2: True # use AMP with O2 style mixed precision instead of native amp on-the-fly weight autocasting.
  grad_allreduce_chunk_size_mb: 125
  gradient_as_bucket_view: True # Allocate gradients in a contiguous bucket to save memory (less fragmentation and buffer memory)

  seq_length: 512
  max_position_embeddings: ${.seq_length}

  encoder:
    num_layers: 12
    hidden_size: 768
    ffn_hidden_size: 2048  # Transformer FFN hidden size. 4 * hidden_size.
    num_attention_heads: 12
    kv_channels: 64  # Projection weights dimension in multi-head attention. Set to hidden_size // num_attention_heads if null
    init_method_std: 0.015  # Standard deviation of the zero mean normal distribution used for weight initialization.')
    hidden_dropout: 0.1  # Dropout probability for hidden state transformer.
    attention_dropout: 0.1 # Dropout probability in the attention layer.
    position_embedding_type: 'learned_absolute' # Position embedding type. Options ['learned_absolute', 'relative']
    relative_attention_num_buckets: 32 # Relative position number of buckets for computing the bias
    relative_attention_max_distance: 128 # max_distance to keep relative distance in the attention_num_buckets.
    relative_position_bias_self_attention_only: True # Whether to only use relative position bias for self attention only.
    apply_query_key_layer_scaling: True # scale Q * K^T by 1 / layer-number.
    layernorm_epsilon: 1e-5
    persist_layer_norm: True # Use of persistent fused layer norm kernel.
    bias_activation_fusion: True # Use a kernel that fuses the bias addition from weight matrices with the subsequent activation function.
    grad_div_ar_fusion: True # Fuse grad division into torch.distributed.all_reduce
    masked_softmax_fusion: True # Use a kernel that fuses the attention softmax with it's mask.
    bias_dropout_add_fusion: True # Use a kernel that fuses the bias addition, dropout and residual connection addition.
    bias: True # Whether to use bias terms in all weight matrices.
    normalization: 'layernorm' # Normalization layer to use. Options are 'layernorm', 'rmsnorm'
    arch: 'transformer' # Options: ['transformer', 'perceiver']
    activation: 'geglu' # Options ['gelu', 'geglu', 'swiglu', 'reglu']
    headscale: False # Whether to learn extra parameters that scale the output of the each self-attention head.
    transformer_block_type: 'pre_ln' # Options ['pre_ln', 'post_ln', 'normformer']
    openai_gelu: False # Use OpenAI's GELU instead of the default GeLU
    # miscellaneous
    onnx_safe: False # Use work-arounds for known problems with Torch ONNX exporter.
    fp32_residual_connection: False # Use FP32 for residual connections.
    # activations checkpointing
    activations_checkpoint_method: null # 'uniform', 'block'
    activations_checkpoint_num_layers: 0

  decoder:
    num_layers: 12
    hidden_size: 768
    ffn_hidden_size: 2048  # Transformer FFN hidden size. 4 * hidden_size.
    num_attention_heads: 12
    kv_channels: 64  # Projection weights dimension in multi-head attention. Set to hidden_size // num_attention_heads if null
    init_method_std: 0.015 # Standard deviation of the zero mean normal distribution used for weight initialization.')
    hidden_dropout: 0.1 # Dropout probability for hidden state transformer.
    attention_dropout: 0.1 # Dropout probability in the attention layer.
    position_embedding_type: 'learned_absolute' # Position embedding type. Options ['learned_absolute', 'relative']
    relative_attention_num_buckets: 32 # Relative position number of buckets for computing the bias
    relative_attention_max_distance: 128 # max_distance to keep relative distance in the attention_num_buckets.
    relative_position_bias_self_attention_only: True # Whether to only use relative position bias for self attention only.
    apply_query_key_layer_scaling: True # scale Q * K^T by 1 / layer-number.
    layernorm_epsilon: 1e-5
    persist_layer_norm: True # Use of persistent fused layer norm kernel.
    bias_activation_fusion: True # Use a kernel that fuses the bias addition from weight matrices with the subsequent activation function.
    grad_div_ar_fusion: True # Fuse grad division into torch.distributed.all_reduce
    masked_softmax_fusion: True # Use a kernel that fuses the attention softmax with it's mask.
    bias_dropout_add_fusion: True # Use a kernel that fuses the bias addition, dropout and residual connection addition.
    bias: True # Whether to use bias terms in all weight matrices.
    normalization: 'layernorm' # Normalization layer to use. Options are 'layernorm', 'rmsnorm'
    arch: 'transformer' # Options: ['transformer', 'perceiver']
    activation: 'geglu' # Options ['gelu', 'geglu', 'swiglu', 'reglu']
    headscale: False # Whether to learn extra parameters that scale the output of the each self-attention head.
    transformer_block_type: 'pre_ln' # Options ['pre_ln', 'post_ln', 'normformer']
    openai_gelu: False # Use OpenAI's GELU instead of the default GeLU
    # miscellaneous
    onnx_safe: False # Use work-arounds for known problems with Torch ONNX exporter.
    fp32_residual_connection: False # Use FP32 for residual connections.
    # activations checkpointing
    activations_checkpoint_method: null # 'uniform', 'block'
    activations_checkpoint_num_layers: 0

  tokenizer:
    library: 'sentencepiece'
    type: null
    model: ${data_dir}/mc4/bpe/mt5_tokenizer.model
    vocab_file: null
    merge_file: null
    num_sentinel_tokens: 100

  # precision
  native_amp_init_scale: 4294967296 # 2 ** 32
  native_amp_growth_interval: 1000
  fp16_lm_cross_entropy: False # Move the cross entropy unreduced loss calculation for lm head to fp16

  # miscellaneous
  seed: 1234
  use_cpu_initialization: False # Init weights on the CPU (slow for large models)
  apex_transformer_log_level: 30 # Python logging level displays logs with severity greater than or equal to this


  # embedding sharing
  share_token_embeddings: True # If True share encoder/decoder embeddings
  share_decoder_tokens_head_embeddings: True # If True share decoder embeddings and decoder projection to logits

  nsys_profile:
    enabled: False
    trace: [nvtx,cuda]
    start_step: 10  # Global batch to start profiling
    end_step: 10 # Global batch to end profiling
    ranks: [0] # Global rank IDs to profile
    gen_shape: False # Generate model and kernel details including input shapes

  optim:
    name: distributed_fused_adam
    bucket_cap_mb: ${training.model.grad_allreduce_chunk_size_mb}
    lr: 0.0001
    betas:
      - 0.9
      - 0.999
    eps: 1e-8
    weight_decay: 0.01
    sched:
      name: WarmupAnnealing
      min_lr: 0.00001
      last_epoch: -1
      warmup_ratio: 0.01


  data:
    data_impl: mmap
    splits_string: "999892,99,9"
    seq_length: 512
    seq_length_dec: 128
    skip_warmup: True
    num_workers: 8
    dataloader_type: single # cyclic
    masked_lm_prob: 0.15
    dataset_type: 't5'
    short_seq_prob: 0.0
    max_ngram_size: 10
    mean_ngram_size: null
    geometric_dist: True
    permutation: False
    whole_word_masking: False
    favor_longer_ngrams: False
    respect_document_boundaries: True # If true, a single training exampl cannot cross document boundaries, increasing the fraction of <pad> tokens within a batch.
    index_mapping_dir: null # path to save index mapping .npy files, by default will save in the same location as data_prefix
    data_prefix: null # Should be weight path weight path... for a blended dataset. If null will automatically blend all language files in mC4_dir.
         """
        expected = OmegaConf.create(s)
        assert expected == conf, f"conf/training/mt5/390m.yaml must be set to {expected} but it currently is {conf}."

    def test_training_mt5_config_3b(self):
        conf = OmegaConf.load('conf/training/mt5/3b.yaml')
        s = """
run:
  name: mt5_3b
  results_dir: ${base_results_dir}/${.name}
  time_limit: "18-00:00:00"
  dependency: "singleton"
  preprocessed_dir: ${data_dir}/mc4/preprocessed # used for auto data blending
  blending_alpha: 0.7 # blending ratio across different languages; language sampling ratio ~L^alpha

name: megatron_mt5
restore_from_path: null # used when starting from a .nemo file

trainer:
  num_nodes: 20
  devices: 8
  accelerator: gpu
  precision: bf16
  logger: False # logger provided by exp_manager
  enable_checkpointing: False
  replace_sampler_ddp: False
  max_epochs: null
  max_steps: 1066667 # consumed_samples = global_step * global_batch_size
  max_time: "17:23:30:00"
  log_every_n_steps: 10
  val_check_interval: 2000
  limit_val_batches: 50
  limit_test_batches: 500
  accumulate_grad_batches: 1
  gradient_clip_val: 1.0


exp_manager:
  explicit_log_dir: ${training.run.results_dir}/results
  exp_dir: null
  name: megatron_mt5
  create_wandb_logger: False
  wandb_logger_kwargs:
    project: nemo_mt5
    name: ${training.run.name}
  resume_if_exists: True
  resume_ignore_no_checkpoint: True
  create_checkpoint_callback: True
  checkpoint_callback_params:
    monitor: val_loss
    save_top_k: 10
    mode: min
    always_save_nemo: False # saves nemo file during validation, not implemented for model parallel
    save_nemo_on_train_end: False # not recommended when training large models on clusters with short time limits
    filename: 'megatron_mt5--{val_loss:.2f}-{step}-{consumed_samples}'
    model_parallel_size: ${multiply:${training.model.tensor_model_parallel_size}, ${training.model.pipeline_model_parallel_size}}
  log_step_timing: True
  step_timing_kwargs:
    sync_cuda: True
    buffer_size: 5

model:
  # model parallelism
  micro_batch_size: 24
  global_batch_size: 1920 # will use more micro batches to reach global batch size
  tensor_model_parallel_size: 2
  pipeline_model_parallel_size: 1
  resume_from_checkpoint: null # manually set the checkpoint file to load from
  pipeline_model_parallel_split_rank: ${divide_floor:${.pipeline_model_parallel_size}, 2}

  # model architecture
  make_vocab_size_divisible_by: 128 # Pad the vocab size to be divisible by this value for computation efficiency.
  pre_process: True # add embedding
  post_process: True # add pooler

  megatron_amp_O2: True # use AMP with O2 style mixed precision instead of native amp on-the-fly weight autocasting.
  grad_allreduce_chunk_size_mb: 125
  gradient_as_bucket_view: True # Allocate gradients in a contiguous bucket to save memory (less fragmentation and buffer memory)

  seq_length: 512
  max_position_embeddings: ${.seq_length}

  encoder:
    num_layers: 24
    hidden_size: 2048
    ffn_hidden_size: 5120  # Transformer FFN hidden size. 4 * hidden_size.
    num_attention_heads: 32
    kv_channels: 64  # Projection weights dimension in multi-head attention. Set to hidden_size // num_attention_heads if null
    init_method_std: 0.015  # Standard deviation of the zero mean normal distribution used for weight initialization.')
    hidden_dropout: 0.1  # Dropout probability for hidden state transformer.
    attention_dropout: 0.1 # Dropout probability in the attention layer.
    position_embedding_type: 'learned_absolute' # Position embedding type. Options ['learned_absolute', 'relative']
    relative_attention_num_buckets: 32 # Relative position number of buckets for computing the bias
    relative_attention_max_distance: 128 # max_distance to keep relative distance in the attention_num_buckets.
    relative_position_bias_self_attention_only: True # Whether to only use relative position bias for self attention only.
    apply_query_key_layer_scaling: True # scale Q * K^T by 1 / layer-number.
    layernorm_epsilon: 1e-5
    persist_layer_norm: True # Use of persistent fused layer norm kernel.
    bias_activation_fusion: True # Use a kernel that fuses the bias addition from weight matrices with the subsequent activation function.
    grad_div_ar_fusion: True # Fuse grad division into torch.distributed.all_reduce
    masked_softmax_fusion: True # Use a kernel that fuses the attention softmax with it's mask.
    bias_dropout_add_fusion: True # Use a kernel that fuses the bias addition, dropout and residual connection addition.
    bias: True # Whether to use bias terms in all weight matrices.
    normalization: 'layernorm' # Normalization layer to use. Options are 'layernorm', 'rmsnorm'
    arch: 'transformer' # Options: ['transformer', 'perceiver']
    activation: 'geglu' # Options ['gelu', 'geglu', 'swiglu', 'reglu']
    headscale: False # Whether to learn extra parameters that scale the output of the each self-attention head.
    transformer_block_type: 'pre_ln' # Options ['pre_ln', 'post_ln', 'normformer']
    openai_gelu: False # Use OpenAI's GELU instead of the default GeLU
    # miscellaneous
    onnx_safe: False # Use work-arounds for known problems with Torch ONNX exporter.
    fp32_residual_connection: False # Use FP32 for residual connections.
    # activations checkpointing
    activations_checkpoint_method: null # 'uniform', 'block'
    activations_checkpoint_num_layers: 0

  decoder:
    num_layers: 24
    hidden_size: 2048
    ffn_hidden_size: 5120  # Transformer FFN hidden size. 4 * hidden_size.
    num_attention_heads: 32
    kv_channels: 64  # Projection weights dimension in multi-head attention. Set to hidden_size // num_attention_heads if null
    init_method_std: 0.015 # Standard deviation of the zero mean normal distribution used for weight initialization.')
    hidden_dropout: 0.1 # Dropout probability for hidden state transformer.
    attention_dropout: 0.1 # Dropout probability in the attention layer.
    position_embedding_type: 'learned_absolute' # Position embedding type. Options ['learned_absolute', 'relative']
    relative_attention_num_buckets: 32 # Relative position number of buckets for computing the bias
    relative_attention_max_distance: 128 # max_distance to keep relative distance in the attention_num_buckets.
    relative_position_bias_self_attention_only: True # Whether to only use relative position bias for self attention only.
    apply_query_key_layer_scaling: True # scale Q * K^T by 1 / layer-number.
    layernorm_epsilon: 1e-5
    persist_layer_norm: True # Use of persistent fused layer norm kernel.
    bias_activation_fusion: True # Use a kernel that fuses the bias addition from weight matrices with the subsequent activation function.
    grad_div_ar_fusion: True # Fuse grad division into torch.distributed.all_reduce
    masked_softmax_fusion: True # Use a kernel that fuses the attention softmax with it's mask.
    bias_dropout_add_fusion: True # Use a kernel that fuses the bias addition, dropout and residual connection addition.
    bias: True # Whether to use bias terms in all weight matrices.
    normalization: 'layernorm' # Normalization layer to use. Options are 'layernorm', 'rmsnorm'
    arch: 'transformer' # Options: ['transformer', 'perceiver']
    activation: 'geglu' # Options ['gelu', 'geglu', 'swiglu', 'reglu']
    headscale: False # Whether to learn extra parameters that scale the output of the each self-attention head.
    transformer_block_type: 'pre_ln' # Options ['pre_ln', 'post_ln', 'normformer']
    openai_gelu: False # Use OpenAI's GELU instead of the default GeLU
    # miscellaneous
    onnx_safe: False # Use work-arounds for known problems with Torch ONNX exporter.
    fp32_residual_connection: False # Use FP32 for residual connections.
    # activations checkpointing
    activations_checkpoint_method: null # 'uniform', 'block'
    activations_checkpoint_num_layers: 0

  tokenizer:
    library: 'sentencepiece'
    type: null
    model: ${data_dir}/mc4/bpe/mt5_tokenizer.model
    vocab_file: null
    merge_file: null
    num_sentinel_tokens: 100

  # precision
  native_amp_init_scale: 4294967296 # 2 ** 32
  native_amp_growth_interval: 1000
  fp16_lm_cross_entropy: False # Move the cross entropy unreduced loss calculation for lm head to fp16

  # miscellaneous
  seed: 1234
  use_cpu_initialization: False # Init weights on the CPU (slow for large models)
  apex_transformer_log_level: 30 # Python logging level displays logs with severity greater than or equal to this


  # embedding sharing
  share_token_embeddings: True # If True share encoder/decoder embeddings
  share_decoder_tokens_head_embeddings: True # If True share decoder embeddings and decoder projection to logits
  
  nsys_profile:
    enabled: False
    trace: [nvtx,cuda]
    start_step: 10  # Global batch to start profiling
    end_step: 10 # Global batch to end profiling
    ranks: [0] # Global rank IDs to profile
    gen_shape: False # Generate model and kernel details including input shapes

  optim:
    name: distributed_fused_adam
    bucket_cap_mb: ${training.model.grad_allreduce_chunk_size_mb}
    lr: 0.0001
    betas:
      - 0.9
      - 0.999
    eps: 1e-8
    weight_decay: 0.01
    sched:
      name: WarmupAnnealing
      min_lr: 0.00001
      last_epoch: -1
      warmup_ratio: 0.01


  data:
    data_impl: mmap
    splits_string: "999892,99,9"
    seq_length: 512
    seq_length_dec: 128
    skip_warmup: True
    num_workers: 8
    dataloader_type: single # cyclic
    masked_lm_prob: 0.15
    dataset_type: 't5'
    short_seq_prob: 0.0
    max_ngram_size: 10
    mean_ngram_size: null
    geometric_dist: True
    permutation: False
    whole_word_masking: False
    favor_longer_ngrams: False
    respect_document_boundaries: True # If true, a single training exampl cannot cross document boundaries, increasing the fraction of <pad> tokens within a batch.
    index_mapping_dir: null # path to save index mapping .npy files, by default will save in the same location as data_prefix
    data_prefix: null # Should be weight path weight path... for a blended dataset. If null will automatically blend all language files in mC4_dir.
        """
        expected = OmegaConf.create(s)
        assert expected == conf, f"conf/training/mt5/3b.yaml must be set to {expected} but it currently is {conf}."
