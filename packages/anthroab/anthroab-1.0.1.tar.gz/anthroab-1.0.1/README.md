# AnthroAb: Human Antibody Language Model

```
             █████  ███    ██ ████████ ██   ██ ██████   ██████      █████  ██████  
             ██   ██ ████   ██    ██    ██   ██ ██   ██ ██    ██    ██   ██ ██   ██ 
             ███████ ██ ██  ██    ██    ███████ ██████  ██    ██ ██ ███████ ██████  
             ██   ██ ██  ██ ██    ██    ██   ██ ██   ██ ██    ██    ██   ██ ██   ██ 
             ██   ██ ██   ████    ██    ██   ██ ██   ██  ██████     ██   ██ ██████
```

AnthroAb is a human antibody language model based on RoBERTa, specifically trained for antibody humanization tasks.

## Features

- **Antibody Humanization**: Predict humanized versions of antibody sequences
- **Sequence Infilling**: Fill masked positions with human-like residues
- **Mutation Suggestions**: Suggest humanizing mutations for frameworks and CDRs
- **Embedding Generation**: Create vector representations of residues or sequences
- **Dual Chain Support**: Separate models for Variable Heavy (VH) and Variable Light (VL) chains

## Installation

```bash
# Install from PyPI (when published)
pip install anthroab

# Or install from source
git clone https://github.com/your-username/AnthroAb
cd AnthroAb
pip install -e .
```

## Quick Start

### Antibody Sequence Humanization

```python
import anthroab

# Humanize a heavy chain sequence
vh_sequence = "***LV*SGAEVKKPGASVKVSCKASGYTFTDYYIHWVKQRPEQGLEWIGWIDPENGDTEYAPKFQGKATITADTSSNTAYLQLSSLTSEDTAVYYCARNLGPSFYFDYWGQGTLVTVSS"
humanized_vh = anthroab.predict_best_score(vh_sequence, 'H')
print(f"Humanized VH: {humanized_vh}")

# Humanize a light chain sequence
vl_sequence = "DIQMTQSPSSLSASV*DRVTITCRASQSISSYLNWYQQKPGKAPKLLIYSASTLASGVPSRFSGSGSGTDF*LTISSLQPEDFATYYCQQSYSTPRTFGQGTKVEIK"
humanized_vl = anthroab.predict_best_score(vl_sequence, 'L')
print(f"Humanized VL: {humanized_vl}")
```

## Model Details

### Architecture
- **Base Model**: RoBERTa (trained from scratch)
- **Architecture**: RobertaForMaskedLM
- **Model Type**: Masked Language Model for antibody sequences

### Model Specifications
- **Hidden Size**: 768
- **Number of Layers**: 12
- **Number of Attention Heads**: 12
- **Intermediate Size**: 3072
- **Max Position Embeddings**: 192 (VH), 145 (VL)
- **Vocabulary Size**: 25 tokens
- **Model Size**: ~164 MB per model

### Available Models
- **VH Model**: `hemantn/roberta-base-humAb-vh` - For Variable Heavy chains
- **VL Model**: `hemantn/roberta-base-humAb-vl` - For Variable Light chains



## Citation

If you use AnthroAb in your research, please cite:

```bibtex
@misc{anthroab,
  author = {Hemant N},
  title = {AnthroAb: Human Antibody Language Model for Humanization},
  year = {2024},
  publisher = {Hugging Face},
  url = {https://huggingface.co/hemantn/roberta-base-humAb-vh}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

**Note**: This codebase and API design are adopted from the [Sapiens](https://github.com/Merck/Sapiens) model by Merck.AnthroAb maintains the same interface and functionality as Sapiens but utilizes a RoBERTa-base model trained on human antibody sequences from the OAS database (up to year 2025) for antibody humanization.

### Original Sapiens Citation
> David Prihoda, Jad Maamary, Andrew Waight, Veronica Juan, Laurence Fayadat-Dilman, Daniel Svozil & Danny A. Bitton (2022) 
> BioPhi: A platform for antibody design, humanization, and humanness evaluation based on natural antibody repertoires and deep learning, mAbs, 14:1, DOI: https://doi.org/10.1080/19420862.2021.2020203

## Related Projects

- **[Sapiens](https://github.com/Merck/Sapiens)**: Original antibody language model by Merck (this codebase is based on Sapiens)
- **[BioPhi](https://github.com/Merck/BioPhi)**: Antibody design and humanization platform
- **[OAS](https://opig.stats.ox.ac.uk/webapps/oas/)**: Observed Antibody Space database

## Support

For questions, issues, or contributions, please open an issue on the GitHub repository. 