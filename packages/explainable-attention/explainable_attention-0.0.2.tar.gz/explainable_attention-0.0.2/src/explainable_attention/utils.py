import math
import torch
from torch.nn.attention.flex_attention import flex_attention, _vmap_for_bhqkv
from typing import Callable

try:
    from torch._dynamo._trace_wrapped_higher_order_op import TransformGetItemToIndex
except ImportError:
    from torch._higher_order_ops.flex_attention import TransformGetItemToIndex

@torch.compiler.disable
def naive_flex_attention_with_scores(
	query: torch.Tensor,
	key: torch.Tensor,
	value: torch.Tensor,
	return_attention_scores: bool = False,
	return_lse: bool = False,
	**kwargs
):
	"""
	A manual and simple implementation of the attention based on Flex Attention
	that also returns the full attention score matrix.
	"""
	assert not return_lse, "return_lse is not supported for naive implementation"
	# Compute attention scores
	scores = query @ key.transpose(-2, -1)
	scores *= kwargs.get("scale_factor", 1/math.sqrt(query.shape[-1]))
	# Compute indices
	b = torch.arange(0, query.shape[0], device=query.device)
	h = torch.arange(0, query.shape[1], device=query.device)
	m = torch.arange(0, query.shape[2], device=query.device)
	n = torch.arange(0, key.shape[2], device=query.device)
	# Apply score mod if available
	with TransformGetItemToIndex():
		if kwargs.get("score_mod", None) is not None:
			# Apply score mod
			mod = _vmap_for_bhqkv(kwargs["score_mod"], prefix=(0,))
			scores = mod(scores, b, h, m, n)
		if kwargs.get("block_mask", None) is not None:
			mod = _vmap_for_bhqkv(kwargs["block_mask"].mask_mod, prefix=())
			mask = mod(b, h, m, n)
			scores = torch.where(mask == 0, float("-inf"), scores)
	scores = torch.softmax(scores, -1)
	attention = torch.matmul(scores, value)
	if return_attention_scores:
		return attention, scores
	return attention

def flex_attention_with_scores(
	query: torch.Tensor,
	key: torch.Tensor,
	value: torch.Tensor,
	*args,
	return_attention_scores: bool = False,
	**kwargs
):
	"""
	A wrapper around Flex Attention that also returns the full attention score matrix.
	"""
	if return_attention_scores and not kwargs.get("return_lse", False):
		return naive_flex_attention_with_scores(query, key, value, return_attention_scores=True, **kwargs)
	return flex_attention(query, key, value, *args, **kwargs)
