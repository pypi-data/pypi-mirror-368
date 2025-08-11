import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional

from ..layers import PatchedLayer


class AttentionAttributionPatchedLayer(PatchedLayer):
    ...


class AttentionAttributionTransformerEncoderLayer(AttentionAttributionPatchedLayer, nn.Module):
    class WeightLogger:
        """
        Used to prevent unnecessary updates in Pytorch's module
        """
        def __init__(self):
            self.data: Optional[torch.Tensor] = None

    def __init__(self, layer):
        super().__init__(layer)
        self.attention_head_mask = nn.Parameter(torch.tensor(1.0), requires_grad=False)
        self._attention_weight_log = self.WeightLogger()

    def forward(self, *args, **kwargs):
        temp = F.scaled_dot_product_attention
        F.scaled_dot_product_attention = self._scaled_dot_product_attention_with_head_mask
        try:
            result = self.patched_layer(*args, **kwargs)
        finally:
            F.scaled_dot_product_attention = temp
        return result

    @property
    def self_attn(self):
        return self.patched_layer.self_attn

    @property
    def attention_weights(self):
        """
        Get the attention weights from the previous forward pass
        """
        return self._attention_weight_log.data

    def _scaled_dot_product_attention_with_head_mask(
        self,
        query,
        key,
        value,
        attn_mask=None,
        dropout_p=0.0,
        is_causal=False,
        scale=None,
        enable_gqa=False
    ) -> torch.Tensor:
        attn_head_mask = self.attention_head_mask
        L, S = query.size(-2), key.size(-2)
        scale_factor = 1 / math.sqrt(query.size(-1)) if scale is None else scale
        attn_bias = torch.zeros(L, S, dtype=query.dtype, device=query.device)
        if is_causal:
            assert attn_mask is None
            temp_mask = torch.ones(L, S, dtype=torch.bool).tril(diagonal=0)
            attn_bias.masked_fill_(temp_mask.logical_not(), float("-inf"))
            attn_bias.to(query.dtype)

        if attn_mask is not None:
            if attn_mask.dtype == torch.bool:
                attn_bias.masked_fill_(attn_mask.logical_not(), float("-inf"))
            else:
                attn_bias = attn_mask + attn_bias

        if enable_gqa:
            key = key.repeat_interleave(query.size(-3)//key.size(-3), -3)
            value = value.repeat_interleave(query.size(-3)//value.size(-3), -3)

        attn_weight = query @ key.transpose(-2, -1) * scale_factor
        attn_weight += attn_bias
        attn_weight = torch.softmax(attn_weight, dim=-1)
        # Attention head masking for attribution
        attn_weight = attn_weight * attn_head_mask.to(attn_weight.device)
        #
        attn_weight = torch.dropout(attn_weight, dropout_p, train=True)
        self._attention_weight_log.data = attn_weight
        return attn_weight @ value
