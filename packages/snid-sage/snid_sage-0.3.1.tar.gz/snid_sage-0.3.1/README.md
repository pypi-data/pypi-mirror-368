# SNID SAGE - Advanced Supernova Spectral Analysis

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

**SNID SAGE** (SuperNova IDentification – Spectral Analysis and Guided Exploration) is your go-to tool for analyzing supernova spectra. It combines an intuitive PySide6/Qt graphical interface with the original SNID (Blondin & Tonry 2007) cross-correlation techniques, enhanced with modern clustering for classification choice, high-performance plotting via `pyqtgraph`, and LLM-powered analysis summaries and interactive chat assistance.

---

![SNID SAGE GUI](snid_sage/images/Screenshot.png)
*SNID SAGE main GUI: intuitive workflow, interactive plotting, and advanced analysis tools.*

---

## Quick Installation (v0.3.0)

### Option 1: Install from PyPI (Recommended)

The easiest way to install SNID SAGE is directly from PyPI:

```bash
pip install snid-sage
```

 

### Option 2: Virtual Environment (Recommended for Development)

We recommend using a virtual environment to avoid conflicts with other Python packages. This ensures a clean, isolated installation.

#### Using venv (Python's built-in virtual environment)
```bash
# Create virtual environment
python -m venv snid_env

# Activate environment
# Windows:
snid_env\Scripts\activate
# macOS/Linux:
source snid_env/bin/activate

# Install SNID SAGE
pip install snid-sage
 
```

#### Using conda
```bash
# Create conda environment
conda create -n snid_sage python=3.10
conda activate snid_sage

# Install SNID SAGE
pip install snid-sage
 
```

### Option 3: Development Installation

For development or testing the latest features:

```bash
# Install from Test PyPI (development versions)
pip install -i https://test.pypi.org/simple/ snid-sage

# Or install from source
git clone https://github.com/FiorenSt/SNID-SAGE.git
cd SNID-SAGE
pip install -e .
```

**Note:** If you choose global installation, we recommend using `pip install --user` to install in your user directory rather than system-wide.



## Getting Started

### Launch the GUI (Recommended)
```bash
# Using installed entry point
snid-gui
# or
snid-sage
```

 

### Use the CLI (For automation)
```bash
# Single spectrum analysis (templates auto-discovered). By default saves summary (.output) and plots
snid data/sn2003jo.dat -o results/

# Single spectrum with explicit templates
snid identify data/sn2003jo.dat templates/ -o results/

# Batch processing (default saves per-object summary and plots)
snid batch "data/*.dat" templates/ -o results/

# Minimal outputs (summary only, no plots)
snid identify data/sn2003jo.dat -o results/ --minimal

# Complete outputs (summary, plots, and all additional data files)
snid identify data/sn2003jo.dat -o results/ --complete

# Disable plots explicitly (default is to generate plots)
snid identify data/sn2003jo.dat -o results/ --no-plots
```



## Documentation & Support

- **[Complete Documentation](https://fiorenst.github.io/SNID-SAGE/)** - Comprehensive guides and tutorials
- **[Quick Start Guide](https://fiorenst.github.io/SNID-SAGE/quickstart/first-analysis/)** - Your first analysis in 5 minutes
- **[GUI Manual](https://fiorenst.github.io/SNID-SAGE/gui/interface-overview/)** - Complete interface guide
- **[CLI Reference](https://fiorenst.github.io/SNID-SAGE/cli/command-reference/)** - All commands and options
- **[AI Integration](https://fiorenst.github.io/SNID-SAGE/ai/overview/)** - Setting up AI analysis
- **[Troubleshooting](https://fiorenst.github.io/SNID-SAGE/reference/troubleshooting/)** - Common issues and solutions
- **[FAQ](https://fiorenst.github.io/SNID-SAGE/reference/faq/)** - Frequently asked questions

## Supported Data Formats

- **FITS files** (.fits, .fit)
- **ASCII tables** (.dat, .txt, .ascii, .asci, .flm)
- **Space-separated values** with flexible column detection
- **Custom formats** with configurable parsers

## Research & Citation

If you use SNID SAGE in your research, please cite:

```bibtex
@software{snid_sage_2025,
  title={SNID SAGE: A Modern Framework for Interactive Supernova
         Classification and Spectral Analysis},
  author={F. Stoppa},
  year={In Prep, 2025},
  url={https://github.com/FiorenSt/SNID-SAGE}
}
```

## Community & Support

- **[Report Bug](https://github.com/FiorenSt/SNID-SAGE/issues)** - Found a bug?
- **[Request Feature](https://github.com/FiorenSt/SNID-SAGE/issues)** - Want a new feature?
- **[Discussions](https://github.com/FiorenSt/SNID-SAGE/discussions)** - Questions and community chat
- **[Email Support](mailto:fiorenzo.stoppa@physics.ox.ac.uk)** - Direct contact

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with care for the astronomical community**

[Documentation](https://fiorenst.github.io/SNID-SAGE/) • [Report Bug](https://github.com/FiorenSt/SNID-SAGE/issues) • [Request Feature](https://github.com/FiorenSt/SNID-SAGE/issues) • [Discussions](https://github.com/FiorenSt/SNID-SAGE/discussions)

</div>
