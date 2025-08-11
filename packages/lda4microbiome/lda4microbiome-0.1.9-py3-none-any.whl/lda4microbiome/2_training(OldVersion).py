"""
LDA model training using MALLET.

This module contains the LDATrainer class for:
- Setting up directory structure for LDA analysis
- Training MALLET LDA models for different numbers of topics
- Processing and saving model outputs
- Calculating model metrics (perplexity, coherence)
"""

from typing import List, Dict, Tuple, Any
import os
import pandas as pd
import numpy as np
import subprocess
from collections import defaultdict
from gensim import corpora
from gensim.models import LdaModel, CoherenceModel
from gensim.corpora import Dictionary
import little_mallet_wrapper as lmw


class LDATrainer:
    """
    A class for training LDA models across multiple topic numbers and managing results.

    This class handles:
    - Setting up directory structure for LDA analysis
    - Training MALLET LDA models for different numbers of topics
    - Processing and saving model outputs
    - Calculating model metrics (perplexity, coherence)
    - Aggregating results across all models
    """

    def __init__(self, base_directory: str, path_to_mallet: str):
        """
        Initialize the LDA Trainer.

        Args:
            base_directory (str): Base directory for storing all results
            path_to_mallet (str): Path to MALLET executable
        """
        self.base_directory = base_directory
        self.path_to_mallet = path_to_mallet

        # Set up directory structure
        self.paths = self._setup_directories()

        # Initialize result storage
        self.all_df_probabilities_rel = pd.DataFrame()
        self.all_metrics = pd.DataFrame(columns=['Num_MCs', 'Perplexity', 'Coherence'])

        # Data containers (to be set later)
        self.flattened_nested_list = None
        self.sampletable_genusid = None

    def _setup_directories(self) -> Dict[str, str]:
        """Set up directory structure and return path dictionary."""
        intermediate_directory = os.path.join(self.base_directory, 'intermediate')
        loop_directory = os.path.join(self.base_directory, 'lda_loop')
        lda_directory = os.path.join(self.base_directory, 'lda_results')
        MC_sample_directory = os.path.join(lda_directory, 'MC_Sample')
        MC_feature_directory = os.path.join(lda_directory, 'MC_Feature')
        MALLET_diagnostics_directory = os.path.join(lda_directory, 'Diagnostics')

        # Create all directories
        directories = [
            intermediate_directory, loop_directory, lda_directory,
            MC_sample_directory, MC_feature_directory, MALLET_diagnostics_directory
        ]

        print(f"Setting up LDA directory structure in: {self.base_directory}")
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"  ✓ Created/verified: {directory}")

        return {
            'intermediate_directory': intermediate_directory,
            'loop_directory': loop_directory,
            'lda_directory': lda_directory,
            'MC_sample_directory': MC_sample_directory,
            'MC_feature_directory': MC_feature_directory,
            'MALLET_diagnostics_directory': MALLET_diagnostics_directory,
            'path_to_training_data': os.path.join(loop_directory, 'training.txt'),
            'path_to_formatted_training_data': os.path.join(loop_directory, 'mallet.training')
        }

    def load_training_data(self):
        """
        Load training data from files created by TaxonomyProcessor.

        This method automatically loads:
        - flattened_nested_list from training.txt
        - sampletable_genusid from annotated_randomid.csv
        """
        # Load the sample table with random IDs
        sampletable_path = os.path.join(self.paths['intermediate_directory'], 'annotaed_randomid.csv')
        if not os.path.exists(sampletable_path):
            raise FileNotFoundError(f"Sample table not found: {sampletable_path}. Run TaxonomyProcessor first.")

        self.sampletable_genusid = pd.read_csv(sampletable_path, index_col=0)
        print(f"  ✓ Loaded sample table: {self.sampletable_genusid.shape}")

        # Load the flattened nested list from training data
        training_data_path = self.paths['path_to_training_data']
        if not os.path.exists(training_data_path):
            raise FileNotFoundError(f"Training data not found: {training_data_path}. Run TaxonomyProcessor first.")

        with open(training_data_path, 'r') as f:
            self.flattened_nested_list = [line.strip() for line in f]

        print(f"  ✓ Loaded training documents: {len(self.flattened_nested_list)} documents")
        print("Training data loaded successfully.")

    def _generate_file_paths(self, num_topics: int) -> Dict[str, str]:
        """Generate all file paths for a specific number of topics."""
        loop_path = self.paths['loop_directory']
        diagnostics_path = self.paths['MALLET_diagnostics_directory']
        mc_sample_path = self.paths['MC_sample_directory']
        mc_feature_path = self.paths['MC_feature_directory']

        return {
            'model': os.path.join(loop_path, f'mallet.model.{num_topics}'),
            'topic_keys': os.path.join(loop_path, f'mallet.topic_keys.{num_topics}'),
            'topic_distributions': os.path.join(loop_path, f'mallet.topic_distributions.{num_topics}'),
            'word_weights': os.path.join(loop_path, f'mallet.word_weights.{num_topics}'),
            'diagnostics': os.path.join(diagnostics_path, f'mallet.diagnostics.{num_topics}.xml'),
            'sample_probs': os.path.join(mc_sample_path, f'MC_Sample_probabilities{num_topics}.csv'),
            'feature_probs': os.path.join(mc_feature_path, f'MC_Feature_Probabilities_{num_topics}.csv')
        }

    def _create_topic_index(self, num_topics: int) -> List[str]:
        """Create index names for topics."""
        return [f"K{num_topics}_MC{i}" for i in range(num_topics)]

    def _train_single_model(self, num_topics: int, file_paths: Dict[str, str]) -> None:
        """Train a single MALLET LDA model."""

        lmw.import_data(
            self.path_to_mallet,
            self.paths['path_to_training_data'],
            self.paths['path_to_formatted_training_data'],
            self.flattened_nested_list
        )

        # Construct MALLET command
        mallet_command = [
            self.path_to_mallet,
            'train-topics',
            '--input', self.paths['path_to_formatted_training_data'],
            '--num-topics', str(num_topics),
            '--output-state', file_paths['model'],
            '--output-topic-keys', file_paths['topic_keys'],
            '--output-doc-topics', file_paths['topic_distributions'],
            '--word-topic-counts-file', file_paths['word_weights'],
            '--diagnostics-file', file_paths['diagnostics'],
            '--optimize-interval', '10',
            '--num-iterations', '1000',
            '--random-seed', '43'
        ]

        # Run MALLET
        print(f"Running MALLET for {num_topics} microbial components...")
        subprocess.run(mallet_command, check=True)
        print(f"Completed MALLET for {num_topics} microbial components.")

    def _process_model_output(self, num_topics: int, file_paths: Dict[str, str]) -> Tuple[pd.DataFrame, List]:
        """Process MALLET model output and save individual results."""
        # Load model output
        topic_distributions, word_topics = self._load_mallet_model_output(
            file_paths['topic_distributions'], 
            file_paths['word_weights']
        )

        # Create topic index
        topic_index = self._create_topic_index(num_topics)

        # Process ASV data
        df_asv = pd.DataFrame(word_topics, columns=['MC', 'Term', 'Frequency'])
        df_asv_pivot = df_asv.pivot_table(index='MC', columns='Term', values='Frequency', fill_value=0)
        df_asv_probabilities = df_asv_pivot.div(df_asv_pivot.sum(axis=1), axis=0)
        df_asv_probabilities.index = topic_index

        # Create topic distribution DataFrame
        df_topic_dist = pd.DataFrame(
            topic_distributions,
            index=self.sampletable_genusid.index,
            columns=topic_index
        )
        df_topic_dist_wide = df_topic_dist.T

        # Save individual results
        df_topic_dist_wide.to_csv(file_paths['sample_probs'], index=True)
        df_asv_probabilities.to_csv(file_paths['feature_probs'], index=True)
        print(f"Saved individual model results for {num_topics} topics.")

        return df_asv_probabilities, topic_distributions, word_topics

    def _load_mallet_model_output(self, topic_distributions_path: str, word_weights_path: str) -> Tuple[List, List]:
        """
        Load MALLET model output files.

        Args:
            topic_distributions_path: Path to topic distributions file
            word_weights_path: Path to word weights file

        Returns:
            Tuple of (topic_distributions, word_topics)
        """
        # Load topic distributions

        topic_distributions = lmw.load_topic_distributions(topic_distributions_path)

        # Load word weights
        word_topics = []
        with open(word_weights_path, 'r') as f:
            for line in f:
                parts = line.split()
                try:
                    if len(parts) < 2:
                        raise ValueError("Line does not have enough parts")

                    word = parts[1]
                    topic_freq_pairs = parts[2:]

                    for pair in topic_freq_pairs:
                        topic_id, frequency = pair.split(':')
                        word_topics.append((int(topic_id), word, int(frequency)))

                except ValueError as e:
                    # Log or print the problematic line for debugging
                    print(f"Skipping line due to format issues: {line} - Error: {e}")

        return topic_distributions, word_topics

    def _calculate_perplexity(self, topic_distributions: List, epsilon: float = 1e-10) -> float:
        """
        Calculate perplexity for topic distributions.

        Args:
            topic_distributions: List of topic probability distributions
            epsilon: Small value to avoid log(0)

        Returns:
            Average perplexity across all samples
        """
        perplexities = []

        for distribution in topic_distributions:
            # Ensure the distribution doesn't have zero values by clipping
            distribution = np.clip(distribution, epsilon, 1.0)
            # Calculate the entropy for this distribution
            entropy = -np.sum(np.log(distribution) * distribution)
            # Calculate perplexity and store it
            perplexities.append(np.exp(entropy))

        # Return the average perplexity over all samples
        return np.mean(perplexities)

    def _calculate_coherence(self, word_topics: List, texts: List, top_n: int = 10) -> float:
        """
        Calculate coherence score for topics.

        Args:
            word_topics: List of (topic_id, word, frequency) tuples
            texts: List of document texts
            top_n: Number of top words to use for coherence calculation

        Returns:
            Coherence score
        """
        try:
            # Ensure texts are in the correct format (list of lists of words)
            processed_texts = []
            for text in texts:
                if isinstance(text, str):
                    # Split by whitespace and filter out empty strings
                    words = [word.strip() for word in text.split() if word.strip()]
                    processed_texts.append(words)
                elif isinstance(text, list):
                    # Already a list, but ensure all elements are strings
                    words = [str(word).strip() for word in text if str(word).strip()]
                    processed_texts.append(words)
                else:
                    print(f"Warning: Unexpected input type: {type(text)}. Skipping.")
                    continue

            if not processed_texts:
                raise ValueError("No valid texts found after processing")

            # Create dictionary from processed texts
            id2word = Dictionary(processed_texts)

            # Group word_topics by topic number
            topics_dict = defaultdict(list)
            for topic_num, word, freq in word_topics:
                # Ensure word is a string and exists in dictionary
                word_str = str(word).strip()
                if word_str in id2word.token2id:
                    topics_dict[topic_num].append((word_str, float(freq)))

            if not topics_dict:
                raise ValueError("No valid topics found in word_topics")

            # Extract top N words for each topic
            topics = []
            for topic_num, word_freqs in topics_dict.items():
                # Sort words by frequency (descending) and take top N
                top_words = [word for word, freq in sorted(word_freqs, key=lambda x: x[1], reverse=True)[:top_n]]
                if top_words:  # Only add non-empty topics
                    topics.append(top_words)

            if not topics:
                raise ValueError("No valid topics extracted")

            # Calculate coherence using 'c_v' measure with texts (not corpus)
            coherence_model = CoherenceModel(
                topics=topics, 
                texts=processed_texts,  # Use texts, not corpus
                dictionary=id2word, 
                coherence='c_v'
            )

            coherence_score = coherence_model.get_coherence()

            print(f"Coherence calculated successfully: {coherence_score:.4f}")
            return coherence_score

        except Exception as e:
            print(f"Error calculating coherence: {str(e)}")
            # Return a default value or re-raise depending on your needs
            return 0.0

    def train_models(self, MC_range: List[int] = None, range_str: str = None) -> Dict[str, Any]:
        """
        Train LDA models for a range of topic numbers.

        Args:
            MC_range: List of numbers of topics to train. If None, defaults to range(2, 21)
            range_str: String representation of range for file naming

        Returns:
            Dictionary containing all results and metrics
        """
        # Set default range if not provided
        if MC_range is None:
            MC_range = list(range(2, 21))
            print("No range provided. Using default range: 2-20 topics")
        
        # Ensure MC_range is a list
        if not isinstance(MC_range, list):
            MC_range = list(MC_range)
        
        # Load training data automatically
        print("Loading training data...")
        self.load_training_data()

        if range_str is None:
            range_str = f"{min(MC_range)}-{max(MC_range)}"

        print("="*60)
        print(f"Starting LDA training for {len(MC_range)} different topic numbers...")
        print(f"Topic range: {MC_range}")
        print("="*60)

        for num_topics in MC_range:
            print(f"\n--- Processing {num_topics} topics ---")

            # Generate file paths
            file_paths = self._generate_file_paths(num_topics)

            # Train model
            self._train_single_model(num_topics, file_paths)

            # Process output
            df_asv_probabilities, topic_distributions, word_topics = self._process_model_output(num_topics, file_paths)

            # Calculate metrics
            perplexity = self._calculate_perplexity(topic_distributions)
            coherence = self._calculate_coherence(word_topics, self.flattened_nested_list)

            # Store results
            self.all_df_probabilities_rel = pd.concat([self.all_df_probabilities_rel, df_asv_probabilities])

            new_row = pd.DataFrame([{
                'Num_MCs': num_topics,
                'Perplexity': perplexity,
                'Coherence': coherence
            }])
            self.all_metrics = pd.concat([self.all_metrics, new_row], ignore_index=True)

            print(f"Processed and appended results for {num_topics} MCs.")

        # Save final results
        self._save_final_results(range_str)

        return {
            'probabilities': self.all_df_probabilities_rel,
            'metrics': self.all_metrics,
            'paths': self.paths
        }

    def _save_final_results(self, range_str: str):
        """Save final combined results."""
        prob_path = os.path.join(self.paths['loop_directory'], f'all_MC_probabilities_rel_{range_str}.csv')
        metrics_path = os.path.join(self.paths['lda_directory'], f'all_MC_metrics_{range_str}.csv')

        self.all_df_probabilities_rel.to_csv(prob_path)
        self.all_metrics.to_csv(metrics_path)

        print("="*60)
        print("Training complete! Final results saved:")
        print(f"  • Probabilities: {prob_path}")
        print(f"  • Metrics: {metrics_path}")
        print("="*60)






















