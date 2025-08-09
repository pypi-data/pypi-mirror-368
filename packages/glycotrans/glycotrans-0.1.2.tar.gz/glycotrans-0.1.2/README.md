# GlycoTrans

GlycoTrans is a package for predicting glycan structures from LC-MS/MS data. The package provides an inference pipeline along with utilities required for glycan structure prediction
using our GlycoBERT and GlycoBART transformer-based deep learning models. For more details on the models and how we trained them, 
please refer to our [manuscript](https://doi.org/10.1101/2025.07.02.662857).

## Installation

### From PyPI
```bash
pip install glycotrans
```

### From GitHub
```bash
pip install git+https://github.com/CABSEL/glycotrans.git
```

We also offer a user-friendly Google Colaboratory notebook that allows you to run GlycoTrans without any local installation. The notebook contains a ready-to-use example workflow,
which you can easily copy, run, and adapt to your specific needs. [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1w7XSB_mjE3gV-zeI4r1HoVHStbf_wriD)

The `21658_Moon_20230505_90_MW055_CALNx1_002.mzML` file used in the notebook can be found at 

[![Google Drive](https://img.shields.io/badge/Google%20Drive-4285F4?style=for-the-badge&logo=googledrive&logoColor=white)](https://drive.google.com/file/d/1Cw2sPFwBrYifYP2_U-7w3O42JvwNfypk/view?usp=share_link)

## Usage

### `glycobert_inference()` from `utils.py`

Wrapper function for glycan structure inference from LC-MS/MS data using the GlycoBERT model.

**Required Arguments:**
<pre>
filepath (string): path to the .mzML or .mzXML LC-MS/MS spectral file
</pre>

**Optional Arguments:**

<pre>
- vocab_path (string, default = 'vocab_glycobert.json'): path to the GlycoBERT vocabulary file
- modelDir (string, default = 'CABSEL/glycobert'): path to the trained GlycoBERT model directory
- batch_size (int, default = 256): number of spectra to process during each batch
- filename (string, default = 'unspecified'): name of the .mzML or .mzXML MS/MS file
- lc (string, default = 'PGC'): type of liquid chromatography (LC) used; options: 'PGC', 'C18', 'HILIC', 'MGC', 'other_lc' (if LC type is  unknown or outside the given options)
- mode (string, default = 'negative'): type of ion mode used; options: 'negative', 'positive', 'other_mode' (if mode is unknown or outside the given options)
- modification (string, default = 'reduced'): type of glycan derivatization; options: 'reduced', 'permethylated', '2AA', 'PA', 'native', 'Rapifluor', 'other_mod' (if custom modification) 
- glycan_type (string, default = 'N'): type of glycan class; options: 'O', 'N', 'lipids', 'free', 'other_type' (if glycan type is unknown or outside the given options)
- trap (string, default = 'linear'): type of ion trap used; options: 'linear', 'orbitrap', 'amazon', 'MSD', 'TOF', 'octopole', 'other_trap' (if trap is unknown or outside the given options)
- ionization (string, default = 'other_ion'): type of ionization used; options: 'ESI', 'MALDI', 'other_ion' (if ionization is unknown or outside the given options)
- fragmentation (string, default = 'CID'): type of fragmentation used; options: 'CID', 'HCD', 'other_frag' (if fragmentation is unknown or outside the given options)
- taxonomy_level (string, default = 'Class'): taxonomic classification level to consider from df_use
- taxonomy_filter (string, default = 'Mammalia'): specific taxonomic Class of glycans to consider from df_use
- df_use (DataFrame, default = None): glycan database with known glycan structures, taxonomy_level, etc. By default, the df_glycan database from Glycowork package is used
- mass_tag (float, default = None): custom modification mass. Set modification to 'other_mod' if using custom mofification mass
- filter_out (set, default = {'Ac','Kdn', 'P', 'HexA', 'Pen', 'HexN', 'Me', 'PCho', 'PEtN'}): set of monosaccharide or modification types that is used to filter out compositions
- glycan_pkl (string, default = 'glycan_classes.pkl'): filepath to glycan classes used in GlycoBERT training
- device (string, default = 'cpu'): type of computing device used; options: 'cpu', 'cuda'
</pre>

**Output Arguments**
<pre>
df_out (DataFrame): dataframe containing predicted glycan structure, composition, etc.
</pre>

**Example Usage**
```
df_out = glycobert_inference(filepath = 'C:\files\21658_Moon_20230505_90_MW055_CALNx1_002.mzML', mode='positive', modification='reduced', glycan_type='O')
```



### `filter_glycans_glycobert()` from `utils.py`
Wrapper function for the downstream processing of glycan structures predicted by `glycobert_inference()`.
The predicted glycan structures are retained or removed based on the quality control filters such as precursor mass, diagnostic ions, etc.
Run this function after running the `glycobert_inference()` function.

**Required Arguments:**
<pre>
df_out (DataFrame): output dataframe from the glycobert_inference function
</pre>

**Optional Arguments:**

<pre>
- pred_thresh (int, default = 0.01): prediction confidence threshold used for filtering. Glycan structures with prediction confidence below pred_thresh are removed
- frag_threshold (int, default = 1): fraction of MS/MS peaks to consider. MS/MS peaks are sorted in the descending order of their intensity before filtering. frag_threshold ranges from 0 to 1
- MS1_ppm (int, default = 10): MS1 mass tolerance in ppm
- MS2_tolerance (int, default = 0.5): MS2 mass tolerance in Da
- annotation_thresh (int, default =3): threshold for number of ion matches
- filter_diag_ion (list, default = ['Neu5Gc', 'Kdn', 'S']): list of monosaccharides not expected in the prediction. Glycan structures with the listed monosaccharides will be removed
</pre>
see `glycobert_inference()` for the remaining arguments

**Output Arguments**
<pre>
- df_before_deduplication (DataFrame): dataframe containing glycan predictions from GlycoBERT model after all the quality filters
- df_filtered (DataFrame): dataframe after removing duplicate glycan predictions from df_before_deduplication dataframe
</pre>

**Example Usage**

```
df_filtered, df_before_deduplication = filter_glycans_glycobert(df_out)
```




### `glycobart_inference()` from `utils.py`
Wrapper function for glycan structure inference from LC-MS/MS data using the GlycoBART model.

**Required Arguments:**
<pre>
filepath (string): path to the .mzML or .mzXML LC-MS/MS spectral file
</pre>

**Optional Arguments:**

<pre>
- vocab_path (string, default = 'vocab_glycobart.json'): path to the GlycoBART vocabulary file
- modelDir (string, default = 'CABSEL/glycobart'): path to the trained GlycoBART model directory
- num_beam (int, default = 32): number of glycan structures to consider during GlycoBART inference
- num_return (int, default = 32): number of glycan structures to return from GlycoBART inference. Should not be greater than num_beam
</pre>
see `glycobert_inference()` for the remaining arguments

**Output Arguments**
<pre>
df_out (DataFrame): dataframe containing predicted glycan structure, composition, etc.
</pre>

**Example Usage**

```
df_out = glycobart_inference(filepath = 'C:\files\21658_Moon_20230505_90_MW055_CALNx1_002.mzML' , mode='positive', modification='reduced', glycan_type='O', num_beam = 4, num_return = 4)
```




### `filter_glycans_glycobart()` from `utils.py`
Wrapper function for the downstream processing of glycan structures predicted by `glycobart_inference()`.
The predicted glycan structures are retained or removed based on the quality control filters such as precursor mass, diagnostic ions, etc.
Run this function after running the `glycobart_inference()` function.

**Required Arguments:**
<pre>
df_out (DataFrame): output dataframe from the glycobart_inference function
</pre>

**Optional Arguments:**

see `glycobert_inference()` and `filter_glycans_glycobert()`

**Output Arguments**
<pre>
- df_before_deduplication (DataFrame): dataframe containing glycan predictions from GlycoBART model after all the quality filers
- df_filtered (DataFrame): dataframe after removing duplicate glycan predictions from df_before_deduplication dataframe
</pre>

**Example Usage**

```
df_filtered, df_before_deduplication = filter_glycans_glycobart(df_out)
```