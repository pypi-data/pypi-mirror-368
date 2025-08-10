"""
Text evaluation metrics for comparing reference and generated text.
Provides exact match, ROUGE-L, Levenshtein distance, and fractional exact match metrics.
"""
import numpy as np
from typing import Optional, Tuple, List, Union
from rouge_score import rouge_scorer
from Levenshtein import distance

def exact_match(reference: str, generated: str, tokenizer=None) -> Tuple[float, int]:
    """Calculate exact match score and matching prefix length.
    
    Args:
        reference: Ground truth text
        generated: Generated text to evaluate
        tokenizer: Optional tokenizer for token-level comparison
        
    Returns:
        Tuple of (exact_match_score, matching_prefix_length)
        
    Example:
        >>> exact_match("hello world", "hello world")
        (1.0, 11)
    """
    if tokenizer:
        ref_tokens = tokenizer(reference, add_special_tokens=False).input_ids
        gen_tokens = tokenizer(generated, add_special_tokens=False).input_ids
        
        match_length = 0
        for t1, t2 in zip(ref_tokens, gen_tokens):
            if t1 == t2:
                match_length += 1
            else:
                break
                
        return float(ref_tokens == gen_tokens), match_length
    
    ref_str = reference.strip()
    gen_str = generated.strip()
    match_length = 0
    for c1, c2 in zip(ref_str, gen_str):
        if c1 == c2:
            match_length += 1
        else:
            break
    
    return float(ref_str == gen_str), match_length

def rouge_l(reference: str, generated: str, tokenizer=None) -> float:
    """Calculate ROUGE-L F1 score between reference and generated text.
    
    Args:
        reference: Ground truth text
        generated: Generated text to evaluate
        tokenizer: Optional tokenizer for token-level comparison
        
    Returns:
        ROUGE-L F1 score (0.0 to 1.0)
        
    Example:
        >>> rouge_l("the cat sat on the mat", "cat sat on mat")
        0.8571428571428571
    """
    if tokenizer:
        reference = " ".join([str(x) for x in tokenizer(reference, add_special_tokens=False).input_ids])
        generated = " ".join([str(x) for x in tokenizer(generated, add_special_tokens=False).input_ids])
    
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    scores = scorer.score(reference, generated)
    return scores['rougeL'].fmeasure

def levenshtein(reference: str, generated: str) -> float:
    """Calculate normalized Levenshtein distance between reference and generated text.
    
    Args:
        reference: Ground truth text
        generated: Generated text to evaluate
        
    Returns:
        Normalized edit distance (0.0 = identical, 1.0 = completely different)
        
    Example:
        >>> levenshtein("hello", "hallo")
        0.2
    """
    ref_str = reference.strip()
    gen_str = generated.strip()
    dist = distance(ref_str, gen_str)
    max_len = max(len(ref_str), len(gen_str))
    return dist / max_len if max_len > 0 else 0.0

def fractional_exact_match(reference: str, generated: str, tokenizer=None) -> float:
    """Calculate fractional exact match rate - fraction of generated tokens that are correct and in right position.
    
    Args:
        reference: Ground truth text
        generated: Generated text to evaluate
        tokenizer: Optional tokenizer for token-level comparison
        
    Returns:
        Fraction of correct tokens in correct positions (0.0 to 1.0)
        
    Example:
        >>> fractional_exact_match("hello world", "hello earth")
        0.5
    """
    if tokenizer:
        ref_tokens = tokenizer(reference, add_special_tokens=False).input_ids
        gen_tokens = tokenizer(generated, add_special_tokens=False).input_ids
    else:
        ref_tokens = list(reference.strip())
        gen_tokens = list(generated.strip())
    
    if len(gen_tokens) == 0:
        return 0.0
    
    correct_positions = sum(1 for i, token in enumerate(gen_tokens) 
                           if i < len(ref_tokens) and token == ref_tokens[i])
    
    return correct_positions / len(gen_tokens)