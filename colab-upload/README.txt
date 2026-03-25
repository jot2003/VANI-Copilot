VANI Copilot - Colab Upload Files
=================================

Upload TOÀN BỘ thư mục này lên Google Drive tại:
  MyDrive/vani-copilot/

Sau đó mở notebooks trên Colab theo thứ tự:

1. notebooks/03_finetune_embedding.ipynb  (T4 GPU, ~30 phút)
2. notebooks/02_finetune_llm_qlora.ipynb  (A100 GPU, ~2-3 giờ)  
3. notebooks/04_finetune_reranker.ipynb   (T4 GPU, ~20 phút)
4. notebooks/05_evaluation.ipynb          (T4 GPU, ~15 phút)

Files:
- train.jsonl    : 9,014 samples (training data)
- val.jsonl      : 1,127 samples (validation data)  
- test.jsonl     : 1,127 samples (test data)
- policies.txt   : VANI Store policies (knowledge base)
- faq.txt        : FAQ (knowledge base)
- products.txt   : Product catalog (knowledge base)
