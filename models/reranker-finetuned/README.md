---
tags:
- sentence-transformers
- cross-encoder
- reranker
- generated_from_trainer
- dataset_size:9500
- loss:BinaryCrossEntropyLoss
base_model: cross-encoder/mmarco-mMiniLMv2-L12-H384-v1
pipeline_tag: text-ranking
library_name: sentence-transformers
metrics:
- accuracy
- accuracy_threshold
- f1
- f1_threshold
- precision
- recall
- average_precision
model-index:
- name: CrossEncoder based on cross-encoder/mmarco-mMiniLMv2-L12-H384-v1
  results:
  - task:
      type: cross-encoder-binary-classification
      name: Cross Encoder Binary Classification
    dataset:
      name: reranker eval
      type: reranker_eval
    metrics:
    - type: accuracy
      value: 0.81
      name: Accuracy
    - type: accuracy_threshold
      value: 1.9531536102294922
      name: Accuracy Threshold
    - type: f1
      value: 0.8047808764940239
      name: F1
    - type: f1_threshold
      value: -1.18611478805542
      name: F1 Threshold
    - type: precision
      value: 0.7890625
      name: Precision
    - type: recall
      value: 0.8211382113821138
      name: Recall
    - type: average_precision
      value: 0.9071608589039756
      name: Average Precision
---

# CrossEncoder based on cross-encoder/mmarco-mMiniLMv2-L12-H384-v1

