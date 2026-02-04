---
tags:
- setfit
- sentence-transformers
- text-classification
- generated_from_setfit_trainer
widget:
- text: Hello there
- text: Alright
- text: Do you stock Arduino?
- text: Rules for taking equipment home
- text: Tell me about the camera
metrics:
- accuracy
pipeline_tag: text-classification
library_name: setfit
inference: true
base_model: sentence-transformers/all-MiniLM-L6-v2
model-index:
- name: SetFit with sentence-transformers/all-MiniLM-L6-v2
  results:
  - task:
      type: text-classification
      name: Text Classification
    dataset:
      name: Unknown
      type: unknown
      split: test
    metrics:
    - type: accuracy
      value: 0.9375
      name: Accuracy
---

# SetFit with sentence-transformers/all-MiniLM-L6-v2

This is a [SetFit](https://github.com/huggingface/setfit) model that can be used for Text Classification. This SetFit model uses [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) as the Sentence Transformer embedding model. A [LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html) instance is used for classification.

The model has been trained using an efficient few-shot learning technique that involves:

1. Fine-tuning a [Sentence Transformer](https://www.sbert.net) with contrastive learning.
2. Training a classification head with features from the fine-tuned Sentence Transformer.

## Model Details

### Model Description
- **Model Type:** SetFit
- **Sentence Transformer body:** [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- **Classification head:** a [LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html) instance
- **Maximum Sequence Length:** 256 tokens
- **Number of Classes:** 9 classes
<!-- - **Training Dataset:** [Unknown](https://huggingface.co/datasets/unknown) -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Repository:** [SetFit on GitHub](https://github.com/huggingface/setfit)
- **Paper:** [Efficient Few-Shot Learning Without Prompts](https://arxiv.org/abs/2209.11055)
- **Blogpost:** [SetFit: Efficient Few-Shot Learning Without Prompts](https://huggingface.co/blog/setfit)

### Model Labels
| Label               | Examples                                                                                                               |
|:--------------------|:-----------------------------------------------------------------------------------------------------------------------|
| greeting            | <ul><li>'Greetings'</li><li>'Good morning'</li><li>'Hey'</li></ul>                                                     |
| troubleshooting     | <ul><li>'Error message'</li><li>'ROS2 installation error'</li><li>'Arduino upload failed'</li></ul>                    |
| project_idea        | <ul><li>'Show me project ideas'</li><li>'What projects use RealSense?'</li><li>'What can I build?'</li></ul>           |
| acknowledgment      | <ul><li>'Okay, got it'</li><li>'Thanks'</li><li>'Sure'</li></ul>                                                       |
| equipment_query     | <ul><li>'Tell me about RealSense camera'</li><li>'Specs for Raspberry Pi'</li><li>'What is Intel RealSense?'</li></ul> |
| compatibility_check | <ul><li>'Will X interface with Y?'</li><li>'Does ROS2 work with Raspberry Pi?'</li><li>'Does X work with Y?'</li></ul> |
| guidance            | <ul><li>'Steps to borrow a robot'</li><li>'How to reserve equipment'</li><li>'Setup instructions'</li></ul>            |
| lab_info            | <ul><li>'Who can I contact?'</li><li>'Where is the lab located?'</li><li>'Lab rules and regulations'</li></ul>         |
| capability_check    | <ul><li>'Can you help with X?'</li></ul>                                                                               |

## Evaluation

### Metrics
| Label   | Accuracy |
|:--------|:---------|
| **all** | 0.9375   |

## Uses

### Direct Use for Inference

First install the SetFit library:

```bash
pip install setfit
```

Then you can load this model and run inference.

```python
from setfit import SetFitModel

# Download from the 🤗 Hub
model = SetFitModel.from_pretrained("setfit_model_id")
# Run inference
preds = model("Alright")
```

<!--
### Downstream Use

*List how someone could finetune this model on their own dataset.*
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Set Metrics
| Training set | Min | Median | Max |
|:-------------|:----|:-------|:----|
| Word count   | 1   | 3.7903 | 9   |

| Label               | Training Sample Count |
|:--------------------|:----------------------|
| acknowledgment      | 7                     |
| capability_check    | 1                     |
| compatibility_check | 8                     |
| equipment_query     | 13                    |
| greeting            | 6                     |
| guidance            | 6                     |
| lab_info            | 7                     |
| project_idea        | 8                     |
| troubleshooting     | 6                     |

### Training Hyperparameters
- batch_size: (16, 16)
- num_epochs: (3, 3)
- max_steps: -1
- sampling_strategy: oversampling
- body_learning_rate: (2e-05, 1e-05)
- head_learning_rate: 0.01
- loss: CosineSimilarityLoss
- distance_metric: cosine_distance
- margin: 0.25
- end_to_end: False
- use_amp: False
- warmup_proportion: 0.1
- l2_weight: 0.01
- seed: 42
- evaluation_strategy: epoch
- eval_max_steps: -1
- load_best_model_at_end: True

### Training Results
| Epoch  | Step | Training Loss | Validation Loss |
|:------:|:----:|:-------------:|:---------------:|
| 0.0048 | 1    | 0.1759        | -               |
| 0.2392 | 50   | 0.1783        | -               |
| 0.4785 | 100  | 0.0712        | -               |
| 0.7177 | 150  | 0.0239        | -               |
| 0.9569 | 200  | 0.0108        | -               |
| 1.0    | 209  | -             | 0.0381          |
| 1.1962 | 250  | 0.006         | -               |
| 1.4354 | 300  | 0.0039        | -               |
| 1.6746 | 350  | 0.0036        | -               |
| 1.9139 | 400  | 0.0032        | -               |
| 2.0    | 418  | -             | 0.0314          |
| 2.1531 | 450  | 0.0027        | -               |
| 2.3923 | 500  | 0.0026        | -               |
| 2.6316 | 550  | 0.0025        | -               |
| 2.8708 | 600  | 0.0023        | -               |
| 3.0    | 627  | -             | 0.0306          |

### Framework Versions
- Python: 3.12.3
- SetFit: 1.1.3
- Sentence Transformers: 5.2.0
- Transformers: 4.57.6
- PyTorch: 2.9.1+cu128
- Datasets: 4.5.0
- Tokenizers: 0.22.2

## Citation

### BibTeX
```bibtex
@article{https://doi.org/10.48550/arxiv.2209.11055,
    doi = {10.48550/ARXIV.2209.11055},
    url = {https://arxiv.org/abs/2209.11055},
    author = {Tunstall, Lewis and Reimers, Nils and Jo, Unso Eun Seo and Bates, Luke and Korat, Daniel and Wasserblat, Moshe and Pereg, Oren},
    keywords = {Computation and Language (cs.CL), FOS: Computer and information sciences, FOS: Computer and information sciences},
    title = {Efficient Few-Shot Learning Without Prompts},
    publisher = {arXiv},
    year = {2022},
    copyright = {Creative Commons Attribution 4.0 International}
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