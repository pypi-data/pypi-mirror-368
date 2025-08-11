# explainable-attention

Implementation of various tools for multi-head attention explainability from transformers.

## Self-Attention Attribution

[Hao, Yaru, et al. "Self-attention attribution: Interpreting information interactions inside transformer." Proceedings of the AAAI Conference on Artificial Intelligence. Vol. 35. No. 14. 2021.](https://arxiv.org/abs/2004.11207)

```py
from explainable_attention.self_attention_attribution import compute

...

def objective(batch):
    x, y = batch
    y = model(x)
    loss = loss_fn(x, y)
    return loss

attribution = saa.compute(
    model.transformer_encoder.layers,
    objective,
    batch,
    integration_steps=20)
```