This is a [Cross Encoder](https://www.sbert.net/docs/cross_encoder/usage/usage.html) model finetuned from [cross-encoder/mmarco-mMiniLMv2-L12-H384-v1](https://huggingface.co/cross-encoder/mmarco-mMiniLMv2-L12-H384-v1) using the [sentence-transformers](https://www.SBERT.net) library. It computes scores for pairs of texts, which can be used for text reranking and semantic search.

## Model Details

### Model Description
- **Model Type:** Cross Encoder
- **Base model:** [cross-encoder/mmarco-mMiniLMv2-L12-H384-v1](https://huggingface.co/cross-encoder/mmarco-mMiniLMv2-L12-H384-v1) <!-- at revision 1427fd652930e4ba29e8149678df786c240d8825 -->
- **Maximum Sequence Length:** 256 tokens
- **Number of Output Labels:** 1 label
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Documentation:** [Cross Encoder Documentation](https://www.sbert.net/docs/cross_encoder/usage/usage.html)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/huggingface/sentence-transformers)
- **Hugging Face:** [Cross Encoders on Hugging Face](https://huggingface.co/models?library=sentence-transformers&other=cross-encoder)

## Usage

### Direct Usage (Sentence Transformers)

First install the Sentence Transformers library:

```bash
pip install -U sentence-transformers
```

Then you can load this model and run inference.
```python
from sentence_transformers import CrossEncoder

# Download from the 🤗 Hub
model = CrossEncoder("cross_encoder_model_id")
# Get scores for pairs of texts
pairs = [
    ['Làm thế nào để biết rằng tai nghe Bluetooth tôi mua là hàng chính hãng?', 'Có một số cách để biết rằng tai nghe Bluetooth bạn mua là hàng chính hãng:\n\n- **Kiểm tra bao bì**: Bao bì của tai nghe chính hãng thường được thiết kế cẩn thận và có đầy đủ thông tin về sản phẩm. Hãy kiểm tra xem bao bì có bị hư hỏng hoặc có dấu hiệu tái sử dụng không.\n- **Kiểm tra sản phẩm**: Khi mở hộp tai nghe, hãy kiểm tra xem sản phẩm có bị trầy xước hoặc hư hỏng không. Bạn cũng nên kiểm tra xem các phụ kiện đi kèm có đầy đủ không.\n- **Kiểm tra số sê-ri**: Mỗi sản phẩm chính hãng đều có một số sê-ri duy nhất. Bạn có thể kiểm tra số sê-ri này trên trang web của nhà sản xuất để xác nhận tính hợp lệ của sản phẩm.\n- **Mua từ nhà bán lẻ uy tín**: Hãy mua tai nghe Bluetooth từ các nhà bán lẻ uy tín để đảm bảo rằng bạn mua được hàng chính hãng.'],
    ['Làm thế nào để tránh sử dụng dầu ăn bị oxy hóa?', 'Để tránh sử dụng dầu ăn bị oxy hóa, bạn nên chọn dầu ăn có nguồn gốc rõ ràng, không mua dầu ăn đã để quá lâu. Không nên chiên rán thực phẩm ở nhiệt độ quá cao, nên sử dụng dầu ăn một lần và không nên tái sử dụng nhiều lần.'],
    ['sao mình không đăng nhập được ạ.', 'Cám ơn bạn đã nhắn tin cho DooPage, chúng tôi sẽ sớm phản hồi lại tin nhắn của bạn. Nếu bạn có thắc mắc gì chỉ cần bấm nút "Gặp quản trị viên".'],
    ['đây nó cứ hiện như thế này.', 'dạ vâng, anh chờ em báo case của mình cho phía dev check trên hệ thống ạ.'],
    ['em liên hệ a để hướng dẫn được không.', 'chị có thể gửi email về địa chỉ <email> giúp em ạ.'],
]
scores = model.predict(pairs)
print(scores.shape)
# (5,)

# Or rank different texts based on similarity to a single text
ranks = model.rank(
    'Làm thế nào để biết rằng tai nghe Bluetooth tôi mua là hàng chính hãng?',
    [
        'Có một số cách để biết rằng tai nghe Bluetooth bạn mua là hàng chính hãng:\n\n- **Kiểm tra bao bì**: Bao bì của tai nghe chính hãng thường được thiết kế cẩn thận và có đầy đủ thông tin về sản phẩm. Hãy kiểm tra xem bao bì có bị hư hỏng hoặc có dấu hiệu tái sử dụng không.\n- **Kiểm tra sản phẩm**: Khi mở hộp tai nghe, hãy kiểm tra xem sản phẩm có bị trầy xước hoặc hư hỏng không. Bạn cũng nên kiểm tra xem các phụ kiện đi kèm có đầy đủ không.\n- **Kiểm tra số sê-ri**: Mỗi sản phẩm chính hãng đều có một số sê-ri duy nhất. Bạn có thể kiểm tra số sê-ri này trên trang web của nhà sản xuất để xác nhận tính hợp lệ của sản phẩm.\n- **Mua từ nhà bán lẻ uy tín**: Hãy mua tai nghe Bluetooth từ các nhà bán lẻ uy tín để đảm bảo rằng bạn mua được hàng chính hãng.',
        'Để tránh sử dụng dầu ăn bị oxy hóa, bạn nên chọn dầu ăn có nguồn gốc rõ ràng, không mua dầu ăn đã để quá lâu. Không nên chiên rán thực phẩm ở nhiệt độ quá cao, nên sử dụng dầu ăn một lần và không nên tái sử dụng nhiều lần.',
        'Cám ơn bạn đã nhắn tin cho DooPage, chúng tôi sẽ sớm phản hồi lại tin nhắn của bạn. Nếu bạn có thắc mắc gì chỉ cần bấm nút "Gặp quản trị viên".',
        'dạ vâng, anh chờ em báo case của mình cho phía dev check trên hệ thống ạ.',
        'chị có thể gửi email về địa chỉ <email> giúp em ạ.',
    ]
)
# [{'corpus_id': ..., 'score': ...}, {'corpus_id': ..., 'score': ...}, ...]
```

<!--
### Direct Usage (Transformers)

<details><summary>Click to see the direct usage in Transformers</summary>

</details>
-->

<!--
### Downstream Usage (Sentence Transformers)

You can finetune this model on your own dataset.

<details><summary>Click to expand</summary>

</details>
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

## Evaluation

### Metrics

#### Cross Encoder Binary Classification

* Dataset: `reranker_eval`
* Evaluated with [<code>CEBinaryClassificationEvaluator</code>](https://sbert.net/docs/package_reference/cross_encoder/evaluation.html#sentence_transformers.cross_encoder.evaluation.CEBinaryClassificationEvaluator)

| Metric                | Value      |
|:----------------------|:-----------|
| accuracy              | 0.81       |
| accuracy_threshold    | 1.9532     |
| f1                    | 0.8048     |
| f1_threshold          | -1.1861    |
| precision             | 0.7891     |
| recall                | 0.8211     |
| **average_precision** | **0.9072** |

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Dataset

#### Unnamed Dataset

* Size: 9,500 training samples
* Columns: <code>sentence_0</code>, <code>sentence_1</code>, and <code>label</code>
* Approximate statistics based on the first 1000 samples:
  |         | sentence_0                                                                                      | sentence_1                                                                                        | label                                                          |
  |:--------|:------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------|:---------------------------------------------------------------|
  | type    | string                                                                                          | string                                                                                            | float                                                          |
  | details | <ul><li>min: 10 characters</li><li>mean: 72.24 characters</li><li>max: 392 characters</li></ul> | <ul><li>min: 19 characters</li><li>mean: 281.85 characters</li><li>max: 2799 characters</li></ul> | <ul><li>min: 0.0</li><li>mean: 0.51</li><li>max: 1.0</li></ul> |
* Samples:
  | sentence_0                                                                           | sentence_1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | label            |
  |:-------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------|
  | <code>Làm thế nào để biết rằng tai nghe Bluetooth tôi mua là hàng chính hãng?</code> | <code>Có một số cách để biết rằng tai nghe Bluetooth bạn mua là hàng chính hãng:<br><br>- **Kiểm tra bao bì**: Bao bì của tai nghe chính hãng thường được thiết kế cẩn thận và có đầy đủ thông tin về sản phẩm. Hãy kiểm tra xem bao bì có bị hư hỏng hoặc có dấu hiệu tái sử dụng không.<br>- **Kiểm tra sản phẩm**: Khi mở hộp tai nghe, hãy kiểm tra xem sản phẩm có bị trầy xước hoặc hư hỏng không. Bạn cũng nên kiểm tra xem các phụ kiện đi kèm có đầy đủ không.<br>- **Kiểm tra số sê-ri**: Mỗi sản phẩm chính hãng đều có một số sê-ri duy nhất. Bạn có thể kiểm tra số sê-ri này trên trang web của nhà sản xuất để xác nhận tính hợp lệ của sản phẩm.<br>- **Mua từ nhà bán lẻ uy tín**: Hãy mua tai nghe Bluetooth từ các nhà bán lẻ uy tín để đảm bảo rằng bạn mua được hàng chính hãng.</code> | <code>1.0</code> |
  | <code>Làm thế nào để tránh sử dụng dầu ăn bị oxy hóa?</code>                         | <code>Để tránh sử dụng dầu ăn bị oxy hóa, bạn nên chọn dầu ăn có nguồn gốc rõ ràng, không mua dầu ăn đã để quá lâu. Không nên chiên rán thực phẩm ở nhiệt độ quá cao, nên sử dụng dầu ăn một lần và không nên tái sử dụng nhiều lần.</code>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | <code>1.0</code> |
  | <code>sao mình không đăng nhập được ạ.</code>                                        | <code>Cám ơn bạn đã nhắn tin cho DooPage, chúng tôi sẽ sớm phản hồi lại tin nhắn của bạn. Nếu bạn có thắc mắc gì chỉ cần bấm nút "Gặp quản trị viên".</code>                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | <code>1.0</code> |
* Loss: [<code>BinaryCrossEntropyLoss</code>](https://sbert.net/docs/package_reference/cross_encoder/losses.html#binarycrossentropyloss) with these parameters:
  ```json
  {
      "activation_fn": "torch.nn.modules.linear.Identity",
      "pos_weight": null
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `eval_strategy`: steps
- `per_device_train_batch_size`: 16
- `per_device_eval_batch_size`: 16
- `num_train_epochs`: 5

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `do_predict`: False
- `eval_strategy`: steps
- `prediction_loss_only`: True
- `per_device_train_batch_size`: 16
- `per_device_eval_batch_size`: 16
- `gradient_accumulation_steps`: 1
- `eval_accumulation_steps`: None
- `torch_empty_cache_steps`: None
- `learning_rate`: 5e-05
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `max_grad_norm`: 1
- `num_train_epochs`: 5
- `max_steps`: -1
- `lr_scheduler_type`: linear
- `lr_scheduler_kwargs`: None
- `warmup_ratio`: None
- `warmup_steps`: 0
- `log_level`: passive
- `log_level_replica`: warning
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `enable_jit_checkpoint`: False
- `save_on_each_node`: False
- `save_only_model`: False
- `restore_callback_states_from_checkpoint`: False
- `use_cpu`: False
- `seed`: 42
- `data_seed`: None
- `bf16`: False
- `fp16`: False
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `local_rank`: -1
- `ddp_backend`: None
- `debug`: []
- `dataloader_drop_last`: False
- `dataloader_num_workers`: 0
- `dataloader_prefetch_factor`: None
- `disable_tqdm`: False
- `remove_unused_columns`: True
- `label_names`: None
- `load_best_model_at_end`: False
- `ignore_data_skip`: False
- `fsdp`: []
- `fsdp_config`: {'min_num_params': 0, 'xla': False, 'xla_fsdp_v2': False, 'xla_fsdp_grad_ckpt': False}
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `parallelism_config`: None
- `deepspeed`: None
- `label_smoothing_factor`: 0.0
- `optim`: adamw_torch_fused
- `optim_args`: None
- `group_by_length`: False
- `length_column_name`: length
- `project`: huggingface
- `trackio_space_id`: trackio
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `dataloader_pin_memory`: True
- `dataloader_persistent_workers`: False
- `skip_memory_metrics`: True
- `push_to_hub`: False
- `resume_from_checkpoint`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_private_repo`: None
- `hub_always_push`: False
- `hub_revision`: None
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `include_for_metrics`: []
- `eval_do_concat_batches`: True
- `auto_find_batch_size`: False
- `full_determinism`: False
- `ddp_timeout`: 1800
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `include_num_input_tokens_seen`: no
- `neftune_noise_alpha`: None
- `optim_target_modules`: None
- `batch_eval_metrics`: False
- `eval_on_start`: False
- `use_liger_kernel`: False
- `liger_kernel_config`: None
- `eval_use_gather_object`: False
- `average_tokens_across_devices`: True
- `use_cache`: False
- `prompts`: None
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: proportional
- `router_mapping`: {}
- `learning_rate_mapping`: {}

</details>

### Training Logs
| Epoch  | Step | Training Loss | reranker_eval_average_precision |
|:------:|:----:|:-------------:|:-------------------------------:|
| 0.3367 | 200  | -             | 0.8361                          |
| 0.6734 | 400  | -             | 0.8701                          |
| 0.8418 | 500  | 0.6277        | -                               |
| 1.0    | 594  | -             | 0.8797                          |
| 1.0101 | 600  | -             | 0.8730                          |
| 1.3468 | 800  | -             | 0.8809                          |
| 1.6835 | 1000 | 0.3880        | 0.8963                          |
| 2.0    | 1188 | -             | 0.9014                          |
| 2.0202 | 1200 | -             | 0.8987                          |
| 2.3569 | 1400 | -             | 0.9011                          |
| 2.5253 | 1500 | 0.3248        | -                               |
| 2.6936 | 1600 | -             | 0.9009                          |
| 3.0    | 1782 | -             | 0.8981                          |
| 3.0303 | 1800 | -             | 0.9036                          |
| 3.3670 | 2000 | 0.2715        | 0.9026                          |
| 3.7037 | 2200 | -             | 0.9072                          |


### Framework Versions
- Python: 3.12.13
- Sentence Transformers: 5.3.0
- Transformers: 5.0.0
- PyTorch: 2.10.0+cu128
- Accelerate: 1.13.0
- Datasets: 4.0.0
- Tokenizers: 0.22.2

## Citation

### BibTeX

#### Sentence Transformers
```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084",
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->