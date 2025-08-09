# ABOUTME: Model utilities - token counting and context window management
"""Model utilities for token counting and context window management."""


class SimpleModel:
    """Simple model for token counting estimation."""
    
    def token_count(self, text: str) -> int:
        """
        Estimate token count for text.
        Uses rough approximation: 1 token ≈ 4 characters
        """
        return len(text) // 4


def estimate_token_count(text: str, model: SimpleModel) -> float:
    """
    Estimate token count with sampling for large texts.
    
    For small texts, uses the model directly.
    For large texts, samples every 100th line to speed up estimation.
    """
    len_text = len(text)
    if len_text < 200:
        return model.token_count(text)
    
    lines = text.splitlines(keepends=True)
    num_lines = len(lines)
    step = num_lines // 100 or 1
    lines = lines[::step]
    sample_text = "".join(lines)
    sample_tokens = model.token_count(sample_text)
    est_tokens = sample_tokens / len(sample_text) * len_text
    return est_tokens