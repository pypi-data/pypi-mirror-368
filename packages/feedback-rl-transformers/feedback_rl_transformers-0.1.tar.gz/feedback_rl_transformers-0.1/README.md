
# QA Trainer 📚🤖

**QA Trainer** is a Python package for fine-tuning Question Answering models using feedback data.  
It uses [SimpleTransformers](https://simpletransformers.ai/) for model training and [Optuna](https://optuna.org/) for hyperparameter tuning.

---



---

## 📂 Example Dataset Format

The dataset must be a **JSON array** of feedback entries.
Each entry should have:

* `"question"` → The question text
* `"answer"` → The answer text (used as both context and answer in training)
* `"feedback"` → A positive number to include it in training, negative/zero to exclude

**Example `feedback_data.json for question answer model but format will remain same for other model also you can take help of simple transformers python libary`**

```json
[
    {
        "question": "What is AI?",
        "answer": "AI stands for Artificial Intelligence.",
        "feedback": 1
    },
    {
        "question": "Who is the president of Mars?",
        "answer": "Elon Musk.",
        "feedback": -1
    },
    {
        "question": "What is Python?",
        "answer": "Python is a programming language.",
        "feedback": 1
    }
]
```

---

## 🚀 Quick Start

```python
from feedback_rl_transformers import train_with_feedback

train_with_feedback(
    feedback_data_path="feedback_data.json",  # Path to your feedback dataset
    model_type="bert",                        # Model type (see table below)
    model_path="bert-base-uncased",           # Pretrained model name or path
    output_dir="fine_tuned_model",            # Where to save the final model
    n_trials=5,                               # Optuna hyperparameter tuning trials
    use_cuda=False                            # Set True to use GPU if available
)
```

---

## 🧠 Supported Models

| Model Name    | Code          |
| ------------- | ------------- |
| ALBERT        | `albert`      |
| BERT          | `bert`        |
| BERTweet      | `bertweet`    |
| BigBird\*     | `bigbird`     |
| CamemBERT     | `camembert`   |
| DeBERTa\*     | `deberta`     |
| DistilBERT    | `distilbert`  |
| ELECTRA       | `electra`     |
| FlauBERT      | `flaubert`    |
| HerBERT       | `herbert`     |
| LayoutLM      | `layoutlm`    |
| LayoutLMv2    | `layoutlmv2`  |
| Longformer\*  | `longformer`  |
| MPNet\*       | `mpnet`       |
| MobileBERT    | `mobilebert`  |
| RemBERT       | `rembert`     |
| RoBERTa       | `roberta`     |
| SqueezeBert\* | `squeezebert` |
| XLM           | `xlm`         |
| XLM-RoBERTa   | `xlmroberta`  |
| XLNet         | `xlnet`       |

\*Some large models may require more memory or a GPU.

---

## ⚙️ Parameters

| Parameter            | Type | Description                                       |
| -------------------- | ---- | ------------------------------------------------- |
| `feedback_data_path` | str  | Path to feedback JSON dataset                     |
| `model_type`         | str  | Model type code (see table)                       |
| `model_path`         | str  | Pretrained model name or path                     |
| `output_dir`         | str  | Directory where fine-tuned model will be saved    |
| `n_trials`           | int  | Number of Optuna trials for hyperparameter tuning |
| `use_cuda`           | bool | Use GPU if available                              |

---

## 📤 Output

After training:

* The fine-tuned model will be saved in `output_dir`
* Best hyperparameters from Optuna will be printed

---

