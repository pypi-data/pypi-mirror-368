"""
Perplexity utilities for MALLET output.

This module provides helpers to compute perplexity from MALLET's
reported LL/token values in training logs.

Usage examples:

    from little_mallet_wrapper.perplexity_utils import (
        compute_perplexity_from_ll_per_token,
        get_training_perplexity_from_log,
    )

    # Convert a known LL/token value to perplexity
    ppl = compute_perplexity_from_ll_per_token(-7.86552)

    # Parse a MALLET training log and compute perplexity from the last LL/token
    ppl_from_log = get_training_perplexity_from_log("/path/to/train.log")
"""

import re
import numpy as np


def compute_perplexity_from_ll_per_token(ll_per_token: float) -> float:
    """
    Convert MALLET's LL/token (mean log-likelihood per token) into perplexity.

    Perplexity is defined as exp(-LL/token) when LL/token is the natural-log
    average per-token log-likelihood.

    Parameters
    ----------
    ll_per_token : float
        The LL/token value reported by MALLET, e.g., -7.86552.

    Returns
    -------
    float
        Perplexity corresponding to the provided LL/token value.
    """
    return float(np.exp(-float(ll_per_token)))


def get_training_perplexity_from_log(log_path: str) -> float:
    """
    Parse a MALLET training log and return the perplexity based on the last
    reported "LL/token: <value>" line.

    This function scans the file for occurrences of the pattern
    "LL/token: <number>" and uses the final value, assuming the log corresponds
    to a single training run where later iterations reflect more converged values.

    Parameters
    ----------
    log_path : str
        Path to a text file containing MALLET's stdout/stderr from train-topics.
        For example, redirect when training:  ... train-topics ... > train.log 2>&1

    Returns
    -------
    float
        The perplexity computed as exp(-LL/token) using the last observed LL/token.

    Raises
    ------
    ValueError
        If no LL/token line can be found in the provided log file.
    """
    pattern = re.compile(r"LL/token:\s*(-?\d+(?:\.\d+)?)")
    last_ll = None
    with open(log_path, "r") as f:
        for line in f:
            m = pattern.search(line)
            if m:
                try:
                    last_ll = float(m.group(1))
                except ValueError:
                    # Skip unparsable values
                    continue
    if last_ll is None:
        raise ValueError(f"No 'LL/token' line found in log file: {log_path}")
    return compute_perplexity_from_ll_per_token(last_ll)

