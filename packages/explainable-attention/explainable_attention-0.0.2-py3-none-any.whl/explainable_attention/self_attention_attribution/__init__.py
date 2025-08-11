import torch
import torch.nn as nn
from tqdm import tqdm

from .layers import AttentionAttributionTransformerEncoderLayer, AttentionAttributionPatchedLayer

def compute(
    transformer_layers,
    objective,
    batch,
    integration_steps: int = 20,
    show_progress: bool = True
):
    # Ensure the layers have been patched
    patch(transformer_layers)

    # Reset all attention head masks to 1.0
    one = torch.tensor(1.0)

    with torch.no_grad():
        for layer in transformer_layers:
            layer.attention_head_mask.requires_grad_(False)
            layer.attention_head_mask.set_(one.to(layer.attention_head_mask.device))

    # forward pass with no masking
    # k = 1.0
    loss = objective(batch)
    attention_weights = [layer.attention_weights for layer in transformer_layers]
    attribution_results = [g.detach() for g in torch.autograd.grad(loss, attention_weights, retain_graph=False, create_graph=False)]

    for layer, A, attribution in zip(tqdm(transformer_layers, disable=(not show_progress)), attention_weights, attribution_results):
        for k in torch.linspace(0.0, 1.0, integration_steps)[:-1]:
            layer.attention_head_mask.set_(k.to(layer.attention_head_mask.device))
            attribution += torch.autograd.grad(objective(batch), layer.attention_weights, retain_graph=False, create_graph=False)[0].detach()
        with torch.no_grad():
            attribution[:] = A * attribution / integration_steps
            layer.attention_head_mask.set_(one.to(layer.attention_head_mask.device))

    with torch.no_grad():
        return torch.stack(attribution_results).transpose(0, 1)

# Patching -----------------------------------------------------------------------------------------

_patching_map = {}

def patch(encoder_layers):
    for i in range(len(encoder_layers)):
        layer = encoder_layers[i]
        if isinstance(layer, AttentionAttributionPatchedLayer):
            # No need to patch
            continue
        if layer.__class__ not in _patching_map:
            raise Exception("Unable to patch layer:", layer)
        encoder_layers[i] = _patching_map[layer.__class__](layer)
    return encoder_layers


def unpatch(encoder_layers):
    for i in range(len(encoder_layers)):
        layer = encoder_layers[i]
        if not isinstance(layer, AttentionAttributionPatchedLayer):
            # No need to unpatch
            continue
        encoder_layers[i] = layer.unpatch()
    return encoder_layers


def register_patch(layer_class, patch_class):
    _patching_map[layer_class] = patch_class


register_patch(nn.TransformerEncoderLayer, AttentionAttributionTransformerEncoderLayer)
try:
    from transformers.models.vit.modeling_vit import ViTLayer
    register_patch(ViTLayer, AttentionAttributionTransformerEncoderLayer)
except ImportError:
    pass
