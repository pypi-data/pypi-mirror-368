"""
metrics.py - Standalone metrics helpers for Gensim and MALLET.

Provides:
- Gensim:
  - compute_gensim_perplexity(lda_model, corpus)
  - compute_gensim_coherence(lda_model, texts=None, corpus=None, dictionary=None, coherence='c_v', topn=20)
  - compute_gensim_coherence_per_topic(lda_model, texts=None, corpus=None, dictionary=None, coherence='c_v', topn=20)

- MALLET:
  - mallet_perplexity_from_log(log_path)
  - parse_mallet_diagnostics_coherence(diagnostics_xml_path)

Notes:
- Gensim perplexity: gensim's LdaModel.log_perplexity returns the average per-word log-likelihood bound (natural log).
  Perplexity is computed as exp(-bound).
- MALLET perplexity: use LL/token reported in training logs and compute exp(-LL/token).
- MALLET coherence: parsed from the diagnostics XML (per-topic coherence); we also return the mean across topics.
"""

from __future__ import annotations

import math
import re
from typing import List, Optional, Tuple

# Optional imports: delay errors to call time to keep this module importable without gensim
try:
    from gensim.models.ldamodel import LdaModel  # type: ignore
    from gensim.models.coherencemodel import CoherenceModel  # type: ignore
except Exception:  # pragma: no cover
    LdaModel = None  # type: ignore
    CoherenceModel = None  # type: ignore

# XML parsing for MALLET diagnostics
import xml.etree.ElementTree as ET


def compute_gensim_perplexity(lda_model, corpus) -> float:
    """
    Compute perplexity for a Gensim LdaModel using its log_perplexity on the given corpus.

    Parameters
    ----------
    lda_model : gensim.models.LdaModel
        A trained Gensim LDA model.
    corpus : iterable
        The corpus (bag-of-words) used to evaluate perplexity.

    Returns
    -------
    float
        Perplexity = exp(-log_per_word_bound).
    """
    if LdaModel is None:
        raise ImportError("gensim is required for compute_gensim_perplexity but is not installed.")
    bound = lda_model.log_perplexity(corpus)
    return float(math.exp(-bound))


def compute_gensim_coherence(
    lda_model,
    texts: Optional[List[List[str]]] = None,
    corpus=None,
    dictionary=None,
    coherence: str = "c_v",
    topn: int = 20,
) -> float:
    """
    Compute overall coherence for a Gensim LdaModel using gensim.models.CoherenceModel.

    For 'c_v' and 'c_uci'/'c_npmi', supply tokenized texts. For 'u_mass', supply corpus+dictionary.

    Parameters
    ----------
    lda_model : gensim.models.LdaModel
    texts : list of list of str, optional
        Tokenized texts (required for 'c_v', 'c_uci', 'c_npmi').
    corpus : iterable, optional
        BoW corpus (used for 'u_mass').
    dictionary : gensim.corpora.Dictionary, optional
        Dictionary aligning ids to tokens (used for 'u_mass').
    coherence : str
        One of {'c_v','u_mass','c_uci','c_npmi'}.
    topn : int
        Number of top words per topic to use.

    Returns
    -------
    float
        Overall coherence.
    """
    if CoherenceModel is None:
        raise ImportError("gensim is required for compute_gensim_coherence but is not installed.")

    cm = CoherenceModel(
        model=lda_model,
        texts=texts,
        corpus=corpus,
        dictionary=dictionary,
        coherence=coherence,
        topn=topn,
    )
    return float(cm.get_coherence())


def compute_gensim_coherence_per_topic(
    lda_model,
    texts: Optional[List[List[str]]] = None,
    corpus=None,
    dictionary=None,
    coherence: str = "c_v",
    topn: int = 20,
) -> List[float]:
    """
    Compute per-topic coherence scores using gensim.models.CoherenceModel.

    Returns a list of coherence scores aligned with topic ids.
    """
    if CoherenceModel is None:
        raise ImportError("gensim is required for compute_gensim_coherence_per_topic but is not installed.")

    cm = CoherenceModel(
        model=lda_model,
        texts=texts,
        corpus=corpus,
        dictionary=dictionary,
        coherence=coherence,
        topn=topn,
    )
    per_topic = cm.get_coherence_per_topic()
    return [float(x) for x in per_topic]


# === MALLET metrics ===

def mallet_perplexity_from_log(log_path: str) -> float:
    """
    Compute MALLET perplexity by parsing LL/token from a training log.

    Attempts to use little_mallet_wrapper.perplexity_utils if available; otherwise,
    falls back to an internal implementation.
    """
    try:
        # Prefer the shared implementation if installed
        from little_mallet_wrapper.perplexity_utils import get_training_perplexity_from_log  # type: ignore

        return float(get_training_perplexity_from_log(log_path))
    except Exception:
        # Fallback: parse directly
        pattern = re.compile(r"LL/token:\s*(-?\d+(?:\.\d+)?)")
        last_ll = None
        with open(log_path, "r") as f:
            for line in f:
                m = pattern.search(line)
                if m:
                    try:
                        last_ll = float(m.group(1))
                    except ValueError:
                        continue
        if last_ll is None:
            raise ValueError(f"No 'LL/token' line found in log file: {log_path}")
        return float(math.exp(-last_ll))


def parse_mallet_diagnostics_coherence(diagnostics_xml_path: str) -> Tuple[float, List[float]]:
    """
    Parse MALLET diagnostics XML to extract per-topic coherence and their mean.

    Parameters
    ----------
    diagnostics_xml_path : str
        Path to MALLET diagnostics XML produced via --diagnostics-file.

    Returns
    -------
    (mean_coherence, per_topic_coherence)
        mean_coherence : float - arithmetic mean of per-topic coherence values
        per_topic_coherence : list[float] - coherence per topic (ordered by topic id if present)
    """
    tree = ET.parse(diagnostics_xml_path)
    root = tree.getroot()

    # MALLET diagnostics structure typically has <topic ... coherence="..." .../>
    topic_elements = root.findall('.//topic')
    coherences = []
    # Collect pairs of (topic_id, coherence) if id exists, else None
    temp: List[Tuple[Optional[int], float]] = []
    for t in topic_elements:
        coh_val = None
        # Try attribute first
        if 'coherence' in t.attrib:
            try:
                coh_val = float(t.attrib['coherence'])
            except Exception:
                coh_val = None
        # If not an attribute, try child element named 'coherence'
        if coh_val is None:
            child = t.find('coherence')
            if child is not None and child.text:
                try:
                    coh_val = float(child.text)
                except Exception:
                    coh_val = None
        if coh_val is None:
            continue
        # Topic id if present
        topic_id = None
        if 'id' in t.attrib:
            try:
                topic_id = int(t.attrib['id'])
            except Exception:
                topic_id = None
        temp.append((topic_id, coh_val))

    if not temp:
        raise ValueError("No topic coherence values found in MALLET diagnostics XML.")

    # Order by topic id if available
    if any(tid is not None for tid, _ in temp):
        temp.sort(key=lambda x: (1 if x[0] is None else 0, -1 if x[0] is None else x[0]))
    coherences = [c for _, c in temp]

    mean_coh = float(sum(coherences) / len(coherences))
    return mean_coh, coherences

