"""
Model selection and Sankey diagram data processing.

This module contains classes for:
- Processing LDA results into Sankey diagram data
- Integrating MALLET diagnostic data
- Model selection based on metrics
"""

import os
import pandas as pd
import numpy as np
import json
import glob
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import List, Dict, Optional

class SankeyDataProcessor:
    """
    A class for processing LDA results into Sankey diagram data.

    This class integrates with LDATrainer to automatically load and process:
    - Sample-MC probability data
    - MALLET diagnostic data
    - Perplexity metrics
    - Flow calculations between different K values
    """

    def __init__(self, base_directory: str, MC_range: List[int], 
                 high_threshold: float = 0.67, medium_threshold: float = 0.33,
                 range_str: Optional[str] = None):
        """
        Initialize the Sankey Data Processor.

        Args:
            base_directory: Base directory where LDATrainer saved results
            MC_range: List of K values (number of topics) to process
            high_threshold: Threshold for high representation (default 0.67)
            medium_threshold: Threshold for medium representation (default 0.33)
            range_str: String representation of range for file naming
        """
        self.base_directory = base_directory
        self.MC_range = MC_range
        self.high_threshold = high_threshold
        self.medium_threshold = medium_threshold

        if range_str is None:
            self.range_str = f"{min(MC_range)}-{max(MC_range)}"
        else:
            self.range_str = range_str

        # Set up paths automatically based on base_directory
        self._setup_paths()

        print(f"SankeyDataProcessor initialized:")
        print(f"  Base directory: {self.base_directory}")
        print(f"  K range: {self.MC_range}")
        print(f"  Thresholds: High={self.high_threshold}, Medium={self.medium_threshold}")

    def _setup_paths(self):
        """Set up all necessary paths based on base directory."""
        self.sample_mc_folder = os.path.join(self.base_directory, 'lda_results', 'MC_Sample')
        self.mc_feature_folder = os.path.join(self.base_directory, 'lda_results', 'MC_Feature')
        self.mallet_folder = os.path.join(self.base_directory, 'lda_results', 'Diagnostics')
        self.perplexity_path = os.path.join(
            self.base_directory, 'lda_results', f'all_MC_metrics_{self.range_str}.csv'
        )

        print(f"  Sample MC folder: {self.sample_mc_folder}")
        print(f"  MC feature folder: {self.mc_feature_folder}")
        print(f"  MALLET diagnostics: {self.mallet_folder}")
        print(f"  Perplexity file: {self.perplexity_path}")

    @classmethod
    def from_lda_trainer(cls, lda_trainer, high_threshold: float = 0.67, 
                        medium_threshold: float = 0.33):
        """
        Create SankeyDataProcessor from an LDATrainer instance.

        Args:
            lda_trainer: LDATrainer instance that has completed training
            high_threshold: Threshold for high representation
            medium_threshold: Threshold for medium representation

        Returns:
            SankeyDataProcessor instance
        """
        if not hasattr(lda_trainer, 'all_metrics') or lda_trainer.all_metrics.empty:
            raise ValueError("LDATrainer must have completed training before creating SankeyDataProcessor")

        # Get MC_range from the trainer's results
        MC_range = sorted(lda_trainer.all_metrics['Num_MCs'].unique().astype(int).tolist())

        return cls(
            base_directory=lda_trainer.base_directory,
            MC_range=MC_range,
            high_threshold=high_threshold,
            medium_threshold=medium_threshold
        )

    def load_sample_mc_data(self):
        """Load all sample-MC probability files"""
        sample_mc_data = {}

        for k in self.MC_range:
            filename = f'MC_Sample_probabilities{k}.csv'
            filepath = os.path.join(self.sample_mc_folder, filename)

            if os.path.exists(filepath):
                df = pd.read_csv(filepath, index_col=0)
                sample_mc_data[k] = df
                print(f"Loaded K={k}: {df.shape[0]} topics (MCs), {df.shape[1]} samples")

                if df.shape[0] != k:
                    print(f"WARNING: K={k} has {df.shape[0]} topics, expected {k}")
            else:
                print(f"File not found: {filename}")

        return sample_mc_data

    def categorize_sample_assignments(self, sample_mc_data):
        """Categorize samples into high/medium representation levels"""
        categorized_data = {}

        for k, df in sample_mc_data.items():
            k_data = {
                'nodes': {},
                'sample_assignments': {}
            }

            # Process each topic
            for topic_idx in range(df.shape[0]):
                topic_name = f"K{k}_MC{topic_idx}"
                topic_probs = df.iloc[topic_idx, :]

                high_samples = []
                medium_samples = []
                total_prob = 0

                for sample_name, prob in topic_probs.items():
                    if prob >= self.high_threshold:
                        high_samples.append((sample_name, prob))
                        total_prob += prob
                    elif prob >= self.medium_threshold:
                        medium_samples.append((sample_name, prob))
                        total_prob += prob

                k_data['nodes'][topic_name] = {
                    'high_samples': high_samples,
                    'medium_samples': medium_samples,
                    'high_count': len(high_samples),
                    'medium_count': len(medium_samples),
                    'total_probability': total_prob
                }

            # Find primary topic assignments
            for sample_idx, sample_name in enumerate(df.columns):
                sample_column = df.iloc[:, sample_idx]
                max_prob = 0
                assigned_topic = None
                assignment_level = None

                for topic_idx, prob in enumerate(sample_column):
                    if prob >= self.medium_threshold and prob > max_prob:
                        max_prob = prob
                        assigned_topic = f"K{k}_MC{topic_idx}"
                        assignment_level = 'high' if prob >= self.high_threshold else 'medium'

                if assigned_topic:
                    k_data['sample_assignments'][sample_name] = {
                        'assigned_topic': assigned_topic,
                        'probability': max_prob,
                        'level': assignment_level
                    }

            categorized_data[k] = k_data
            print(f"K={k}: {len(k_data['sample_assignments'])} samples assigned to topics")

        return categorized_data

    def calculate_flows(self, categorized_data):
        """Calculate flows between consecutive K values"""
        flows = []
        k_values = sorted(categorized_data.keys())

        for i in range(len(k_values) - 1):
            source_k = k_values[i]
            target_k = k_values[i + 1]

            source_assignments = categorized_data[source_k]['sample_assignments']
            target_assignments = categorized_data[target_k]['sample_assignments']

            flow_counts = defaultdict(lambda: defaultdict(int))
            flow_samples = defaultdict(lambda: defaultdict(list))

            common_samples = set(source_assignments.keys()) & set(target_assignments.keys())
            print(f"K{source_k}→K{target_k}: {len(common_samples)} samples to track")

            for sample in common_samples:
                source_info = source_assignments[sample]
                target_info = target_assignments[sample]

                source_segment = f"{source_info['assigned_topic']}_{source_info['level']}"
                target_segment = f"{target_info['assigned_topic']}_{target_info['level']}"

                flow_counts[source_segment][target_segment] += 1
                flow_samples[source_segment][target_segment].append({
                    'sample': sample,
                    'source_prob': source_info['probability'],
                    'target_prob': target_info['probability']
                })

            for source_segment, targets in flow_counts.items():
                for target_segment, count in targets.items():
                    if count > 0:
                        avg_prob = np.mean([
                            (s['source_prob'] + s['target_prob']) / 2 
                            for s in flow_samples[source_segment][target_segment]
                        ])

                        flows.append({
                            'source_k': source_k,
                            'target_k': target_k,
                            'source_segment': source_segment,
                            'target_segment': target_segment,
                            'sample_count': count,
                            'average_probability': avg_prob,
                            'samples': flow_samples[source_segment][target_segment]
                        })

        print(f"Total flows calculated: {len(flows)}")
        return flows

    def extract_topic_coherence(self, xml_file_path):
        """Extract topic coherence data from a single MALLET diagnostic XML file"""
        try:
            tree = ET.parse(xml_file_path)
            root = tree.getroot()
            topics_data = []

            for topic in root.findall('topic'):
                topic_id_raw = topic.get('id')
                try:
                    topic_data = {
                        'topic_id': int(topic.get('id')),
                        'tokens': float(topic.get('tokens')) if topic.get('tokens') else 0.0,
                        'document_entropy': float(topic.get('document_entropy')) if topic.get('document_entropy') else 0.0,
                        'word_length': float(topic.get('word-length')) if topic.get('word-length') else 0.0,
                        'coherence': float(topic.get('coherence')) if topic.get('coherence') else 0.0,
                        'uniform_dist': float(topic.get('uniform_dist')) if topic.get('uniform_dist') else 0.0,
                        'corpus_dist': float(topic.get('corpus_dist')) if topic.get('corpus_dist') else 0.0,
                        'eff_num_words': float(topic.get('eff_num_words')) if topic.get('eff_num_words') else 0.0,
                        'token_doc_diff': float(topic.get('token-doc-diff')) if topic.get('token-doc-diff') else 0.0,
                        'rank_1_docs': float(topic.get('rank_1_docs')) if topic.get('rank_1_docs') else 0.0,
                        'allocation_ratio': float(topic.get('allocation_ratio')) if topic.get('allocation_ratio') else 0.0,
                        'allocation_count': float(topic.get('allocation_count')) if topic.get('allocation_count') else 0.0,
                        'exclusivity': float(topic.get('exclusivity')) if topic.get('exclusivity') else 0.0
                    }
                    topics_data.append(topic_data)
                except (ValueError, TypeError) as e:
                    print(f"Warning: Could not parse topic {topic_id_raw}: {e}")
                    continue

            df = pd.DataFrame(topics_data)
            return df

        except ET.ParseError as e:
            print(f"❌ XML parsing error in {xml_file_path}: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"❌ Unexpected error processing {xml_file_path}: {e}")
            return pd.DataFrame()

    def load_all_mallet_diagnostics(self):
        """Load all MALLET diagnostic files"""
        pattern = os.path.join(self.mallet_folder, 'mallet.diagnostics.*.xml')
        xml_files = glob.glob(pattern)

        if not xml_files:
            print(f"❌ No MALLET diagnostic files found in {self.mallet_folder}")
            return pd.DataFrame()

        print(f"Found {len(xml_files)} MALLET diagnostic files")
        all_topics_data = []

        for xml_file in sorted(xml_files):
            filename = os.path.basename(xml_file)
            k_match = re.search(r'mallet\.diagnostics\.(\d+)\.xml', filename)

            if not k_match:
                print(f"⚠️ Warning: Could not extract K value from filename {filename}")
                continue

            k_value = int(k_match.group(1))
            topics_df = self.extract_topic_coherence(xml_file)

            if topics_df.empty:
                continue

            topics_df['k_value'] = k_value
            topics_df['global_topic_id'] = topics_df.apply(
                lambda row: f"K{k_value}_MC{int(row['topic_id'])}", axis=1
            )

            all_topics_data.append(topics_df)

        if not all_topics_data:
            print("❌ No valid MALLET data could be loaded")
            return pd.DataFrame()

        combined_df = pd.concat(all_topics_data, ignore_index=True)
        print(f"✅ Combined MALLET diagnostics: {len(combined_df)} topics")
        return combined_df

    def load_perplexity_data(self):
        """Load perplexity data from CSV file"""
        try:
            df = pd.read_csv(self.perplexity_path)
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

            if 'Num_MCs' not in df.columns or 'Perplexity' not in df.columns:
                print("❌ Required columns not found in perplexity CSV")
                return {}

            perplexity_dict = {}
            for _, row in df.iterrows():
                k_value = int(row['Num_MCs'])
                perplexity = float(row['Perplexity'])
                perplexity_dict[k_value] = perplexity

            print(f"✅ Loaded perplexity data for K values: {sorted(perplexity_dict.keys())}")
            return perplexity_dict

        except Exception as e:
            print(f"❌ Error loading perplexity data: {e}")
            return {}

    def save_processed_data(self, sankey_data, output_filename='sankey_data.json'):
        """Save processed data to JSON file"""
        if sankey_data is None:
            print("❌ No data to save")
            return

        def convert_numpy(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj

        def deep_convert(data):
            if isinstance(data, dict):
                return {k: deep_convert(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [deep_convert(item) for item in data]
            else:
                return convert_numpy(data)

        converted_data = deep_convert(sankey_data)

        # Save to the LDA results directory
        output_path = os.path.join(self.base_directory, 'lda_results', output_filename)

        with open(output_path, 'w') as f:
            json.dump(converted_data, f, indent=2)

        print(f"💾 Data saved to {output_path}")
        return output_path

    def process_all_data(self, output_filename='fully_integrated_sankey_data.json'):
        """
        🚀 SINGLE METHOD TO GET FULLY INTEGRATED DATA

        This method does everything in one call:
        1. Loads sample-MC data
        2. Categorizes assignments
        3. Calculates flows
        4. Integrates MALLET diagnostics
        5. Integrates perplexity data
        6. Saves the result

        Returns the fully integrated data ready for use.
        """
        print("🚀 Starting complete data processing pipeline...")
        print("=" * 60)

        # Step 1: Load and process base data
        print("1️⃣ Loading sample-MC data...")
        sample_mc_data = self.load_sample_mc_data()

        if not sample_mc_data:
            print("❌ No sample data loaded. Stopping process.")
            return None

        print("\n2️⃣ Categorizing sample assignments...")
        categorized_data = self.categorize_sample_assignments(sample_mc_data)

        print("\n3️⃣ Calculating flows...")
        flows = self.calculate_flows(categorized_data)

        # Step 2: Build base sankey structure
        print("\n4️⃣ Building base sankey structure...")
        sankey_data = {
            'nodes': {},
            'flows': flows,
            'k_range': list(sample_mc_data.keys()),
            'thresholds': {
                'high': self.high_threshold,
                'medium': self.medium_threshold
            },
            'metadata': {
                'total_samples': sample_mc_data[list(sample_mc_data.keys())[0]].shape[1] if sample_mc_data else 0,
                'k_values_processed': list(sample_mc_data.keys()),
                'processing_timestamp': pd.Timestamp.now().isoformat()
            }
        }

        # Collect all node data
        for k, k_data in categorized_data.items():
            for topic_name, node_data in k_data['nodes'].items():
                sankey_data['nodes'][topic_name] = node_data

        print(f"✅ Base structure created: {len(sankey_data['nodes'])} nodes, {len(flows)} flows")

        # Step 3: Integrate MALLET diagnostics
        print("\n5️⃣ Integrating MALLET diagnostics...")
        mallet_df = self.load_all_mallet_diagnostics()

        if not mallet_df.empty:
            mallet_dict = mallet_df.set_index('global_topic_id').to_dict('index')
            integrated_count = 0

            for topic_id, node_data in sankey_data['nodes'].items():
                if topic_id in mallet_dict:
                    mallet_data = mallet_dict[topic_id]
                    node_data['mallet_diagnostics'] = {
                        'coherence': mallet_data['coherence'],
                        'tokens': mallet_data['tokens'],
                        'document_entropy': mallet_data['document_entropy'],
                        'word_length': mallet_data['word_length'],
                        'uniform_dist': mallet_data['uniform_dist'],
                        'corpus_dist': mallet_data['corpus_dist'],
                        'eff_num_words': mallet_data['eff_num_words'],
                        'token_doc_diff': mallet_data['token_doc_diff'],
                        'rank_1_docs': mallet_data['rank_1_docs'],
                        'allocation_ratio': mallet_data['allocation_ratio'],
                        'allocation_count': mallet_data['allocation_count'],
                        'exclusivity': mallet_data['exclusivity']
                    }
                    integrated_count += 1

            sankey_data['metadata']['mallet_integration'] = {
                'integrated_topics': integrated_count,
                'total_mallet_topics': len(mallet_df)
            }
            print(f"✅ MALLET integration: {integrated_count} topics enriched")
        else:
            print("⚠️ No MALLET data available")

        # Step 4: Integrate perplexity data
        print("\n6️⃣ Integrating perplexity data...")
        perplexity_dict = self.load_perplexity_data()

        if perplexity_dict:
            integrated_count = 0

            for topic_id, node_data in sankey_data['nodes'].items():
                try:
                    k_part = topic_id.split('_')[0]
                    if k_part.startswith('K'):
                        k_value = int(k_part[1:])

                        if k_value in perplexity_dict:
                            if 'model_metrics' not in node_data:
                                node_data['model_metrics'] = {}

                            node_data['model_metrics']['perplexity'] = perplexity_dict[k_value]
                            node_data['model_metrics']['k_value'] = k_value
                            integrated_count += 1

                except (ValueError, IndexError):
                    continue

            sankey_data['metadata']['perplexity_integration'] = {
                'integrated_topics': integrated_count,
                'total_k_values_available': len(perplexity_dict)
            }
            print(f"✅ Perplexity integration: {integrated_count} topics enriched")
        else:
            print("⚠️ No perplexity data available")

        # Step 5: Save the final result
        print("\n7️⃣ Saving fully integrated data...")
        output_path = self.save_processed_data(sankey_data, output_filename)

        # Final summary
        print("\n" + "=" * 60)
        print("🎉 COMPLETE DATA PROCESSING FINISHED!")
        print(f"📊 Final Summary:")
        print(f"   - K values: {sankey_data['k_range']}")
        print(f"   - Total topics: {len(sankey_data['nodes'])}")
        print(f"   - Total flows: {len(sankey_data['flows'])}")
        print(f"   - Samples tracked: {sankey_data['metadata']['total_samples']}")

        if 'mallet_integration' in sankey_data['metadata']:
            print(f"   - MALLET enriched topics: {sankey_data['metadata']['mallet_integration']['integrated_topics']}")

        if 'perplexity_integration' in sankey_data['metadata']:
            print(f"   - Perplexity enriched topics: {sankey_data['metadata']['perplexity_integration']['integrated_topics']}")

        print(f"   - Data saved to: {output_path}")
        print("=" * 60)

        return sankey_data
