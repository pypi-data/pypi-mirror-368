from typing import List, Dict, Optional, Tuple, Any
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from scipy.cluster import hierarchy
from scipy.spatial import distance
import matplotlib.patches as mpatches


class MCComparison:
    """
    A class for comparing two microbial components (MCs) by analyzing samples with high representation. 
    Provides functionality to plot metadata and feature comparisons for selected MCs.
    
    Enhanced version with:
    - Automatic taxa mapping from random IDs to taxonomic names
    - Proper MC index naming conversion
    - Flexible taxonomic level selection
    - Better error handling and validation
    """
    
    def __init__(self, base_directory: str, metadata_path: str, taxonomic_level: str = 'genus_ID'):
        """
        Initialize the MCComparison class.
        
        Args:
            base_directory: Base directory containing LDA results and intermediate files
            metadata_path: Path to metadata CSV file
            taxonomic_level: Taxonomic level to use for feature mapping (default: 'genus_ID')
        """
        self.base_directory = base_directory
        self.metadata_path = metadata_path
        self.taxonomic_level = taxonomic_level
        
        # Load metadata
        self.metadata_df = pd.read_csv(metadata_path, index_col=0)
        
        # Load taxa mapping
        self.taxa_df = None
        self.random_asvid_mapping = None
        self._load_taxa_mapping()
        
        # Cache for processed data
        self._mc_feature_cache = {}
        self._mc_sample_cache = {}
        
        print(f"MCComparison initialized:")
        print(f"  Base directory: {self.base_directory}")
        print(f"  Taxonomic level: {self.taxonomic_level}")
        print(f"  Metadata shape: {self.metadata_df.shape}")
        print(f"  Taxa mapping: {len(self.random_asvid_mapping) if self.random_asvid_mapping else 0} ASVs")

    def _load_taxa_mapping(self):
        """Load taxa mapping from intermediate_taxa.csv and create random ID mapping."""
        taxa_path = os.path.join(self.base_directory, 'intermediate', 'intermediate_taxa.csv')
        
        try:
            self.taxa_df = pd.read_csv(taxa_path, index_col=0)
            print(f"✓ Loaded taxa data: {self.taxa_df.shape}")
            
            # Validate taxonomic level
            if self.taxonomic_level not in self.taxa_df.columns:
                available_levels = [col for col in self.taxa_df.columns if col != 'randomID']
                raise ValueError(f"Taxonomic level '{self.taxonomic_level}' not found. Available: {available_levels}")
            
            # Create mapping from randomID to taxonomic level
            self.random_asvid_mapping = dict(zip(self.taxa_df['randomID'], self.taxa_df[self.taxonomic_level]))
            print(f"✓ Created mapping for {len(self.random_asvid_mapping)} ASVs to {self.taxonomic_level}")
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Taxa mapping file not found: {taxa_path}")
        except Exception as e:
            raise Exception(f"Error loading taxa mapping: {e}")

    def _convert_mc_index(self, mc_asv_df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert MC index from raw format to proper K{value}_MC{number} format.
        
        Args:
            mc_asv_df: DataFrame with raw MC indices
            
        Returns:
            DataFrame with converted indices
        """
        old_index = mc_asv_df.index.values.tolist()
        
        # Convert index format: from raw to K{value}_MC{number}
        new_names = []
        for item in old_index:
            try:
                parts = item.split('_')
                k_value = int(parts[0]) - 1  # Adjust K value
                mc_number = int(parts[1]) - 1  # Adjust MC number
                new_name = f"K{k_value}_MC{mc_number}"
                new_names.append(new_name)
            except (ValueError, IndexError) as e:
                print(f"Warning: Could not parse index '{item}': {e}")
                new_names.append(item)  # Keep original if parsing fails
        
        mc_asv_df_converted = mc_asv_df.copy()
        mc_asv_df_converted.index = new_names
        
        print(f"✓ Converted {len(new_names)} MC indices")
        return mc_asv_df_converted

    def _apply_taxa_mapping(self, mc_asv_df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply taxa mapping to convert random IDs to taxonomic names.
        
        Args:
            mc_asv_df: DataFrame with random ID columns
            
        Returns:
            DataFrame with taxonomic names as columns
        """
        mc_asv_mapped = mc_asv_df.copy()
        
        # Map column names from random IDs to taxonomic names
        original_columns = mc_asv_mapped.columns.tolist()
        mc_asv_mapped.columns = mc_asv_mapped.columns.map(self.random_asvid_mapping)
        
        # Count successful mappings
        mapped_count = sum(1 for orig_col in original_columns if orig_col in self.random_asvid_mapping)
        
        print(f"✓ Mapped {mapped_count}/{len(original_columns)} columns to {self.taxonomic_level}")
        
        # Group by taxonomic level and sum (in case of duplicates)
        mc_asv_grouped = mc_asv_mapped.groupby(level=0, axis=1).sum()
        
        if mc_asv_grouped.shape[1] != mc_asv_mapped.shape[1]:
            print(f"✓ Grouped {mc_asv_mapped.shape[1]} → {mc_asv_grouped.shape[1]} unique {self.taxonomic_level} features")
        
        return mc_asv_grouped

    def _load_and_process_mc_feature_data(self, k_value: str) -> pd.DataFrame:
        """
        Load and process MC-feature probability data with proper mapping.
        
        Args:
            k_value: K value as string (e.g., '5')
            
        Returns:
            Processed DataFrame with proper indices and taxonomic columns
        """
        if k_value in self._mc_feature_cache:
            return self._mc_feature_cache[k_value]
        
        # Load raw MC-feature probabilities
        filepath = os.path.join(self.base_directory, 'lda_results', 'MC_Feature', 
                               f'MC_Feature_Probabilities_{k_value}.csv')
        
        try:
            mc_feature_df = pd.read_csv(filepath, index_col=0)
            print(f"✓ Loaded MC-feature data: {mc_feature_df.shape}")
            
            # Apply taxa mapping to columns
            mc_feature_mapped = self._apply_taxa_mapping(mc_feature_df)
            
            # Convert index format
            mc_feature_final = self._convert_mc_index(mc_feature_mapped)
            
            # Cache the result
            self._mc_feature_cache[k_value] = mc_feature_final
            
            return mc_feature_final
            
        except FileNotFoundError:
            raise FileNotFoundError(f"MC-feature file not found: {filepath}")

    def _load_and_process_mc_sample_data(self, k_value: str) -> pd.DataFrame:
        """
        Load and process MC-sample probability data with proper mapping.
        
        Args:
            k_value: K value as string (e.g., '5')
            
        Returns:
            Processed DataFrame with proper indices
        """
        if k_value in self._mc_sample_cache:
            return self._mc_sample_cache[k_value]
        
        # Load raw MC-sample probabilities
        filepath = os.path.join(self.base_directory, 'lda_results', 'MC_Sample', 
                               f'MC_Sample_probabilities{k_value}.csv')
        
        try:
            mc_sample_df = pd.read_csv(filepath, index_col=0)
            print(f"✓ Loaded MC-sample data: {mc_sample_df.shape}")
            
            # Convert index format
            mc_sample_final = self._convert_mc_index(mc_sample_df)
            
            # Cache the result
            self._mc_sample_cache[k_value] = mc_sample_final
            
            return mc_sample_final
            
        except FileNotFoundError:
            raise FileNotFoundError(f"MC-sample file not found: {filepath}")

    def get_high_representation_samples(self, topic_id: str, high_threshold: float = 0.67) -> List[str]:
        """
        Retrieve samples with high representation for a specific topic.

        Args:
            topic_id: Topic ID in format 'K5_MC1'
            high_threshold: Probability threshold for high representation

        Returns:
            List of sample IDs with high representation
        """
        k_value = topic_id.split('_')[0][1:]  # Extract K value
        
        # Load processed data
        sample_mc_df = self._load_and_process_mc_sample_data(k_value)
        
        # Validate topic ID exists
        if topic_id not in sample_mc_df.index:
            available_topics = sample_mc_df.index.tolist()
            raise ValueError(f"Topic ID '{topic_id}' not found. Available: {available_topics}")
        
        # Get samples with high representation
        mc_samples = sample_mc_df.loc[topic_id]
        high_samples = mc_samples[mc_samples > high_threshold].index.tolist()
        
        print(f"✓ Found {len(high_samples)} samples with >{high_threshold:.0%} representation in {topic_id}")
        
        return high_samples

    def get_feature_probabilities(self, mc_id: str) -> pd.Series:
        """
        Retrieve feature probabilities for a given MC with proper taxonomic mapping.

        Args:
            mc_id: MC ID, e.g., 'K5_MC1'

        Returns:
            A Series with feature probabilities using taxonomic names
        """
        k_value = mc_id.split('_')[0][1:]  # Extract the K value
        
        # Load processed data
        mc_feature_df = self._load_and_process_mc_feature_data(k_value)
        
        # Validate MC ID exists
        if mc_id not in mc_feature_df.index:
            available_mcs = mc_feature_df.index.tolist()
            raise ValueError(f"MC ID '{mc_id}' not found. Available: {available_mcs}")
        
        feature_probs = mc_feature_df.loc[mc_id]
        
        print(f"✓ Retrieved feature probabilities for {mc_id} ({len(feature_probs)} {self.taxonomic_level} features)")
        
        return feature_probs

    def compare_metadata(self, samples1: List[str], samples2: List[str], features: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Compare metadata between two sample groups.

        Args:
            samples1: List of sample IDs for MC1
            samples2: List of sample IDs for MC2
            features: List of metadata features to compare
            
        Returns:
            Two DataFrames containing metadata for each group
        """
        # Validate features exist
        available_features = [f for f in features if f in self.metadata_df.columns]
        missing_features = [f for f in features if f not in self.metadata_df.columns]
        
        if missing_features:
            print(f"Warning: Features not found in metadata: {missing_features}")
            print(f"Available features: {list(self.metadata_df.columns)}")
        
        if not available_features:
            raise ValueError("No valid features found in metadata")
        
        # Get metadata for both groups, handling missing samples
        valid_samples1 = [s for s in samples1 if s in self.metadata_df.index]
        valid_samples2 = [s for s in samples2 if s in self.metadata_df.index]
        
        if len(valid_samples1) != len(samples1):
            print(f"Warning: {len(samples1) - len(valid_samples1)} samples from group 1 not found in metadata")
        
        if len(valid_samples2) != len(samples2):
            print(f"Warning: {len(samples2) - len(valid_samples2)} samples from group 2 not found in metadata")
        
        group1_metadata = self.metadata_df.loc[valid_samples1, available_features]
        group2_metadata = self.metadata_df.loc[valid_samples2, available_features]
        
        return group1_metadata, group2_metadata

    def plot_metadata_comparison(self, df1: pd.DataFrame, df2: pd.DataFrame, feature: str, 
                               mc1_name: str = "MC1", mc2_name: str = "MC2"):
        """
        Plot a comparison bar chart for a specific metadata feature.

        Args:
            df1: DataFrame for MC1
            df2: DataFrame for MC2
            feature: The metadata feature to compare
            mc1_name: Name for MC1 in the plot
            mc2_name: Name for MC2 in the plot
        """
        if feature not in df1.columns or feature not in df2.columns:
            print(f"Warning: Feature '{feature}' not found in one or both datasets")
            return
        
        # Calculate proportions
        mc1_counts = df1[feature].value_counts(normalize=True)
        mc2_counts = df2[feature].value_counts(normalize=True)
        
        # Combine data
        combined_df = pd.concat([mc1_counts, mc2_counts], axis=1, sort=False)
        combined_df.columns = [mc1_name, mc2_name]
        combined_df = combined_df.fillna(0)  # Fill missing values with 0
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        combined_df.plot(kind='bar', ax=ax, color=['skyblue', 'lightcoral'])
        
        plt.title(f"Comparison of {feature}\n({mc1_name}: n={len(df1)}, {mc2_name}: n={len(df2)})")
        plt.ylabel('Proportion')
        plt.xlabel(feature)
        plt.xticks(rotation=45, ha='right')
        plt.legend(title='Microbial Component')
        plt.tight_layout()
        plt.show()

    def plot_top_features_heatmap(self, mc1_probs: pd.Series, mc2_probs: pd.Series, 
                                top_n: int = 10, mc1_name: str = "MC1", mc2_name: str = "MC2"):
        """
        Plot heatmap comparing top features from two MCs by probabilities

        Args:
            mc1_probs: Series containing MC1 feature probabilities
            mc2_probs: Series containing MC2 feature probabilities
            top_n: Number of top features to display
            mc1_name: Name for MC1 in the plot
            mc2_name: Name for MC2 in the plot
        """
        # Get top features from both MCs
        all_top_features = pd.concat([mc1_probs.nlargest(top_n), mc2_probs.nlargest(top_n)])
        
        # Sort by mean probability across both MCs
        sorted_features = all_top_features.groupby(all_top_features.index).mean().sort_values(ascending=False)
        top_features = sorted_features.head(top_n * 2).index
        
        # Create heatmap data
        heatmap_data = pd.DataFrame({
            mc1_name: mc1_probs.reindex(top_features, fill_value=0),
            mc2_name: mc2_probs.reindex(top_features, fill_value=0)
        })
        
        # Create plot
        plt.figure(figsize=(8, max(6, len(top_features) * 0.4)))
        
        sns.heatmap(
            heatmap_data, 
            annot=True, 
            cmap='Blues', 
            cbar_kws={'label': f'Probability ({self.taxonomic_level})'},
            fmt='.3f',
            linewidths=0.5
        )
        
        plt.title(f"Top {self.taxonomic_level} Features Comparison\n{mc1_name} vs {mc2_name}")
        plt.xlabel("Microbial Components")
        plt.ylabel(f"{self.taxonomic_level} Features")
        plt.tight_layout()
        plt.show()

    def get_feature_summary(self, mc_id: str, top_n: int = 10) -> Dict[str, Any]:
        """
        Get a summary of top features for a specific MC.
        
        Args:
            mc_id: MC ID (e.g., 'K5_MC1')
            top_n: Number of top features to include
            
        Returns:
            Dictionary with feature summary
        """
        feature_probs = self.get_feature_probabilities(mc_id)
        top_features = feature_probs.nlargest(top_n)
        
        summary = {
            'mc_id': mc_id,
            'taxonomic_level': self.taxonomic_level,
            'total_features': len(feature_probs),
            'top_features': top_features.to_dict(),
            'max_probability': feature_probs.max(),
            'total_probability_mass': feature_probs.sum(),
            'non_zero_features': (feature_probs > 0).sum(),
            'entropy': -np.sum(feature_probs * np.log2(feature_probs + 1e-10))  # Shannon entropy
        }
        
        return summary

    def compare_two_mcs(self, mc1_id: str, mc2_id: str, features: Optional[List[str]] = None, 
                       high_threshold: float = 0.67, top_n: int = 15):
        """
        Compare two MCs by their metadata and top features.

        Args:
            mc1_id: ID of the first MC
            mc2_id: ID of the second MC
            features: List of metadata features to compare (if None, uses default)
            high_threshold: Threshold for high representation samples
            top_n: Number of top features to display in heatmap
        """
        print(f"COMPARING {mc1_id} vs {mc2_id}")
        print("=" * 50)
        
        # Default features if not provided
        if features is None:
            features = ['Diagnosis', 'SampleTime', 'Location']  # Adjust based on your metadata
            # Filter to available features
            features = [f for f in features if f in self.metadata_df.columns]
            if not features:
                print("Warning: No default features found in metadata. Skipping metadata comparison.")
        
        # Get high representation samples
        print(f"1. Finding high representation samples (threshold: {high_threshold:.0%})")
        samples1 = self.get_high_representation_samples(mc1_id, high_threshold)
        samples2 = self.get_high_representation_samples(mc2_id, high_threshold)
        
        print(f"   {mc1_id}: {len(samples1)} samples")
        print(f"   {mc2_id}: {len(samples2)} samples")
        print(f"   Overlap: {len(set(samples1) & set(samples2))} samples")
        
        # Compare metadata if samples and features are available
        if features and samples1 and samples2:
            print(f"\n2. Comparing metadata features: {features}")
            group1_metadata, group2_metadata = self.compare_metadata(samples1, samples2, features)
            
            # Plot metadata comparison
            for feature in features:
                if feature in group1_metadata.columns and feature in group2_metadata.columns:
                    self.plot_metadata_comparison(group1_metadata, group2_metadata, feature, mc1_id, mc2_id)
        
        # Compare feature probabilities
        print(f"\n3. Comparing {self.taxonomic_level} feature probabilities")
        mc1_probs = self.get_feature_probabilities(mc1_id)
        mc2_probs = self.get_feature_probabilities(mc2_id)
        
        # Display top features
        print(f"\n   Top 5 {self.taxonomic_level} features:")
        print(f"   {mc1_id}:")
        for feature, prob in mc1_probs.nlargest(5).items():
            print(f"     {feature}: {prob:.4f}")
        
        print(f"   {mc2_id}:")
        for feature, prob in mc2_probs.nlargest(5).items():
            print(f"     {feature}: {prob:.4f}")
        
        # Plot top features heatmap
        print(f"\n4. Creating feature comparison heatmap (top {top_n})")
        self.plot_top_features_heatmap(mc1_probs, mc2_probs, top_n, mc1_id, mc2_id)
        
        # Find distinctive features
        print(f"\n5. Identifying distinctive features")
        threshold = 0.01  # Minimum probability to consider
        
        mc1_significant = mc1_probs[mc1_probs > threshold]
        mc2_significant = mc2_probs[mc2_probs > threshold]
        
        # Features high in MC1 but low in MC2
        mc1_distinctive = mc1_significant[mc1_significant.index.isin(mc2_probs[mc2_probs < threshold/2].index)]
        
        # Features high in MC2 but low in MC1  
        mc2_distinctive = mc2_significant[mc2_significant.index.isin(mc1_probs[mc1_probs < threshold/2].index)]
        
        if len(mc1_distinctive) > 0:
            print(f"   {mc1_id} distinctive features ({len(mc1_distinctive)}):")
            for feature, prob in mc1_distinctive.nlargest(3).items():
                print(f"     {feature}: {prob:.4f}")
        
        if len(mc2_distinctive) > 0:
            print(f"   {mc2_id} distinctive features ({len(mc2_distinctive)}):")
            for feature, prob in mc2_distinctive.nlargest(3).items():
                print(f"     {feature}: {prob:.4f}")
        
        print(f"\n✓ Comparison completed!")
        
        return {
            'mc1_samples': len(samples1),
            'mc2_samples': len(samples2),
            'mc1_distinctive': mc1_distinctive.to_dict() if len(mc1_distinctive) > 0 else {},
            'mc2_distinctive': mc2_distinctive.to_dict() if len(mc2_distinctive) > 0 else {}
        }

    def get_available_topics(self, k_value: str) -> List[str]:
        """
        Get list of available topics for a given K value.
        
        Args:
            k_value: K value as string (e.g., '5')
            
        Returns:
            List of available topic IDs
        """
        mc_sample_df = self._load_and_process_mc_sample_data(k_value)
        return mc_sample_df.index.tolist()

    def set_taxonomic_level(self, new_level: str):
        """
        Change the taxonomic level and clear cache.
        
        Args:
            new_level: New taxonomic level to use
        """
        if new_level not in self.taxa_df.columns:
            available_levels = [col for col in self.taxa_df.columns if col != 'randomID']
            raise ValueError(f"Taxonomic level '{new_level}' not found. Available: {available_levels}")
        
        self.taxonomic_level = new_level
        self.random_asvid_mapping = dict(zip(self.taxa_df['randomID'], self.taxa_df[new_level]))
        
        # Clear cache to force reprocessing with new taxonomic level
        self._mc_feature_cache.clear()
        
        print(f"✓ Taxonomic level changed to: {new_level}")
        print(f"✓ Cache cleared - next operations will use {new_level} level")


"""
Visualization tools for LDA results.

This module contains classes for:
- Creating clustered heatmaps with metadata annotations
- Topic-taxon distribution visualizations
- Customizable color schemes and layouts
"""


from typing import List, Dict, Optional, Tuple, Any, Callable
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from scipy.cluster import hierarchy
from scipy.spatial import distance
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors


class LDAModelVisualizer:
    """
    A class for visualizing LDA model results with customizable metadata and color schemes.

    This class handles:
    - Loading model results for a specific K value
    - Creating clustered heatmaps with metadata annotations
    - Topic-taxon distribution visualizations
    - Customizable color schemes for categorical and continuous variables
    """

    def __init__(self, base_directory: str, k_value: int, metadata_path: str,
                 universal_headers: List[str], continuous_headers: List[str] = None,
                 top_asv_count: int = 7, id_column: str = 'ID'):
        """
        Initialize the LDA Model Visualizer.

        Args:
            base_directory: Base directory where LDA results are stored
            k_value: Number of topics (K) to visualize
            metadata_path: Path to metadata CSV file
            universal_headers: List of categorical metadata columns to include (required)
            continuous_headers: List of continuous metadata columns to include (optional)
            top_asv_count: Number of top ASVs to show in heatmaps (default: 7)
            id_column: Column name to use for sample IDs (default: 'ID')
        """
        self.base_directory = base_directory
        self.k_value = k_value
        self.metadata_path = metadata_path

        # Set up paths
        self._setup_paths()

        # Initialize configuration
        self.config = {
            'universal_headers': universal_headers,
            'continuous_headers': continuous_headers or [],
            'top_asv_count': top_asv_count,
            'id_column': id_column,
            'custom_colors': {},  # Will be set with defaults or user values
            'continuous_cmaps': {},  # Will be set with defaults or user values
            'figsize': (14, 10),
            'heatmap_vmin': 0,
            'heatmap_vmax': 0.4,
            'cbar_ticks': [0, 0.02, 0.05, 0.1, 0.3]
        }

        # Set default colors
        self._set_default_colors()

        # Load data
        self._load_data()

        print(f"LDAModelVisualizer initialized for K={k_value}")
        print(f"  Base directory: {self.base_directory}")
        print(f"  Visualization directory: {self.viz_directory}")
        print(f"  Universal headers: {universal_headers}")
        print(f"  Continuous headers: {continuous_headers or 'None'}")


    def _setup_paths(self):
        """Set up all necessary paths."""
        self.loop_directory = os.path.join(self.base_directory, 'lda_loop')
        self.inter_directory = os.path.join(self.base_directory, 'intermediate')
        self.viz_directory = os.path.join(self.base_directory, 'lda_visualization')
        self.lda_directory = os.path.join(self.base_directory, 'lda_results')
        self.MC_sample_directory = os.path.join(self.lda_directory, 'MC_Sample')
        self.MC_feature_directory = os.path.join(self.lda_directory, 'MC_Feature')

        # Create visualization directory
        os.makedirs(self.viz_directory, exist_ok=True)

        # Set up file paths for this specific K value
        self.path_to_DirichletComponentProbabilities = os.path.join(
            self.MC_sample_directory, 
            f"MC_Sample_probabilities{self.k_value}.csv"
        )
        self.path_to_ASVProbabilities = os.path.join(
            self.MC_feature_directory, 
            f"MC_Feature_Probabilities_{self.k_value}.csv"
        )
        self.path_to_new_taxa = os.path.join(
            self.inter_directory, 
            "intermediate_taxa.csv"
        )

    def _set_default_colors(self):
        """Set up empty color configurations - will use seaborn/matplotlib defaults."""
        # Initialize empty - will use library defaults when colors are generated
        self.config['custom_colors'] = {}
        self.config['continuous_cmaps'] = {}

        print("✓ Color configuration initialized - will use library defaults")

    def _load_data(self):
        """Load all necessary data files."""
        try:
            # Load Dirichlet Component Probabilities (sample-topic distributions)
            DMP = pd.read_csv(self.path_to_DirichletComponentProbabilities, index_col=0).T
            self.DM_distributions = DMP.values.tolist()
            print(f"✓ Loaded sample-topic distributions: {DMP.shape}")

            # Load ASV probabilities (topic-feature distributions)
            self.ASV_probabilities = pd.read_csv(self.path_to_ASVProbabilities, index_col=0)
            print(f"✓ Loaded topic-ASV distributions: {self.ASV_probabilities.shape}")

            # Load metadata
            self.metadata = pd.read_csv(self.metadata_path, index_col=0)
            print(f"✓ Loaded metadata: {self.metadata.shape}")

            # Load taxonomy data if available
            if os.path.exists(self.path_to_new_taxa):
                self.taxa_data = pd.read_csv(self.path_to_new_taxa, index_col=0)
                print(f"✓ Loaded taxonomy data: {self.taxa_data.shape}")
            else:
                self.taxa_data = None
                print("! Taxonomy data not found")

        except Exception as e:
            raise FileNotFoundError(f"Error loading data: {e}")

    def configure_colors(self, 
                       custom_colors: Optional[Dict] = None,
                       continuous_cmaps: Optional[Dict] = None,
                       **kwargs):
        """
        Configure color schemes for visualization.

        Args:
            custom_colors: Dictionary of custom colors for categorical variables
            continuous_cmaps: Dictionary of colormaps for continuous variables
            **kwargs: Additional configuration parameters (figsize, heatmap_vmin, etc.)
        """
        if custom_colors is not None:
            self.config['custom_colors'].update(custom_colors)
        if continuous_cmaps is not None:
            self.config['continuous_cmaps'].update(continuous_cmaps)

        # Update any additional parameters
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value

        print("✓ Color configuration updated")

    def rgb_to_hex(self, r: int, g: int, b: int) -> str:
        """Convert RGB values to hex code."""
        return '#{:02x}{:02x}{:02x}'.format(r, g, b)

    def prepare_heatmap_data(self, headers_to_include: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Create a multi-index heatmap table from distributions and metadata.

        Args:
            headers_to_include: List of column names to include in the multi-index header

        Returns:
            DataFrame with multi-index columns
        """
        # Use configured headers if none provided
        if headers_to_include is None:
            headers_to_include = self.config['universal_headers'] + self.config['continuous_headers']

        # Convert nested list to DataFrame and transpose
        distributions_df = pd.DataFrame(self.DM_distributions)
        multiheader = distributions_df.T

        # Fill NaN values in metadata with 0
        metadata_df_filled = self.metadata.fillna(0)

        # Get unique IDs from the metadata that match our samples
        sample_ids = metadata_df_filled[self.config['id_column']].values[:len(self.DM_distributions)]

        # Create a list of tuples for the multi-index
        header_tuples = []
        for idx, id_val in enumerate(sample_ids):
            # Get the matching metadata row
            metadata_row = metadata_df_filled[metadata_df_filled[self.config['id_column']] == id_val]

            if not metadata_row.empty:
                # Extract values for each header
                tuple_values = [metadata_row[col].values[0] for col in headers_to_include]
                # Add the ID as the last element
                tuple_values.append(id_val)
                header_tuples.append(tuple(tuple_values))

        # Create column names for the multi-index (headers_to_include + id_column)
        multi_columns = headers_to_include + [self.config['id_column']]

        # Create a DataFrame for the multi-index
        header_df = pd.DataFrame(header_tuples, columns=multi_columns)

        # Create the MultiIndex
        multi_index = pd.MultiIndex.from_frame(header_df)

        # Set the multi-index on the columns
        multiheader.columns = multi_index

        return multiheader

    def create_clustered_heatmap(self, multiheader: pd.DataFrame, 
                               custom_filename: Optional[str] = None,
                               show_dendrograms: bool = False,
                               figsize: Optional[Tuple[int, int]] = None) -> Tuple[Any, Any]:
        """
        Create a clustermap with color annotations for specified headers.

        Args:
            multiheader: DataFrame with multi-index columns to visualize
            custom_filename: Custom filename for output (without extension)
            show_dendrograms: Whether to show dendrograms
            figsize: Figure size tuple

        Returns:
            Tuple of (ClusterGrid object, Legend figure object)
        """
        if figsize is None:
            figsize = (8.27, 11.69)  # A4 size

        # Get headers to color
        headers_to_color = self.config['universal_headers'] + self.config['continuous_headers']

        # Set up file paths
        if custom_filename is None:
            base_filename = f"clustered_heatmap_K{self.k_value}"
        else:
            base_filename = custom_filename

        output_path = os.path.join(self.viz_directory, f"{base_filename}.png")
        legend_path = os.path.join(self.viz_directory, f"{base_filename}_legend.png")

        # Create the clustered heatmap using the integrated function
        g, legend_fig = self._create_clustered_heatmap_internal(
            multiheader=multiheader,
            id_column=self.config['id_column'],
            headers_to_color=headers_to_color,
            custom_colors=self.config['custom_colors'],
            continuous_headers=self.config['continuous_headers'],
            figsize=figsize,
            output_path=output_path,
            legend_path=legend_path,
            show_dendrograms=show_dendrograms,
            continuous_cmaps=self.config['continuous_cmaps']
        )

        print(f"✓ Clustered heatmap saved: {output_path}")
        if legend_fig is not None:
            print(f"✓ Legend saved: {legend_path}")

        return g, legend_fig

    def _create_clustered_heatmap_internal(self, multiheader, id_column=None, headers_to_color=None, 
                                         custom_colors=None, continuous_headers=None, figsize=(8.27, 11.69), 
                                         output_path=None, legend_path=None, show_dendrograms=False, 
                                         continuous_cmaps=None, continuous_colors=None):
        """Internal method for creating clustered heatmap - integrates your original function."""
        # Set default values if not provided
        if id_column is None:
            id_column = multiheader.columns.names[-1]

        if headers_to_color is None:
            headers_to_color = [name for name in multiheader.columns.names if name != id_column]

        if continuous_headers is None:
            continuous_headers = []

        if continuous_cmaps is None:
            continuous_cmaps = {}

        if continuous_colors is None:
            continuous_colors = {}

        # Get unique values for each header and create color palettes
        color_maps = {}
        colors_dict = {}

        # Define gray color for missing values
        missing_color = '#D3D3D3'  # Light gray

        # Create a unique palette for each header
        for header in headers_to_color:
            # Get unique values
            header_values = multiheader.columns.get_level_values(header)

            # Check if this header should use a continuous color scale
            if header in continuous_headers:
                # Filter out non-numeric, zero, and missing values for finding min/max
                numeric_values = pd.to_numeric(header_values, errors='coerce')
                valid_mask = ~np.isnan(numeric_values) & (numeric_values != 0)

                if not any(valid_mask):
                    # If no valid numeric values, fall back to categorical
                    print(f"Warning: Header '{header}' specified as continuous but contains no valid numeric values. Using categorical colors.")
                    is_continuous = False
                else:
                    is_continuous = True
                    # Get min and max for normalization
                    vmin = np.min(numeric_values[valid_mask])
                    vmax = np.max(numeric_values[valid_mask])

                    # Create a normalization function
                    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

                    # Determine which colormap to use for this header
                    if header in continuous_colors:
                        # User provided custom colors to create a colormap
                        color_pair = continuous_colors[header]
                        cmap_name = f"custom_{header.replace(' ', '_')}"

                        # Create a custom colormap from the provided colors
                        if isinstance(color_pair, (list, tuple)) and len(color_pair) >= 2:
                            cmap = LinearSegmentedColormap.from_list(cmap_name, color_pair)
                        else:
                            print(f"Warning: Invalid color pair for '{header}'. Expected [color1, color2]. Using default colormap.")
                            cmap = plt.cm.viridis

                    elif header in continuous_cmaps:
                        # User specified a specific colormap
                        cmap_name = continuous_cmaps[header]
                        if isinstance(cmap_name, str):
                            try:
                                # Try to get a matplotlib colormap
                                cmap = plt.get_cmap(cmap_name)
                            except:
                                print(f"Warning: Colormap '{cmap_name}' not found. Using default.")
                                cmap = plt.cm.viridis
                        else:
                            # Assume it's already a colormap object
                            cmap = cmap_name
                    else:
                        # Use default colormap
                        cmap = plt.cm.viridis

                    # Store info for legend creation
                    color_maps[header] = {
                        'type': 'continuous',
                        'cmap': cmap,
                        'norm': norm,
                        'vmin': vmin,
                        'vmax': vmax
                    }

                    # Map values to colors
                    colors = []
                    for val in header_values:
                        try:
                            num_val = float(val)
                            if np.isnan(num_val) or num_val == 0:  # Treat zero as missing value
                                colors.append(missing_color)
                            else:
                                colors.append(cmap(norm(num_val)))
                        except (ValueError, TypeError):
                            colors.append(missing_color)

                    colors_dict[header] = pd.Series(colors, index=multiheader.columns)
                    continue  # Skip the categorical color assignment
            else:
                is_continuous = False

            # Categorical coloring (for non-continuous headers)
            if not is_continuous:
                # Filter out None, NaN, and empty string values for color assignment
                unique_values = header_values.unique()
                valid_values = [v for v in unique_values if pd.notna(v) and v != '']

                if pd.api.types.is_numeric_dtype(np.array(valid_values, dtype=object)):
                    valid_values = sorted(valid_values)

                # Use custom colors if provided, otherwise generate a palette
                if custom_colors and header in custom_colors:
                    # Use custom color dictionary for this header
                    lut = custom_colors[header].copy()  # Make a copy to avoid modifying the original
                else:
                    # Generate default palette
                    palette = sns.color_palette("deep", len(valid_values))
                    lut = dict(zip(valid_values, palette))

                # Add a color for missing values (None, NaN, or empty string)
                lut[None] = missing_color
                lut[np.nan] = missing_color
                lut[''] = missing_color

                # Store the color lookup table
                color_maps[header] = {
                    'type': 'categorical',
                    'lut': lut
                }

                # Map colors to columns, handling missing values
                colors = []
                for val in header_values:
                    if pd.isna(val) or val == '':
                        colors.append(missing_color)
                    elif val in lut:
                        colors.append(lut[val])
                    else:
                        colors.append(missing_color)  # If value not in lut for some reason

                colors_dict[header] = pd.Series(colors, index=multiheader.columns)

        # Create a DataFrame of colors
        multi_colors = pd.DataFrame(colors_dict)

        # Create the clustermap
        g = sns.clustermap(
            multiheader, 
            center=0, 
            cmap="vlag",
            col_colors=multi_colors,
            dendrogram_ratio=(.1, .2),
            cbar_pos=(-.08, .50, .03, .2),
            linewidths=.15, 
            figsize=figsize,
            col_cluster=True, 
            row_cluster=True
        )

        # Get the specified ID column values for x-tick labels
        g.ax_heatmap.set_xticks([])
        g.ax_heatmap.set_xticklabels([])
        g.ax_heatmap.tick_params(axis='x', bottom=False)

        # Show/hide dendrograms based on parameter
        g.ax_row_dendrogram.set_visible(show_dendrograms)
        g.ax_col_dendrogram.set_visible(show_dendrograms)

        # Save the figure if path is provided
        if output_path:
            g.savefig(output_path, dpi=300, format='png')
            svg_path = output_path.replace('.png', '.svg')
            g.savefig(svg_path, format='svg')

        # Create separate legend file if path is provided
        legend_fig = None
        if legend_path:
            legend_fig = self._create_legend_file(
                color_maps=color_maps,
                headers_to_color=headers_to_color,
                continuous_headers=continuous_headers,
                missing_color=missing_color,
                output_path=legend_path
            )

        return g, legend_fig

    def _create_legend_file(self, color_maps, headers_to_color, continuous_headers, missing_color, output_path=None):
        """Create a separate legend file with vertical organization."""
        from matplotlib.cm import ScalarMappable

        # Create figure for the legends
        fig_height = 1 + 0.8 * len(headers_to_color)  # Dynamic height based on number of headers
        fig, ax = plt.subplots(figsize=(5, fig_height))
        ax.axis('off')  # Hide the axes

        # Configure background
        fig.patch.set_facecolor('white')

        # Vertical spacing parameters
        y_start = 0.95
        y_step = 0.9 / len(headers_to_color)

        legends = []

        # Track headers we've already seen to handle duplicates
        seen_headers = {}

        # Create legends in vertical stack
        for i, header in enumerate(headers_to_color):
            # Handle duplicate header names by creating unique titles
            if header in seen_headers:
                seen_headers[header] += 1
                display_title = f"{header} ({seen_headers[header]})"
            else:
                seen_headers[header] = 1
                display_title = header

            # Calculate y position
            y_pos = y_start - i * y_step

            # Check if this is a continuous or categorical header
            if header in continuous_headers and color_maps[header]['type'] == 'continuous':
                # Get colormap info
                cmap_info = color_maps[header]
                cmap = cmap_info['cmap']
                norm = cmap_info['norm']

                # Create a new axis for the colorbar
                cax_height = 0.02
                cax_width = 0.3
                cax = fig.add_axes([0.35, y_pos - cax_height/2, cax_width, cax_height])

                # Create the colorbar
                sm = ScalarMappable(cmap=cmap, norm=norm)
                sm.set_array([])
                cbar = plt.colorbar(sm, cax=cax, orientation='horizontal')

                # Add title
                cbar.set_label(display_title, fontsize=10, labelpad=8)
                cbar.ax.tick_params(labelsize=8)

                legends.append(cbar)
            else:
                # Categorical legend
                lut = color_maps[header]['lut']

                # Filter out None/NaN keys for the legend
                filtered_lut = {k: v for k, v in lut.items() if k is not None and not (isinstance(k, float) and np.isnan(k)) and k != ''}

                # Add a "Missing" entry if there were missing values
                has_missing = None in lut or np.nan in lut or '' in lut
                if has_missing:
                    filtered_lut["Missing"] = missing_color

                # Create handles for the legend
                handles = [plt.Rectangle((0,0), 1.5, 1.5, color=color, ec="k") for label, color in filtered_lut.items()]
                labels = list(filtered_lut.keys())

                # Add legend
                num_items = len(filtered_lut)

                # Determine number of columns based on number of items
                legend_ncol = 1
                if num_items > 6:
                    legend_ncol = 2
                if num_items > 12:
                    legend_ncol = 3

                leg = ax.legend(
                    handles, 
                    labels, 
                    title=display_title,
                    loc="center", 
                    bbox_to_anchor=(0.5, y_pos),
                    ncol=legend_ncol,
                    frameon=True, 
                    fontsize=8,
                    title_fontsize=10
                )

                # Need to manually add the legend
                ax.add_artist(leg)
                legends.append(leg)

        plt.tight_layout()

        # Save figure if path provided
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight', format='png')
            

        return fig

    def get_top_tokens(self, top_n: Optional[int] = None) -> pd.DataFrame:
        """
        Get top tokens for each topic.

        Args:
            top_n: Number of top tokens to extract per topic

        Returns:
            DataFrame with top tokens for each topic
        """
        if top_n is None:
            top_n = self.config['top_asv_count']

        top_tokens_df = self.ASV_probabilities.apply(
            lambda row: row.nlargest(top_n), axis=1
        )

        return top_tokens_df

    def create_topic_taxon_heatmap(self, 
                                 highlight_taxa_dict: Optional[Dict] = None,
                                 custom_filename: Optional[str] = None,
                                 threshold: float = 0,
                                 cmap_below: str = 'Blues',
                                 cmap_above: str = 'Reds') -> Any:
        """
        Create a topic-taxon heatmap with different color scales.

        Args:
            highlight_taxa_dict: Dictionary with colors as keys and lists of taxa names as values
            custom_filename: Custom filename for output
            threshold: Boundary value that separates the two color scales
            cmap_below: Colormap for values below threshold
            cmap_above: Colormap for values above threshold

        Returns:
            Matplotlib axes object
        """
        if custom_filename is None:
            output_file = os.path.join(self.viz_directory, f"topic_taxon_heatmap_K{self.k_value}.png")
        else:
            output_file = os.path.join(self.viz_directory, f"{custom_filename}.png")

        # Use the ASV probabilities data
        ax = self._create_topic_taxon_heatmap_internal(
            data_matrix=self.ASV_probabilities,
            output_file=output_file,
            highlight_taxa_dict=highlight_taxa_dict,
            threshold=threshold,
            cmap_below=cmap_below,
            cmap_above=cmap_above,
            taxa_already_as_columns=True,
            vmin=self.config['heatmap_vmin'],
            vmax=self.config['heatmap_vmax']
        )

        print(f"✓ Topic-taxon heatmap saved: {output_file}")
        return ax

    def _create_topic_taxon_heatmap_internal(self, data_matrix, output_file=None,
                                           highlight_taxa_dict=None, threshold=0,
                                           cmap_below='Blues', cmap_above='Reds',
                                           taxa_already_as_columns=False,
                                           vmin=None, vmax=None):
        """Internal method for creating topic-taxon heatmap."""
        # Create a copy to avoid modifying the original
        df = data_matrix.copy()

        # Get the dataframe in the right orientation: taxa as columns, topics as rows
        if not taxa_already_as_columns:
            df = df.T

        # Determine color scale boundaries
        if vmin is None:
            vmin = df.values.min()
        if vmax is None:
            vmax = df.values.max()

        # Ensure the threshold is within the data range and create valid ordering
        threshold = max(vmin, min(vmax, threshold))

        # For TwoSlopeNorm, we need vmin < vcenter < vmax
        # If threshold equals vmin or vmax, adjust slightly
        if threshold == vmin:
            threshold = vmin + (vmax - vmin) * 0.01  # Move threshold slightly above vmin
        elif threshold == vmax:
            threshold = vmax - (vmax - vmin) * 0.01  # Move threshold slightly below vmax

        # Double-check the ordering
        if not (vmin < threshold < vmax):
            # If we still don't have proper ordering, use a simple colormap instead
            print(f"Warning: Cannot create TwoSlopeNorm with vmin={vmin:.6f}, threshold={threshold:.6f}, vmax={vmax:.6f}")
            print("Using simple colormap instead")

            # Use a simple colormap
            # Create figure with appropriate size based on number of taxa columns
            # Limit the maximum width to prevent oversized figures
            max_width = 50  # Maximum figure width in inches
            calculated_width = max(12, len(df.columns) * 0.25)
            figure_width = min(calculated_width, max_width)

            if calculated_width > max_width:
                print(f"Warning: Calculated figure width ({calculated_width:.1f}) exceeds maximum ({max_width})")
                print(f"Using maximum width of {max_width} inches. Consider filtering to fewer taxa.")

            plt.figure(figsize=(figure_width, 10))
            ax = sns.heatmap(df, cmap='Blues', linewidths=0.5, linecolor='white',
                             cbar_kws={'label': 'Probability'})
        else:
            # For LDA word weights (all positive values), use TwoSlopeNorm
            if vmin >= 0:  # If all data is positive (LDA word weights)
                # Create colormaps
                cmap_below_obj = plt.get_cmap(cmap_below)
                cmap_above_obj = plt.get_cmap(cmap_above)

                # Create a colormap that changes at the threshold
                below_colors = cmap_below_obj(np.linspace(0, 1, 128))
                above_colors = cmap_above_obj(np.linspace(0, 1, 128))

                # Create a new colormap
                all_colors = np.vstack((below_colors, above_colors))
                custom_cmap = ListedColormap(all_colors)

                # Use TwoSlopeNorm for positive data with a threshold
                norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=threshold, vmax=vmax)

                # Create figure with appropriate size based on number of taxa columns
                # Limit the maximum width to prevent oversized figures
                max_width = 50  # Maximum figure width in inches
                calculated_width = max(12, len(df.columns) * 0.25)
                figure_width = min(calculated_width, max_width)

                if calculated_width > max_width:
                    print(f"Warning: Calculated figure width ({calculated_width:.1f}) exceeds maximum ({max_width})")
                    print(f"Using maximum width of {max_width} inches. Consider filtering to fewer taxa.")

                plt.figure(figsize=(figure_width, 10))

                # Create the heatmap with the appropriate colormap and norm
                ax = sns.heatmap(df, cmap=custom_cmap, norm=norm, linewidths=0.5, linecolor='white',
                                 cbar_kws={'label': 'Probability'})
            else:
                # For data that can be negative, use a custom diverging norm
                # Define a custom normalization class
                class DivergingNorm(mcolors.Normalize):
                    def __init__(self, vmin=None, vmax=None, threshold=0, clip=False):
                        self.threshold = threshold
                        mcolors.Normalize.__init__(self, vmin, vmax, clip)

                    def __call__(self, value, clip=None):
                        # Normalize values to [0, 1] for each segment separately
                        x = np.ma.array(value, copy=True)

                        # For values below or equal to threshold
                        mask_below = x <= self.threshold
                        if np.any(mask_below):
                            if self.threshold > self.vmin:
                                x_below = (self.threshold - x[mask_below]) / (self.threshold - self.vmin)
                            else:
                                x_below = np.zeros_like(x[mask_below])
                            x[mask_below] = x_below

                        # For values above threshold
                        mask_above = x > self.threshold
                        if np.any(mask_above):
                            if self.vmax > self.threshold:
                                x_above = (x[mask_above] - self.threshold) / (self.vmax - self.threshold)
                            else:
                                x_above = np.ones_like(x[mask_above])
                            x[mask_above] = x_above

                        return np.ma.array(x, mask=np.ma.getmask(value))

                # Create the custom colormap and norm
                cmap_below_obj = plt.get_cmap(cmap_below)
                cmap_above_obj = plt.get_cmap(cmap_above)
                below_colors = cmap_below_obj(np.linspace(0, 1, 128))
                above_colors = cmap_above_obj(np.linspace(0, 1, 128))
                all_colors = np.vstack((below_colors, above_colors))
                custom_cmap = ListedColormap(all_colors)

                # Create the custom diverging norm
                norm = DivergingNorm(vmin=vmin, vmax=vmax, threshold=threshold)

                # Create figure with appropriate size based on number of taxa columns
                plt.figure(figsize=(max(12, len(df.columns) * 0.25), 10))

                # Create the heatmap with the appropriate colormap and norm
                ax = sns.heatmap(df, cmap=custom_cmap, norm=norm, linewidths=0.5, linecolor='white',
                                 cbar_kws={'label': 'Probability'})

        # Set the title
        plt.title(f'Topic-Taxon Distribution (K={self.k_value})', fontsize=16)

        # Rotate x-tick labels for better readability
        plt.xticks(rotation=90)

        # Now apply highlighting based on the actual column names
        if highlight_taxa_dict:
            # Get all tick labels
            tick_labels = df.columns.tolist()

            # Create a mapping from column names to positions
            column_to_position = {col: pos for pos, col in enumerate(tick_labels)}

            # Highlight the taxa in the dictionary
            for color, taxa_list in highlight_taxa_dict.items():
                for taxon_name in taxa_list:
                    # Check if this taxon is in our columns
                    if taxon_name in column_to_position:
                        position = column_to_position[taxon_name]

                        # Get the x-tick label at this position
                        x_tick_labels = ax.get_xticklabels()
                        if position < len(x_tick_labels):
                            label = x_tick_labels[position]

                            # Style the label
                            label.set_color(color)
                            label.set_fontweight('bold')

        # Tight layout to ensure all elements are visible
        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, bbox_inches='tight', dpi=300)

        return ax

    def create_clustered_taxa_heatmap(self, 
                                    highlight_dict: Optional[Dict] = None,
                                    custom_filename: Optional[str] = None,
                                    rename_columns: Optional[Dict] = None) -> Tuple[Any, Any]:
        """
        Create a clustered heatmap from token probability data with optional highlighting.

        Args:
            highlight_dict: Dictionary with colors as keys and lists of taxa names as values
            custom_filename: Custom filename for output
            rename_columns: Dictionary to rename specific columns

        Returns:
            Tuple of (figure, axes)
        """
        if custom_filename is None:
            output_path = os.path.join(self.viz_directory, f"clustered_taxa_heatmap_K{self.k_value}.png")
        else:
            output_path = os.path.join(self.viz_directory, f"{custom_filename}.png")

        # Get top tokens
        top_tokens_df = self.get_top_tokens()

        # Create the clustered heatmap
        fig, ax = self._create_clustered_heatmap_taxa_internal(
            top_tokens_df=top_tokens_df,
            output_path=output_path,
            highlight_dict=highlight_dict,
            vmin=self.config['heatmap_vmin'],
            vmax=self.config['heatmap_vmax'],
            figsize=self.config['figsize'],
            cbar_ticks=self.config['cbar_ticks'],
            rename_columns=rename_columns
        )

        print(f"✓ Clustered taxa heatmap saved: {output_path}")
        return fig, ax

    def _create_clustered_heatmap_taxa_internal(self, top_tokens_df, output_path=None, highlight_dict=None, 
                                              vmin=0, vmax=0.4, figsize=(14, 10), 
                                              cbar_ticks=[0, 0.02, 0.05, 0.1, 0.3],
                                              rename_columns=None):
        """Internal method for creating clustered taxa heatmap."""
        # Make a copy to avoid modifying the original dataframe
        top_tokens_df_customized = top_tokens_df.copy()

        # Rename columns if specified
        if rename_columns:
            top_tokens_df_customized = top_tokens_df_customized.rename(columns=rename_columns)

        # Fill any NaN values with 0 to avoid distance computation issues
        df_for_clustering = top_tokens_df_customized.fillna(0)

        # Add a small epsilon to any zero rows to avoid distance computation issues
        epsilon = 1e-10

        # Add epsilon to rows that are all zeros
        if (df_for_clustering.sum(axis=1) == 0).any():
            zero_rows = df_for_clustering.sum(axis=1) == 0
            df_for_clustering.loc[zero_rows] = epsilon

        # Add epsilon to columns that are all zeros
        if (df_for_clustering.sum(axis=0) == 0).any():
            zero_cols = df_for_clustering.sum(axis=0) == 0
            df_for_clustering.loc[:, zero_cols] = epsilon

        # Compute clustering with the cleaned data
        row_linkage = hierarchy.linkage(distance.pdist(df_for_clustering.values), method='ward')
        row_order = hierarchy.dendrogram(row_linkage, no_plot=True)['leaves']

        # Compute the clustering for columns (taxa)
        col_linkage = hierarchy.linkage(distance.pdist(df_for_clustering.values.T), method='ward')
        col_order = hierarchy.dendrogram(col_linkage, no_plot=True)['leaves']

        # Reorder the original dataframe according to the clustering
        df_clustered = top_tokens_df_customized.iloc[row_order, col_order]

        # Fill NaN values with zeros for visualization purposes
        df_clustered_filled = df_clustered.fillna(0)

        # Set up the plot
        fig, ax = plt.subplots(figsize=figsize)

        # Create a continuous colormap using PuBu
        cmap = plt.cm.PuBu

        # Create a custom normalization
        norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

        # Create the heatmap with annotations and continuous colors
        heatmap = sns.heatmap(df_clustered_filled, 
                      cmap=cmap,
                      norm=norm,
                      cbar_kws={'label': 'Probability',
                                'ticks': cbar_ticks,
                                'shrink': 0.5,  # Make the colorbar shorter
                                'fraction': 0.046,  # Adjust width
                                'pad': 0.04,    # Adjust distance from plot
                                'aspect': 20},  # Make it thinner
                      annot=True,
                      fmt='.2f',
                      annot_kws={'size': 8},
                      square=True,
                      mask=pd.isna(df_clustered),
                      ax=ax)

        # Rotate the x-axis labels for better readability
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.yticks(fontsize=10)

        # Apply highlighting if provided
        if highlight_dict:
            # Get the current tick labels
            xlabels = [label.get_text() for label in ax.get_xticklabels()]

            # Create a list to hold legend handles
            legend_handles = []

            # Process each color in the highlight dict
            for color, taxa_list in highlight_dict.items():
                # Find which taxa in the list are actually in the x-axis labels
                for i, label_text in enumerate(xlabels):
                    if label_text in taxa_list:
                        # Get the current label
                        label = ax.get_xticklabels()[i]
                        # Set its color
                        label.set_color(color)
                        # Make it bold
                        label.set_fontweight('bold')

                # Add to legend only if at least one taxon with this color exists in the plot
                if any(taxon in xlabels for taxon in taxa_list):
                    patch = mpatches.Patch(color=color, label=f"{color.capitalize()} highlighted taxa")
                    legend_handles.append(patch)

            # Add legend if there are handles
            if legend_handles:
                plt.legend(handles=legend_handles, loc='upper left', bbox_to_anchor=(1.05, 1), 
                          borderaxespad=0.)

        # Set title
        plt.title(f'Clustered Taxa Heatmap (K={self.k_value}, Top {self.config["top_asv_count"]} ASVs)', fontsize=14)

        # Tight layout to ensure all elements are visible
        plt.tight_layout()

        # Save the figure if a path is provided
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')

        return fig, ax

    def create_all_visualizations(self, 
                                custom_prefix: Optional[str] = None,
                                highlight_taxa_dict: Optional[Dict] = None,
                                include_feature_analysis: bool = True) -> Dict[str, Any]:
        """
        Create all standard visualizations for the model.

        Args:
            custom_prefix: Custom prefix for all output files
            highlight_taxa_dict: Dictionary for highlighting specific taxa
            include_feature_analysis: Whether to include topic-feature analysis

        Returns:
            Dictionary containing all visualization objects
        """
        print(f"Creating all visualizations for K={self.k_value}...")
        print("=" * 50)

        results = {}

        # 1. Prepare heatmap data
        print("1️⃣ Preparing heatmap data...")
        multiheader = self.prepare_heatmap_data()
        results['multiheader'] = multiheader

        # 2. Create clustered heatmap with metadata
        print("\n2️⃣ Creating clustered heatmap with metadata...")
        filename = f"{custom_prefix}_clustered_metadata" if custom_prefix else None
        g, legend_fig = self.create_clustered_heatmap(
            multiheader=multiheader,
            custom_filename=filename
        )
        results['clustered_heatmap'] = g
        results['legend_figure'] = legend_fig

        # 3. Create clustered taxa heatmap (topic-feature analysis)
        if include_feature_analysis:
            print("\n3️⃣ Creating topic-feature analysis...")
            try:
                # Import and use TopicFeatureProcessor
                feature_processor = TopicFeatureProcessor(self.base_directory, self.k_value)

                # Create the default clustered taxa heatmap
                filename = f"{custom_prefix}_clustered_taxa" if custom_prefix else None
                ax_taxa = feature_processor.create_default_visualization(
                    top_n=self.config.get('top_asv_count', 10),
                    custom_filename=filename,
                    highlight_features=highlight_taxa_dict
                )
                results['clustered_taxa_heatmap'] = ax_taxa
                results['feature_processor'] = feature_processor

            except Exception as e:
                print(f"Warning: Could not create topic-feature analysis: {e}")
                results['clustered_taxa_heatmap'] = None

        print("\n" + "=" * 50)
        print("🎉 All visualizations created successfully!")
        print(f"📁 Outputs saved to: {self.viz_directory}")
        if include_feature_analysis:
            print("📊 Topic-feature analysis uses genus_ID level by default")
        print("=" * 50)

        return results

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the loaded model and configuration.

        Returns:
            Dictionary containing model summary information
        """
        return {
            'k_value': self.k_value,
            'base_directory': self.base_directory,
            'num_samples': len(self.DM_distributions),
            'num_topics': len(self.DM_distributions[0]) if self.DM_distributions else 0,
            'num_asvs': self.ASV_probabilities.shape[1] if hasattr(self, 'ASV_probabilities') else 0,
            'metadata_columns': list(self.metadata.columns) if hasattr(self, 'metadata') else [],
            'configured_headers': {
                'universal': self.config['universal_headers'],
                'continuous': self.config['continuous_headers']
            },
            'visualization_config': {
                'top_asv_count': self.config['top_asv_count'],
                'custom_colors': list(self.config['custom_colors'].keys()),
                'continuous_cmaps': list(self.config['continuous_cmaps'].keys())
            }
        }


class TopicFeatureProcessor:
    """
    A class for processing topic-feature matrices by mapping ASVs to taxonomic levels.

    This class handles:
    - Loading ASV probabilities and taxonomic data
    - Mapping ASVs to specified taxonomic levels
    - Grouping and summing probabilities by taxonomic level
    - Creating visualizations of topic-feature matrices
    - Integration with LDAModelVisualizer workflow
    """

    def __init__(self, base_directory: str, k_value: int):
        """
        Initialize the Topic Feature Processor.

        Args:
            base_directory: Base directory where LDA results are stored
            k_value: Number of topics (K) to process
        """
        self.base_directory = base_directory
        self.k_value = k_value

        # Set up paths
        self._setup_paths()

        # Initialize data containers
        self.new_taxa = None
        self.asv_probabilities = None
        self.processed_data = {}

        print(f"TopicFeatureProcessor initialized for K={k_value}")
        print(f"  Base directory: {self.base_directory}")

    def _setup_paths(self):
        """Set up all necessary paths."""
        self.inter_directory = os.path.join(self.base_directory, 'intermediate')
        self.lda_directory = os.path.join(self.base_directory, 'lda_results')
        self.MC_feature_directory = os.path.join(self.lda_directory, 'MC_Feature')
        self.viz_directory = os.path.join(self.base_directory, 'lda_visualization')

        # Create visualization directory
        os.makedirs(self.viz_directory, exist_ok=True)

        # Set up file paths
        self.path_to_new_taxa = os.path.join(self.inter_directory, "intermediate_taxa.csv")
        self.path_to_ASVProbabilities = os.path.join(
            self.MC_feature_directory, f"MC_Feature_Probabilities_{self.k_value}.csv"
        )

    def load_data(self):
        """Load taxonomic and ASV probability data."""
        try:
            # Load taxonomic data
            print(f"Reading taxonomic data from: {self.path_to_new_taxa}")
            self.new_taxa = pd.read_csv(self.path_to_new_taxa, index_col=0)
            print(f"✓ Taxonomic data loaded: {self.new_taxa.shape}")

            # Load ASV probabilities
            print(f"Reading ASV probabilities from: {self.path_to_ASVProbabilities}")
            self.asv_probabilities = pd.read_csv(self.path_to_ASVProbabilities, index_col=0)
            print(f"✓ ASV probabilities loaded: {self.asv_probabilities.shape}")

            # Display available taxonomic levels
            available_levels = [col for col in self.new_taxa.columns if col not in ['randomID']]
            print(f"✓ Available taxonomic levels: {available_levels}")

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Required data file not found: {e}")
        except Exception as e:
            raise Exception(f"Error loading data: {e}")

    def process_feature_level(self, 
                            feature_level: str = 'genus_ID', 
                            top_n: int = 10,
                            get_top_tokens_func: Optional[Callable] = None) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        """
        Process ASV probabilities at a specified taxonomic level.

        Args:
            feature_level: Taxonomic level to group by ('Genus', 'Family', 'Order', etc.)
            top_n: Number of top features to extract per topic
            get_top_tokens_func: Custom function to get top tokens

        Returns:
            Tuple of (processed_probabilities_df, top_tokens_df)
        """
        # Load data if not already loaded
        if self.new_taxa is None or self.asv_probabilities is None:
            self.load_data()

        # Validate feature level
        if feature_level not in self.new_taxa.columns:
            available_cols = [col for col in self.new_taxa.columns if col not in ['randomID']]
            raise ValueError(f"Feature level '{feature_level}' not found. Available: {available_cols}")

        print(f"\nProcessing feature level: {feature_level}")
        print("=" * 50)

        # Create mapping dictionary
        print(f"Creating mapping dictionary using column: {feature_level}")
        mapping_dict = dict(zip(self.new_taxa['randomID'], self.new_taxa[feature_level]))

        # Create MC labels
        MC_list = [f"MC{i}" for i in range(self.k_value)]
        print(f"Created {len(MC_list)} MC labels: {MC_list}")

        # Prepare ASV probabilities
        AP = self.asv_probabilities.copy()
        AP = AP.reset_index(drop=True)
        AP.index = MC_list

        print(f"Original ASV probabilities shape: {AP.shape}")

        # Map column names using the dictionary
        print("Mapping ASV IDs to taxonomic names...")
        original_columns = AP.columns.tolist()
        AP.columns = [mapping_dict.get(col, col) for col in AP.columns]

        # Count mapped columns
        mapped_count = sum(1 for orig_col in original_columns if orig_col in mapping_dict)
        print(f"Mapped {mapped_count}/{len(original_columns)} columns to taxonomic names")

        # Group by taxonomic level and sum probabilities
        print(f"Grouping by {feature_level} and summing probabilities...")
        grouped_AP = AP.groupby(level=0, axis=1).sum()

        print(f"✓ Grouped probabilities shape: {grouped_AP.shape}")
        print(f"✓ Unique {feature_level} features: {len(grouped_AP.columns)}")

        # Calculate top tokens
        top_tokens_df = None
        if get_top_tokens_func is None:
            # Default function
            def default_top_tokens(row):
                return row.nlargest(top_n)
            get_top_tokens_func = default_top_tokens

        try:
            print(f"Calculating top {top_n} tokens for each MC...")
            top_tokens_df = grouped_AP.apply(get_top_tokens_func, axis=1)
            print(f"✓ Top tokens calculated: {top_tokens_df.shape}")
        except Exception as e:
            print(f"Warning: Could not calculate top tokens - {str(e)}")
            top_tokens_df = None

        # Store processed data
        self.processed_data[feature_level] = {
            'grouped_probabilities': grouped_AP,
            'top_tokens': top_tokens_df,
            'mapping_count': mapped_count,
            'total_features': len(grouped_AP.columns)
        }

        # Print summary
        print("\n=== PROCESSING SUMMARY ===")
        print(f"Feature level: {feature_level}")
        print(f"Number of MCs: {len(MC_list)}")
        print(f"Original ASVs: {len(original_columns)}")
        print(f"Mapped ASVs: {mapped_count}")
        print(f"Unique {feature_level} features: {len(grouped_AP.columns)}")
        print("=" * 50)

        return grouped_AP, top_tokens_df

    def create_feature_heatmap(self, 
                             feature_level: str = 'genus_ID',
                             use_top_tokens: bool = True,
                             top_n: int = 10,
                             figsize: Tuple[int, int] = (16, 8),  # Increased default width
                             custom_filename: Optional[str] = None,
                             highlight_features: Optional[Dict] = None,
                             **heatmap_kwargs) -> plt.Axes:
        """
        Create a heatmap of topic-feature probabilities.

        Args:
            feature_level: Taxonomic level to visualize
            use_top_tokens: Whether to use only top tokens or all features
            top_n: Number of top tokens to show (if use_top_tokens=True)
            figsize: Figure size
            custom_filename: Custom filename for output
            highlight_features: Dict with colors as keys and feature lists as values
            **heatmap_kwargs: Additional arguments for seaborn heatmap

        Returns:
            matplotlib Axes object
        """
        # Process data if not already done
        if feature_level not in self.processed_data:
            self.process_feature_level(feature_level, top_n=top_n)

        # Get data to plot
        if use_top_tokens and self.processed_data[feature_level]['top_tokens'] is not None:
            data_to_plot = self.processed_data[feature_level]['top_tokens']
            plot_title = f'Top {top_n} {feature_level} Features by Topic (K={self.k_value})'
        else:
            data_to_plot = self.processed_data[feature_level]['grouped_probabilities']
            plot_title = f'All {feature_level} Features by Topic (K={self.k_value})'

        # Set up the plot
        plt.figure(figsize=figsize)

        # Default heatmap parameters
        default_kwargs = {
            'cmap': 'Blues',
            'annot': True,
            'fmt': '.2f',
            'annot_kws': {'size': 9, 'weight': 'bold'},  # Larger, bolder text
            'cbar_kws': {'label': 'Probability'},
            'linewidths': 0.5,
            'square': False  # Allow rectangular cells for better text fit
        }
        default_kwargs.update(heatmap_kwargs)

        # Create heatmap
        ax = sns.heatmap(data_to_plot, **default_kwargs)

        # Set aspect ratio to allow wider cells
        ax.set_aspect('auto')

        # Adjust subplot parameters to ensure everything fits
        plt.subplots_adjust(bottom=0.25, left=0.1, right=0.9, top=0.85)

        # Set title
        plt.title(plot_title, fontsize=14, pad=20)

        # Rotate x-axis labels
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)

        # Apply highlighting if provided
        if highlight_features:
            self._apply_feature_highlighting(ax, highlight_features)

        # Adjust layout
        plt.tight_layout()

        # Save if filename provided
        if custom_filename is None:
            filename = f"topic_{feature_level}_heatmap_K{self.k_value}"
            if use_top_tokens:
                filename += f"_top{top_n}"
        else:
            filename = custom_filename

        output_path = os.path.join(self.viz_directory, f"{filename}.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Feature heatmap saved: {output_path}")
        
        svg_path = output_path.replace('.png', '.svg')
        plt.savefig(svg_path, bbox_inches='tight')

        return ax

    def _apply_feature_highlighting(self, ax: plt.Axes, highlight_features: Dict):
        """Apply color highlighting to specific features in the heatmap."""
        # Get current tick labels
        xlabels = [label.get_text() for label in ax.get_xticklabels()]

        # Apply highlighting
        for color, feature_list in highlight_features.items():
            for i, label_text in enumerate(xlabels):
                if label_text in feature_list:
                    # Get the current label and style it
                    label = ax.get_xticklabels()[i]
                    label.set_color(color)
                    label.set_fontweight('bold')

    def create_feature_comparison(self, 
                                feature_levels: List[str] = None,
                                top_n: int = 10,
                                figsize: Tuple[int, int] = (15, 10)) -> plt.Figure:
        """
        Create a comparison plot of multiple taxonomic levels.

        Args:
            feature_levels: List of taxonomic levels to compare (defaults to common levels)
            top_n: Number of top features to show for each level
            figsize: Figure size

        Returns:
            matplotlib Figure object
        """
        # Use default feature levels if none provided
        if feature_levels is None:
            feature_levels = ['genus_ID', 'Genus', 'Family']
        # Process all feature levels
        for level in feature_levels:
            if level not in self.processed_data:
                self.process_feature_level(level, top_n=top_n)

        # Create subplots
        n_levels = len(feature_levels)
        fig, axes = plt.subplots(1, n_levels, figsize=figsize)

        if n_levels == 1:
            axes = [axes]

        # Create heatmap for each level
        for i, level in enumerate(feature_levels):
            data = self.processed_data[level]['top_tokens']
            if data is not None:
                sns.heatmap(
                    data, 
                    ax=axes[i],
                    cmap='Blues',
                    annot=True,
                    fmt='.3f',
                    cbar=True,
                    xticklabels=True,
                    yticklabels=True if i == 0 else False
                )
                axes[i].set_title(f'{level}\n(Top {top_n})', fontsize=12)
                axes[i].tick_params(axis='x', rotation=45)

        plt.suptitle(f'Topic-Feature Comparison (K={self.k_value})', fontsize=16)
        plt.tight_layout()

        # Save comparison plot
        output_path = os.path.join(self.viz_directory, f"feature_comparison_K{self.k_value}.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Feature comparison saved: {output_path}")

        return fig

    def get_feature_summary(self, feature_level: str) -> Dict[str, Any]:
        """
        Get summary statistics for a processed feature level.

        Args:
            feature_level: Taxonomic level to summarize

        Returns:
            Dictionary with summary statistics
        """
        if feature_level not in self.processed_data:
            raise ValueError(f"Feature level '{feature_level}' not processed yet")

        data = self.processed_data[feature_level]
        grouped_probs = data['grouped_probabilities']

        # Calculate statistics
        summary = {
            'feature_level': feature_level,
            'k_value': self.k_value,
            'num_topics': len(grouped_probs),
            'num_features': len(grouped_probs.columns),
            'mapped_asvs': data['mapping_count'],
            'total_probability_mass': grouped_probs.sum().sum(),
            'avg_probability_per_feature': grouped_probs.mean(axis=0).mean(),
            'max_probability': grouped_probs.max().max(),
            'min_probability': grouped_probs.min().min(),
            'sparsity': (grouped_probs == 0).sum().sum() / grouped_probs.size,
            'top_features_per_topic': {}
        }

        # Get top feature for each topic
        for topic in grouped_probs.index:
            top_feature = grouped_probs.loc[topic].idxmax()
            top_prob = grouped_probs.loc[topic].max()
            summary['top_features_per_topic'][topic] = {
                'feature': top_feature,
                'probability': top_prob
            }

        return summary

    def create_default_visualization(self,
                                   top_n: int = 10,
                                   custom_filename: Optional[str] = None,
                                   highlight_features: Optional[Dict] = None) -> plt.Axes:
        """
        Create the default clustered taxa heatmap using genus_ID.

        Args:
            top_n: Number of top features to show
            custom_filename: Custom filename for output
            highlight_features: Dict with colors as keys and feature lists as values

        Returns:
            matplotlib Axes object
        """
        # Process genus_ID level if not already done
        if 'genus_ID' not in self.processed_data:
            self.process_feature_level('genus_ID', top_n=top_n)

        # Create the heatmap with default filename
        if custom_filename is None:
            custom_filename = f"clustered_taxa_heatmap_K{self.k_value}"

        ax = self.create_feature_heatmap(
            feature_level='genus_ID',
            use_top_tokens=True,
            top_n=top_n,
            custom_filename=custom_filename,
            highlight_features=highlight_features
        )

        return ax
        """
        Save processed data to CSV files.

        Args:
            feature_level: Taxonomic level to save
            output_dir: Output directory (uses viz_directory if None)
        """
        if feature_level not in self.processed_data:
            raise ValueError(f"Feature level '{feature_level}' not processed yet")

        if output_dir is None:
            output_dir = self.viz_directory

        data = self.processed_data[feature_level]

        # Save grouped probabilities
        grouped_file = os.path.join(output_dir, f"topic_{feature_level}_probabilities_K{self.k_value}.csv")
        data['grouped_probabilities'].to_csv(grouped_file)
        print(f"✓ Grouped probabilities saved: {grouped_file}")

        # Save top tokens if available
        if data['top_tokens'] is not None:
            top_tokens_file = os.path.join(output_dir, f"topic_{feature_level}_top_tokens_K{self.k_value}.csv")
            data['top_tokens'].to_csv(top_tokens_file)
            print(f"✓ Top tokens saved: {top_tokens_file}")

