# Microbiome LDA Topic Modeling Workflow

## Overview
This workflow implements Latent Dirichlet Allocation (LDA) topic modeling for microbiome data analysis using MALLET through the my_little_warp Python interface.

## Workflow Illustration
Please refer to the workflow diagram in ![Workflow Diagram](figures/workflow.drawio.svg) for a visual representation of the process.

## Workflow Steps
The workflow consists of three steps, corresponding to three `.py` files. The first step may take significant time to run (depends on the size of your data, potentially hours). Once all models are calculated, you can select an optimal model based on evaluation metrics and domain interpretation.
Three types of data are required: an ASV table (rows represent samples, columns represent features), a taxonomy mapping file, and sample metadata. You can find examples of these data files in the example folder.

### Step 0: Data Transforming (`step0_DataPreprocessing(MALLET).py`)

#### Inputs

- Input ASV abundance table and taxonomy file paths
- ASV abundance table requires a CSV file where the index contains samples and columns contain features (ASV IDs), with values as **raw counts** instead of relative abundance values
- Taxonomy table requires a CSV file where the index contains ASV IDs and columns include taxonomy levels (Domain, Kingdom, Phylum, Class, Order, Family, Genus, and Species)

#### Process

- Annotating ASVs based on genus level, falling back through taxonomic hierarchy (Family → Order → Class → Phylum) when genus is missing/uncultured. Assign unique IDs to ASVs that share the same annotation, allowing ASV-level interpretation
- Creating random IDs for each ASV to avoid LDA package's built-in data processing
- Transforming data format - Converting ASV abundance tables into document format where each sample becomes a "document" with taxa repeated based on their abundance counts
- Preparing Mallet input - Creating training files for the Mallet LDA toolkit

#### Outputs

Get a dictionary including:
- `asvtable`: Transposed ASV abundance matrix
- `taxa_split`: Enhanced taxonomy table with genus-based names, sequential IDs, and random IDs
- `sampletable_randomID`: ASV table with columns renamed to random IDs for anonymization
- `paths`: Dictionary of all created directory and file paths for the analysis pipeline

### Step 1: Model Building (`step1_loop_.py`)
- Inputs include ASV table and taxonomy mapping file.
- Explore topic models across a predefined range of topics (K)
- Default K range: 2 to 21 microbe components (MC), but adjust this range based on your research question
- Fewer models will take less time to run
- Utilize MALLET for robust LDA topic modeling
- Implement through my_little_warp Python interface

### Step 2: Model Evaluation (`step2_selection(new).py`)
- Calculate and analyze key evaluation metrics
- Metrics include:
  - Coherence scores
  - Perplexity
  - Number of microbe component clusters in all models (Ideally, K should not exceed this number)
- Compare performance across different numbers of topics

### Step 3: Model Selection and Visualization (`step3_visualization.py`)
- Inputs include which K you selected.
- Make an informed decision on the optimal number of topics
- Generate visualizations to support topic interpretation
- Create:
  - MC-sample heatmap, annotated by selected metadata
  - MC-ASV heatmap
  - Interpretative visualizations of microbiome topics

## Key Considerations
- Careful selection of K (number of topics)
- Interpretation of topics in the biological context
- Validation of results

## Output
Comprehensive analysis of microbiome data through probabilistic topic modeling

## Installation

# Clone the repository
git clone https://github.com/username/microbiome-lda-workflow.git
cd microbiome-lda-workflow

# Create and activate conda environment
conda env create -f environment.yml
conda activate microbiome-lda
