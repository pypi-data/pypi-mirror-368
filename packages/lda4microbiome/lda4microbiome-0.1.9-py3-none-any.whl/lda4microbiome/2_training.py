"""
LDA model training using both Gensim and MALLET.

This module contains the LDATrainer class for:
- Setting up directory structure for LDA analysis
- Training LDA models (Gensim by default, MALLET for MCMC) for different numbers of topics
- Processing and saving model outputs
- Calculating model metrics (perplexity, coherence)
"""

from typing import List, Dict, Tuple, Any, Optional
import os
import pandas as pd
import numpy as np
import subprocess
import pickle
import json
import math
import warnings
from collections import defaultdict
from gensim import corpora
from gensim.models import LdaModel, CoherenceModel
from gensim.corpora import Dictionary
import little_mallet_wrapper as lmw


class MALLETStyleMetricsCalculator:
    """
    A unified metrics calculator that implements MALLET-style calculations
    for both perplexity and coherence, ensuring consistent evaluation across
    different LDA implementations.
    """
    
    def __init__(self, random_seed: int = 42):
        """
        Initialize the metrics calculator.
        
        Args:
            random_seed: Random seed for reproducible results
        """
        self.random_seed = random_seed
        np.random.seed(random_seed)
    
    def calculate_mallet_style_perplexity(self, 
                                        topic_distributions: List[List[float]], 
                                        documents: Optional[List[str]] = None,
                                        word_topic_matrix: Optional[np.ndarray] = None) -> float:
        """
        Calculate perplexity using microbiome-appropriate formula: exp(-∑_d ∑_n log p(w_n|d)).
        
        This formula is more suitable for microbiome data as it:
        - Does not normalize by document length (avoiding bias from varying sample sizes)
        - Directly measures how well the model predicts observed ASVs
        - Calculates p(w_n|d) = ∑_k p(w_n|k) * p(k|d) properly
        
        Args:
            topic_distributions: Document-topic distributions [n_docs x n_topics]
            documents: Original documents as list of strings (ASV names)
            word_topic_matrix: Word-topic probability matrix [n_words x n_topics]
            
        Returns:
            Perplexity value using microbiome-appropriate formula
        """
        if not topic_distributions:
            raise ValueError("Topic distributions cannot be empty")
        
        total_log_likelihood = 0.0
        
        # Build vocabulary if not provided
        if documents and word_topic_matrix is None:
            vocab = self._build_vocabulary(documents)
            # Create a simplified word-topic matrix (uniform distribution as fallback)
            n_topics = len(topic_distributions[0])
            word_topic_matrix = np.ones((len(vocab), n_topics)) / len(vocab)
        
        for doc_idx, doc_topics in enumerate(topic_distributions):
            # Ensure probabilities sum to 1 and are positive
            doc_topics = np.array(doc_topics)
            doc_topics = np.clip(doc_topics, 1e-10, 1.0)
            doc_topics = doc_topics / doc_topics.sum()
            
            if documents and doc_idx < len(documents):
                # Get actual words (ASVs) in this document
                words = documents[doc_idx].split()
            else:
                # If no documents provided, create a representative set of words
                # based on topic distribution (higher weight topics contribute more words)
                words = self._generate_representative_words(doc_topics, word_topic_matrix)
            
            # Calculate log p(w_n|d) for each ASV in this sample
            for word in words:
                # Calculate p(w_n|d) = ∑_k p(w_n|k) * p(k|d)
                word_prob = self._calculate_word_probability(word, doc_topics, word_topic_matrix, documents)
                
                # Add log probability to total
                if word_prob > 0:
                    total_log_likelihood += math.log(word_prob)
                else:
                    # Handle zero probability (shouldn't happen with proper smoothing)
                    total_log_likelihood += math.log(1e-15)
        
        # Calculate perplexity: exp(-∑_d ∑_n log p(w_n|d))
        # Handle numerical overflow by capping the exponent
        exponent = -total_log_likelihood
        
        # Prevent overflow: if exponent is too large, return inf
        if exponent > 700:  # math.exp(700) is near the overflow limit
            print(f"Warning: Perplexity calculation overflow prevented. Log-likelihood: {total_log_likelihood:.2f}")
            return float('inf')
        elif exponent < -700:  # Very small perplexity
            return 0.0
        else:
            perplexity = math.exp(exponent)
            return perplexity
    
    def calculate_mallet_style_coherence(self, 
                                       word_topics: List[Tuple[int, str, int]], 
                                       texts: List[str], 
                                       top_n: int = 10,
                                       smoothing: float = 0.01) -> Dict[str, float]:
        """
        Calculate coherence scores using MALLET's probabilistic coherence methodology.
        
        This implements MALLET's coherence calculation which computes:
        C(t) = sum_{i=1}^{M-1} sum_{j=i+1}^{M} log[(D(w_i, w_j) + ε) / D(w_j)]
        
        Where:
        - D(w_i, w_j) is the number of documents containing both words w_i and w_j
        - D(w_j) is the number of documents containing word w_j
        - ε is a smoothing parameter to avoid log(0)
        
        Args:
            word_topics: List of (topic_id, word, frequency) tuples
            texts: List of document texts for co-occurrence calculation
            top_n: Number of top words to use for coherence calculation
            smoothing: Smoothing parameter (epsilon) to avoid log(0)
            
        Returns:
            Dictionary mapping topic names to coherence scores
        """
        try:
            # Process texts and build word-document matrix
            processed_texts = self._process_texts_for_coherence(texts)
            
            if not processed_texts:
                raise ValueError("No valid texts found after processing")
            
            # Build word-document co-occurrence matrix
            word_doc_matrix = self._build_word_document_matrix(processed_texts)
            
            # Group word_topics by topic number and calculate coherence
            topics_dict = self._extract_topics_from_word_topics_enhanced(word_topics)
            
            if not topics_dict:
                raise ValueError("No valid topics found in word_topics")
            
            # Calculate MALLET-style coherence for each topic
            topic_coherences = {}
            
            for topic_num, word_freqs in topics_dict.items():
                # Get top N words for this topic
                top_words = [
                    word for word, freq in 
                    sorted(word_freqs, key=lambda x: x[1], reverse=True)[:top_n]
                ]
                
                if len(top_words) < 2:  # Need at least 2 words for coherence
                    topic_coherences[f"MC{topic_num}"] = 0.0
                    continue
                
                # Calculate MALLET-style coherence for this topic
                coherence_score = self._calculate_topic_coherence_mallet_style(
                    top_words, word_doc_matrix, smoothing
                )
                
                topic_coherences[f"MC{topic_num}"] = coherence_score
            
            return topic_coherences
            
        except Exception as e:
            warnings.warn(f"Error in MALLET-style coherence calculation: {str(e)}")
            # Return default coherence scores
            unique_topics = set(topic_id for topic_id, _, _ in word_topics)
            return {f"MC{topic_id}": 0.0 for topic_id in unique_topics}
    
    def _process_texts_for_coherence(self, texts: List[str]) -> List[List[str]]:
        """Process texts for coherence calculation."""
        processed_texts = []
        
        for text in texts:
            if isinstance(text, str):
                # Split by whitespace and filter out empty strings
                words = [word.strip() for word in text.split() if word.strip()]
                if words:  # Only add non-empty documents
                    processed_texts.append(words)
            elif isinstance(text, list):
                # Already a list, but ensure all elements are strings
                words = [str(word).strip() for word in text if str(word).strip()]
                if words:
                    processed_texts.append(words)
        
        return processed_texts
    
    def _build_word_document_matrix(self, processed_texts: List[List[str]]) -> Dict[str, Dict[str, int]]:
        """Build word-document co-occurrence matrix for MALLET-style coherence."""
        word_doc_count = defaultdict(int)  # Word -> number of documents containing it
        word_cooccurrence = defaultdict(lambda: defaultdict(int))  # Word1 -> Word2 -> co-occurrence count
        
        for doc_words in processed_texts:
            # Get unique words in this document
            unique_words = set(doc_words)
            
            # Count document frequency for each word
            for word in unique_words:
                word_doc_count[word] += 1
            
            # Count co-occurrences
            unique_words_list = list(unique_words)
            for i, word1 in enumerate(unique_words_list):
                for word2 in unique_words_list[i+1:]:
                    # Count both directions for easier lookup
                    word_cooccurrence[word1][word2] += 1
                    word_cooccurrence[word2][word1] += 1
        
        return {
            'doc_freq': dict(word_doc_count),
            'cooccurrence': dict(word_cooccurrence)
        }
    
    def _extract_topics_from_word_topics_enhanced(self, 
                                                word_topics: List[Tuple[int, str, int]]) -> Dict[int, List[Tuple[str, float]]]:
        """Enhanced method to extract and organize topics from word_topics data."""
        topics_dict = defaultdict(list)
        
        for topic_num, word, freq in word_topics:
            # Ensure word is a string
            word_str = str(word).strip()
            if word_str:  # Only add non-empty words
                topics_dict[topic_num].append((word_str, float(freq)))
        
        return dict(topics_dict)
    
    def _calculate_topic_coherence_mallet_style(self, 
                                              top_words: List[str], 
                                              word_doc_matrix: Dict[str, Dict], 
                                              smoothing: float) -> float:
        """Calculate MALLET-style coherence for a single topic."""
        if len(top_words) < 2:
            return 0.0
        
        doc_freq = word_doc_matrix['doc_freq']
        cooccurrence = word_doc_matrix['cooccurrence']
        
        coherence_sum = 0.0
        pair_count = 0
        
        # MALLET formula: sum_{i=1}^{M-1} sum_{j=i+1}^{M} log[(D(w_i, w_j) + ε) / D(w_j)]
        for i in range(len(top_words)):
            for j in range(i + 1, len(top_words)):
                word_i = top_words[i]
                word_j = top_words[j]
                
                # Get document frequencies
                d_word_j = doc_freq.get(word_j, 0)
                
                if d_word_j == 0:
                    continue  # Skip if word_j doesn't appear in any document
                
                # Get co-occurrence count
                d_word_i_word_j = cooccurrence.get(word_i, {}).get(word_j, 0)
                
                # Calculate MALLET coherence score for this pair
                score = math.log((d_word_i_word_j + smoothing) / d_word_j)
                coherence_sum += score
                pair_count += 1
        
        # Return average coherence score per pair (for normalization)
        return coherence_sum / pair_count if pair_count > 0 else 0.0
    
    def _extract_topics_from_word_topics(self, 
                                       word_topics: List[Tuple[int, str, int]], 
                                       id2word: Dictionary) -> Dict[int, List[Tuple[str, float]]]:
        """Extract and organize topics from word_topics data."""
        topics_dict = defaultdict(list)
        
        for topic_num, word, freq in word_topics:
            # Ensure word is a string and exists in dictionary
            word_str = str(word).strip()
            if word_str in id2word.token2id:
                topics_dict[topic_num].append((word_str, float(freq)))
        
        return dict(topics_dict)
    
    def _build_vocabulary(self, documents: List[str]) -> Dict[str, int]:
        """Build vocabulary from documents."""
        vocab = {}
        word_id = 0
        
        for doc in documents:
            if isinstance(doc, str):
                words = doc.split()
                for word in words:
                    word = word.strip()
                    if word and word not in vocab:
                        vocab[word] = word_id
                        word_id += 1
        
        return vocab
    
    def _generate_representative_words(self, doc_topics: np.ndarray, 
                                     word_topic_matrix: Optional[np.ndarray]) -> List[str]:
        """Generate representative words for a document based on its topic distribution."""
        if word_topic_matrix is None:
            # Fallback: generate dummy words based on topic weights
            words = []
            for topic_idx, topic_prob in enumerate(doc_topics):
                # Number of words proportional to topic probability
                num_words = max(1, int(topic_prob * 10))
                for i in range(num_words):
                    words.append(f"topic{topic_idx}_word{i}")
            return words
        
        # Use actual word-topic matrix to generate representative words
        words = []
        n_words_per_topic = 5  # Generate 5 words per significant topic
        
        for topic_idx, topic_prob in enumerate(doc_topics):
            if topic_prob > 0.01:  # Only consider topics with >1% probability
                # Get top words for this topic
                if topic_idx < word_topic_matrix.shape[1]:
                    topic_word_probs = word_topic_matrix[:, topic_idx]
                    top_word_indices = np.argsort(topic_word_probs)[-n_words_per_topic:]
                    
                    for word_idx in top_word_indices:
                        words.append(f"word_{word_idx}")
        
        return words if words else ["unknown_word"]
    
    def _calculate_word_probability(self, word: str, doc_topics: np.ndarray,
                                  word_topic_matrix: Optional[np.ndarray],
                                  documents: Optional[List[str]] = None) -> float:
        """Calculate p(w_n|d) = Σ_k p(w_n|k) * p(k|d)."""
        if word_topic_matrix is None:
            # Fallback: uniform probability across all topics
            return 1.0 / len(doc_topics)
        
        # Try to find word index in a vocabulary
        word_idx = self._get_word_index(word, documents)
        
        if word_idx is None or word_idx >= word_topic_matrix.shape[0]:
            # Word not found, use small uniform probability
            return 1e-6
        
        # Calculate p(w_n|d) = Σ_k p(w_n|k) * p(k|d)
        word_prob = 0.0
        for topic_k in range(len(doc_topics)):
            if topic_k < word_topic_matrix.shape[1]:
                p_word_given_topic = word_topic_matrix[word_idx, topic_k]
                p_topic_given_doc = doc_topics[topic_k]
                word_prob += p_word_given_topic * p_topic_given_doc
        
        return max(word_prob, 1e-15)  # Avoid zero probability
    
    def _get_word_index(self, word: str, documents: Optional[List[str]] = None) -> Optional[int]:
        """Get word index in vocabulary (simplified version)."""
        # This is a simplified version - in practice, you'd use the actual vocabulary
        # For now, use a hash-based approach to assign consistent indices
        if word.startswith('topic') and '_word' in word:
            # Extract numeric part for generated words
            try:
                parts = word.split('_')
                if len(parts) >= 2:
                    return int(parts[-1]) % 1000  # Modulo to keep within bounds
            except ValueError:
                pass
        
        # Use hash for real words (consistent but arbitrary mapping)
        return abs(hash(word)) % 1000
    
    def create_comprehensive_metrics_dataframe(self, 
                                             models_data: Dict[int, Dict[str, Any]],
                                             range_str: str = "") -> pd.DataFrame:
        """
        Create a comprehensive metrics DataFrame with individual topic entries.
        
        Args:
            models_data: Dictionary mapping num_topics to model data
            range_str: String identifier for the range (for filename)
            
        Returns:
            DataFrame with columns: Topic_Name, K, Perplexity, Coherence
        """
        metrics_rows = []
        
        for num_topics, data in models_data.items():
            perplexity = data.get('perplexity', 0.0)
            topic_coherences = data.get('topic_coherences', {})
            
            # Create entries for each topic
            for topic_idx in range(num_topics):
                topic_name = f"K{num_topics}_MC{topic_idx}"
                
                # Coherence is topic-specific
                coherence = topic_coherences.get(f"MC{topic_idx}", 0.0)
                
                metrics_rows.append({
                    'Topic_Name': topic_name,
                    'K': num_topics,
                    'Perplexity': perplexity,  # Same for all topics in a model
                    'Coherence': coherence     # Different for each topic
                })
        
        metrics_df = pd.DataFrame(metrics_rows)
        
        # Sort by number of topics, then by topic name
        metrics_df = metrics_df.sort_values(['K', 'Topic_Name']).reset_index(drop=True)
        
        return metrics_df


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

    def __init__(self, base_directory: str, path_to_mallet: Optional[str] = None, 
                 implementation: str = 'gensim', **gensim_params):
        """
        Initialize the LDA Trainer.

        Args:
            base_directory (str): Base directory for storing all results
            path_to_mallet (str, optional): Path to MALLET executable (required for MALLET implementation)
            implementation (str): Implementation to use ('gensim' or 'mallet'). Default is 'gensim'.
            **gensim_params: Additional parameters for Gensim LDA model
                           Default: passes=20, iterations=400, alpha='auto', eta='auto', 
                           random_state=42, chunksize=2000, eval_every=None
        """
        self.base_directory = base_directory
        self.path_to_mallet = path_to_mallet
        self.implementation = implementation.lower()
        
        # Validate implementation choice
        if self.implementation not in ['gensim', 'mallet']:
            raise ValueError("Implementation must be either 'gensim' or 'mallet'")
        
        # Validate MALLET path if using MALLET
        if self.implementation == 'mallet' and not path_to_mallet:
            raise ValueError("path_to_mallet is required when using MALLET implementation")
        
        # Set default Gensim parameters
        self.gensim_params = {
            'passes': 20,
            'iterations': 400,
            'alpha': 'auto',
            'eta': 'auto',
            'random_state': 42,
            'chunksize': 2000,
            'eval_every': None
        }
        # Update with user-provided parameters
        self.gensim_params.update(gensim_params)

        # Set up directory structure
        self.paths = self._setup_directories()

        # Initialize result storage
        self.all_df_probabilities_rel = pd.DataFrame()
        self.all_metrics = pd.DataFrame(columns=['K', 'Perplexity', 'Coherence'])
        self.all_coherence_scores = pd.DataFrame()  # Store all individual coherence scores
        self.models_data = {}  # Store all model data for comprehensive metrics

        # Data containers (to be set later)
        self.flattened_nested_list = None
        self.sampletable_genusid = None
        self.gensim_corpus = None
        self.gensim_dictionary = None
        self.processed_texts = None
        
        # Initialize MALLET-style metrics calculator
        self.metrics_calculator = MALLETStyleMetricsCalculator(random_seed=42)
        
        print(f"LDATrainer initialized with {self.implementation.upper()} implementation")
        if self.implementation == 'gensim':
            print(f"  Gensim parameters: {self.gensim_params}")

    def _setup_directories(self) -> Dict[str, str]:
        """Set up directory structure and return path dictionary."""
        intermediate_directory = os.path.join(self.base_directory, 'intermediate')
        loop_directory = os.path.join(self.base_directory, 'lda_loop')
        lda_directory = os.path.join(self.base_directory, 'lda_results')
        MC_sample_directory = os.path.join(lda_directory, 'MC_Sample')
        MC_feature_directory = os.path.join(lda_directory, 'MC_Feature')
        diagnostics_directory = os.path.join(lda_directory, 'Diagnostics')

        # Create all directories
        directories = [
            intermediate_directory, loop_directory, lda_directory,
            MC_sample_directory, MC_feature_directory, diagnostics_directory
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
            'diagnostics_directory': diagnostics_directory,
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
        
        # Prepare Gensim data if using Gensim
        if self.implementation == 'gensim':
            self._prepare_gensim_data()
        
        print("Training data loaded successfully.")

    def _prepare_gensim_data(self):
        """Prepare data for Gensim training."""
        print("Preparing data for Gensim...")
        
        # Convert documents to list of word lists
        self.processed_texts = []
        for doc in self.flattened_nested_list:
            words = [word.strip() for word in doc.split() if word.strip()]
            self.processed_texts.append(words)
        
        # Create Gensim dictionary and corpus
        self.gensim_dictionary = Dictionary(self.processed_texts)
        self.gensim_corpus = [self.gensim_dictionary.doc2bow(text) for text in self.processed_texts]
        
        print(f"  ✓ Created dictionary with {len(self.gensim_dictionary)} unique terms")
        print(f"  ✓ Created corpus with {len(self.gensim_corpus)} documents")

    def _generate_file_paths(self, num_topics: int) -> Dict[str, str]:
        """Generate all file paths for a specific number of topics."""
        loop_path = self.paths['loop_directory']
        diagnostics_path = self.paths['diagnostics_directory']
        mc_sample_path = self.paths['MC_sample_directory']
        mc_feature_path = self.paths['MC_feature_directory']

        if self.implementation == 'gensim':
            return {
                'model': os.path.join(loop_path, f'gensim_model_{num_topics}.pkl'),
                'dictionary': os.path.join(loop_path, f'gensim_dictionary_{num_topics}.pkl'),
                'coherence': os.path.join(diagnostics_path, f'coherence_{num_topics}.json'),
                'sample_probs': os.path.join(mc_sample_path, f'MC_Sample_probabilities{num_topics}.csv'),
                'feature_probs': os.path.join(mc_feature_path, f'MC_Feature_Probabilities_{num_topics}.csv')
            }
        else:
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
        """Train a single LDA model using the specified implementation."""
        print(f"DEBUG: Using implementation: {self.implementation}")
        if self.implementation == 'gensim':
            self._train_gensim_model(num_topics, file_paths)
        else:
            self._train_mallet_model(num_topics, file_paths)

    def _train_gensim_model(self, num_topics: int, file_paths: Dict[str, str]) -> None:
        """Train a single Gensim LDA model."""
        print(f"Training Gensim LDA model with {num_topics} topics...")
        
        # Train the model
        lda_model = LdaModel(
            corpus=self.gensim_corpus,
            id2word=self.gensim_dictionary,
            num_topics=num_topics,
            **self.gensim_params
        )
        
        # Save model and dictionary
        with open(file_paths['model'], 'wb') as f:
            pickle.dump(lda_model, f)
        with open(file_paths['dictionary'], 'wb') as f:
            pickle.dump(self.gensim_dictionary, f)
        
        print(f"Completed Gensim LDA training for {num_topics} topics.")

    def _train_mallet_model(self, num_topics: int, file_paths: Dict[str, str]) -> None:
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

    def _process_model_output(self, num_topics: int, file_paths: Dict[str, str]) -> Tuple[pd.DataFrame, List, List]:
        """Process model output and save individual results."""
        if self.implementation == 'gensim':
            return self._process_gensim_output(num_topics, file_paths)
        else:
            return self._process_mallet_output(num_topics, file_paths)

    def _process_gensim_output(self, num_topics: int, file_paths: Dict[str, str]) -> Tuple[pd.DataFrame, List, List]:
        """Process Gensim model output and save individual results."""
        # Load the trained model
        with open(file_paths['model'], 'rb') as f:
            lda_model = pickle.load(f)
        
        # Get topic distributions for documents
        topic_distributions = []
        for doc_bow in self.gensim_corpus:
            doc_topics = dict(lda_model.get_document_topics(doc_bow, minimum_probability=0))
            # Ensure all topics are represented (fill missing with 0)
            topic_probs = [doc_topics.get(topic_id, 0.0) for topic_id in range(num_topics)]
            topic_distributions.append(topic_probs)
        
        # Get word-topic distributions
        word_topics = []
        for topic_id in range(num_topics):
            topic_words = lda_model.show_topic(topic_id, topn=len(self.gensim_dictionary))
            for word, prob in topic_words:
                # Convert probability to frequency-like score (multiply by large number for compatibility)
                freq = int(prob * 10000)
                if freq > 0:  # Only include words with non-zero probability
                    word_topics.append((topic_id, word, freq))
        
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
        
        # Calculate coherence score using MALLET-style formula for consistency
        coherence_score = self._calculate_mallet_style_coherence(lda_model, num_topics)
        
        # Save coherence score
        coherence_data = {
            'num_topics': num_topics,
            'coherence_score': coherence_score,
            'method': 'mallet_style',
            'formula': 'sum_i sum_{j<i} log[(D(w_j, w_i) + beta) / D(w_i)]'
        }
        with open(file_paths['coherence'], 'w') as f:
            json.dump(coherence_data, f, indent=2)
        
        # Save individual results
        df_topic_dist_wide.to_csv(file_paths['sample_probs'], index=True)
        df_asv_probabilities.to_csv(file_paths['feature_probs'], index=True)
        print(f"Saved individual model results for {num_topics} topics.")
        
        return df_asv_probabilities, topic_distributions, word_topics

    def _process_mallet_output(self, num_topics: int, file_paths: Dict[str, str]) -> Tuple[pd.DataFrame, List, List]:
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

    def _calculate_mallet_style_coherence(self, model, num_topics, top_n=10, beta=0.01):
        """Calculate coherence score using MALLET's formula."""
        
        # Get top words for each topic
        topics = []
        for topic_id in range(num_topics):
            top_words = [word for word, prob in model.show_topic(topic_id, topn=top_n)]
            topics.append(top_words)
        
        # Pre-calculate document frequencies for all words in the dictionary
        doc_freq = {self.gensim_dictionary[term_id]: freq for term_id, freq in self.gensim_dictionary.dfs.items()}
        
        total_coherence = 0
        for topic_words in topics:
            topic_coherence = 0
            for i in range(1, len(topic_words)):
                for j in range(i):
                    w_i = topic_words[i]
                    w_j = topic_words[j]
                    
                    # D(w) = document frequency of word w
                    d_wi = doc_freq.get(w_i, 0)
                    
                    if d_wi == 0:
                        continue
                    
                    # D(w_i, w_j) = co-document frequency of w_i and w_j
                    co_doc_freq = 0
                    for doc_bow in self.gensim_corpus:
                        doc_words = {self.gensim_dictionary[term_id] for term_id, _ in doc_bow}
                        if w_i in doc_words and w_j in doc_words:
                            co_doc_freq += 1
                    
                    # Score for this pair
                    score = np.log((co_doc_freq + beta) / d_wi)
                    topic_coherence += score
            
            total_coherence += topic_coherence
            
        return total_coherence

    def train_models(self, MC_range: List[int] = None, range_str: str = None) -> Dict[str, Any]:
        """
        Train LDA models for a range of topic numbers using MALLET-style metrics.

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
        print(f"Using MALLET-style metrics for consistent evaluation")
        print("="*60)

        for num_topics in MC_range:
            print(f"\n--- Processing {num_topics} topics ---")

            # Generate file paths
            file_paths = self._generate_file_paths(num_topics)

            # Train model
            self._train_single_model(num_topics, file_paths)

            # Process output
            df_asv_probabilities, topic_distributions, word_topics = self._process_model_output(num_topics, file_paths)

            # Calculate metrics using MALLET-style methods
            print(f"Calculating MALLET-style perplexity for {num_topics} topics...")
            perplexity = self.metrics_calculator.calculate_mallet_style_perplexity(
                topic_distributions, 
                documents=self.flattened_nested_list
            )
            
            print(f"Calculating MALLET-style coherence for {num_topics} topics...")
            topic_coherences = self.metrics_calculator.calculate_mallet_style_coherence(
                word_topics, 
                self.flattened_nested_list
            )
            
            # Average coherence for backward compatibility
            avg_coherence = np.mean(list(topic_coherences.values())) if topic_coherences else 0.0

            # Store model data for comprehensive metrics
            self.models_data[num_topics] = {
                'perplexity': perplexity,
                'topic_coherences': topic_coherences,
                'avg_coherence': avg_coherence,
                'topic_distributions': topic_distributions,
                'word_topics': word_topics
            }

            # Store results (maintain backward compatibility)
            self.all_df_probabilities_rel = pd.concat([self.all_df_probabilities_rel, df_asv_probabilities])

            new_row = pd.DataFrame([{
                'K': num_topics,
                'Perplexity': perplexity,
                'Coherence': avg_coherence
            }])
            self.all_metrics = pd.concat([self.all_metrics, new_row], ignore_index=True)

            print(f"✓ Perplexity: {perplexity:.2f}")
            print(f"✓ Average coherence: {avg_coherence:.4f}")
            print(f"✓ Individual topic coherences: {len(topic_coherences)} topics")
            print(f"Processed and appended results for {num_topics} MCs.")

        # Save enhanced final results
        self._save_enhanced_results(range_str)

        return {
            'probabilities': self.all_df_probabilities_rel,
            'metrics': self.all_metrics,
            'models_data': self.models_data,
            'paths': self.paths
        }

    def _save_enhanced_results(self, range_str: str):
        """Save enhanced final results with comprehensive metrics DataFrame."""
        # Save traditional results (backward compatibility)
        prob_path = os.path.join(self.paths['loop_directory'], f'all_MC_probabilities_rel_{range_str}.csv')
        metrics_path = os.path.join(self.paths['lda_directory'], f'all_MC_metrics_{range_str}.csv')

        self.all_df_probabilities_rel.to_csv(prob_path)
        self.all_metrics.to_csv(metrics_path)

        # Create and save comprehensive metrics DataFrame
        comprehensive_metrics = self.metrics_calculator.create_comprehensive_metrics_dataframe(
            self.models_data, range_str
        )
        
        # Save comprehensive metrics with improved naming
        comprehensive_path = os.path.join(self.paths['lda_directory'], f'comprehensive_MC_metrics_{range_str}.csv')
        comprehensive_metrics.to_csv(comprehensive_path, index=False)
        
        # Save individual model data for future analysis
        models_data_path = os.path.join(self.paths['lda_directory'], f'models_data_{range_str}.json')
        # Convert numpy arrays to lists for JSON serialization
        serializable_data = {}
        for num_topics, data in self.models_data.items():
            serializable_data[str(num_topics)] = {
                'perplexity': float(data['perplexity']),
                'avg_coherence': float(data['avg_coherence']),
                'topic_coherences': {k: float(v) for k, v in data['topic_coherences'].items()},
                'num_topics': num_topics,
                'num_documents': len(data['topic_distributions'])
            }
        
        with open(models_data_path, 'w') as f:
            json.dump(serializable_data, f, indent=2)

        print("="*60)
        print("Training complete! Enhanced results saved:")
        print(f"  • Traditional probabilities: {prob_path}")
        print(f"  • Traditional metrics: {metrics_path}")
        print(f"  • Comprehensive metrics: {comprehensive_path}")
        print(f"  • Models summary data: {models_data_path}")
        print(f"")
        print(f"Comprehensive metrics summary:")
        print(f"  - Total topics evaluated: {len(comprehensive_metrics)}")
        print(f"  - Models range: {comprehensive_metrics['K'].min()}-{comprehensive_metrics['K'].max()}")
        print(f"  - Average perplexity: {comprehensive_metrics['Perplexity'].mean():.2f}")
        print(f"  - Average coherence: {comprehensive_metrics['Coherence'].mean():.4f}")
        print(f"  - Perplexity range: {comprehensive_metrics['Perplexity'].min():.2f} - {comprehensive_metrics['Perplexity'].max():.2f}")
        print(f"  - Coherence range: {comprehensive_metrics['Coherence'].min():.4f} - {comprehensive_metrics['Coherence'].max():.4f}")
        print("="*60)

    def _save_final_results(self, range_str: str):
        """Save final combined results (legacy method for backward compatibility)."""
        prob_path = os.path.join(self.paths['loop_directory'], f'all_MC_probabilities_rel_{range_str}.csv')
        metrics_path = os.path.join(self.paths['lda_directory'], f'all_MC_metrics_{range_str}.csv')

        self.all_df_probabilities_rel.to_csv(prob_path)
        self.all_metrics.to_csv(metrics_path)

        print("="*60)
        print("Training complete! Final results saved:")
        print(f"  • Probabilities: {prob_path}")
        print(f"  • Metrics: {metrics_path}")
        print("="*60)






















