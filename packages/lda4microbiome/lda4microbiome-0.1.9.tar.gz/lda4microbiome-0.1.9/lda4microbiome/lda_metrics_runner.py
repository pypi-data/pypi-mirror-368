"""
lda_metrics_runner.py - Independent integration to compute LDA metrics as you specified.

What this provides
- Trains models via your existing LDATrainer (no edits to training.py).
- Then computes metrics using:
  - Gensim implementation: perplexity via LdaModel.log_perplexity and coherence via gensim CoherenceModel.
  - MALLET implementation: coherence from MALLET diagnostics XML and perplexity from LL/token in MALLET logs.
- Aggregates results into a DataFrame and optionally writes a CSV.

How to use

    from lda4microbiome.lda_metrics_runner import LDAMetricsRunner

    runner = LDAMetricsRunner(base_directory=base_directory, path_to_mallet=path_to_mallet)

    # For MALLET
    mallet_results_df = runner.run(
        implementation='mallet',
        mc_range=range(5, 16),
        mallet_log_paths=None,   # or a dict {K: "/path/to/log_for_K.log"}
        save_csv=True
    )

    # For Gensim
    gensim_results_df = runner.run(
        implementation='gensim',
        mc_range=range(5, 16),
        save_csv=True
    )

Notes
- For MALLET perplexity, you need captured training logs that contain lines like:
    [beta: 0.04343] <1000> LL/token: -7.86552
  Provide these via mallet_log_paths={K: path_to_log} or place them in the loop directory following a pattern
  you pass in via mallet_log_pattern (e.g., "mallet_train_{K}.log"). If not found, perplexity is set to NaN.
"""

from __future__ import annotations

import os
import math
from typing import Dict, List, Optional, Union
import warnings
import pickle
import pandas as pd

# Local imports from your package
from .training import LDATrainer
from .metrics import (
    compute_gensim_perplexity,
    compute_gensim_coherence,
    # compute_gensim_coherence_per_topic,  # available if you need it
    mallet_perplexity_from_log,
    parse_mallet_diagnostics_coherence,
)


class LDAMetricsRunner:
    def __init__(
        self,
        base_directory: str,
        path_to_mallet: Optional[str] = None,
        gensim_params: Optional[Dict] = None,
    ) -> None:
        self.base_directory = base_directory
        self.path_to_mallet = path_to_mallet
        self.gensim_params = gensim_params or {}

    def run(
        self,
        implementation: str,
        mc_range: Union[List[int], range],
        save_csv: bool = True,
        csv_filename: Optional[str] = None,
        # MALLET-only options
        mallet_log_paths: Optional[Dict[int, str]] = None,
        mallet_log_pattern: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Train models via LDATrainer and compute metrics as specified.

        Parameters
        ----------
        implementation : "gensim" or "mallet"
        mc_range : list or range of topic counts
        save_csv : whether to write a CSV of metrics
        csv_filename : custom CSV filename (optional)
        mallet_log_paths : optional mapping {K: "/path/to/log_for_K.log"}
        mallet_log_pattern : optional filename pattern in loop dir, e.g., "mallet_train_{K}.log"
        """
        impl = implementation.lower()
        if impl not in {"gensim", "mallet"}:
            raise ValueError("implementation must be 'gensim' or 'mallet'")

        # Initialize trainer
        trainer = LDATrainer(
            base_directory=self.base_directory,
            path_to_mallet=self.path_to_mallet,
            implementation=impl,
            **self.gensim_params,
        )

        # Train models (writes outputs to disk)
        trainer.train_models(list(mc_range))

        # For gensim metrics we need texts + dictionary/corpus
        training_txt_path = trainer.paths["path_to_training_data"]
        texts = self._load_texts(training_txt_path)

        metrics_rows = []

        for K in list(mc_range):
            paths = trainer._generate_file_paths(K)
            if impl == "gensim":
                row = self._compute_gensim_metrics_for_K(K, paths, texts)
            else:
                row = self._compute_mallet_metrics_for_K(
                    K,
                    paths,
                    trainer.paths["loop_directory"],
                    mallet_log_paths=mallet_log_paths,
                    mallet_log_pattern=mallet_log_pattern,
                )
            metrics_rows.append(row)

        df = pd.DataFrame(metrics_rows).sort_values("K").reset_index(drop=True)

        if save_csv:
            lda_dir = trainer.paths["lda_directory"]
            if not csv_filename:
                mc_list = list(mc_range)
                csv_filename = f"metrics_{impl}_{min(mc_list)}-{max(mc_list)}.csv"
            out_path = os.path.join(lda_dir, csv_filename)
            df.to_csv(out_path, index=False)
            print(f"Saved metrics to {out_path}")

        return df

    # --- helpers ---

    def _load_texts(self, training_txt_path: str) -> List[List[str]]:
        texts: List[List[str]] = []
        with open(training_txt_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                # In your pipeline, training.txt stores the documents as whitespace-separated tokens per line
                tokens = [w for w in line.split() if w]
                texts.append(tokens)
        return texts

    def _compute_gensim_metrics_for_K(self, K: int, paths: Dict[str, str], texts: List[List[str]]):
        # Load model and dictionary
        with open(paths["model"], "rb") as f:
            lda_model = pickle.load(f)
        with open(paths["dictionary"], "rb") as f:
            dictionary = pickle.load(f)
        corpus = [dictionary.doc2bow(t) for t in texts]

        # Metrics
        perplexity = compute_gensim_perplexity(lda_model, corpus)
        coherence = compute_gensim_coherence(
            lda_model,
            texts=texts,
            dictionary=dictionary,
            coherence="c_v",
            topn=20,
        )

        return {
            "K": K,
            "Perplexity": float(perplexity),
            "Coherence": float(coherence),
            "Implementation": "gensim",
        }

    def _compute_mallet_metrics_for_K(
        self,
        K: int,
        paths: Dict[str, str],
        loop_dir: str,
        mallet_log_paths: Optional[Dict[int, str]] = None,
        mallet_log_pattern: Optional[str] = None,
    ):
        # Coherence from diagnostics XML
        mean_coh, _ = parse_mallet_diagnostics_coherence(paths["diagnostics"])

        # Perplexity from logs
        log_path = None
        if mallet_log_paths and K in mallet_log_paths:
            log_path = mallet_log_paths[K]
        elif mallet_log_pattern:
            candidate = os.path.join(loop_dir, mallet_log_pattern.format(K=K))
            if os.path.exists(candidate):
                log_path = candidate
        # Try a couple of common default names if pattern not supplied
        if log_path is None:
            for name in (
                f"mallet_train_{K}.log",
                f"train_topics_{K}.log",
                f"mallet_{K}.log",
            ):
                candidate = os.path.join(loop_dir, name)
                if os.path.exists(candidate):
                    log_path = candidate
                    break

        if log_path and os.path.exists(log_path):
            try:
                perplexity = mallet_perplexity_from_log(log_path)
            except Exception as e:
                warnings.warn(f"Failed to parse MALLET log for K={K}: {e}")
                perplexity = math.nan
        else:
            warnings.warn(
                f"No MALLET log found for K={K}. Provide mallet_log_paths or mallet_log_pattern to compute perplexity."
            )
            perplexity = math.nan

        return {
            "K": K,
            "Perplexity": float(perplexity) if not (isinstance(perplexity, float) and math.isnan(perplexity)) else math.nan,
            "Coherence": float(mean_coh),
            "Implementation": "mallet",
        }

