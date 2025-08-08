# SNID SAGE Documentation Navigation Guide

A comprehensive guide to navigating the SNID SAGE documentation, organized from quick access to in-depth technical details.

## Quick Navigation by User Type

### New Users - Start Here
1. **[Installation Guide](installation/installation.md)** → Get SNID SAGE running
2. **[First Analysis Tutorial](quickstart/first-analysis.md)** → Your first spectrum in 5 minutes
3. **[GUI Interface Overview](gui/interface-overview.md)** → Learn the interface
4. **[Basic Analysis Tutorial](tutorials/basic-analysis.md)** → Complete walkthrough
5. **[FAQ](reference/faq.md)** → Common questions answered

### Researchers & Scientists
1. **[Classification Guide](tutorials/classification.md)** → Understanding supernova types
2. **[Advanced Analysis](tutorials/advanced-analysis.md)** → Complex analysis techniques
3. **[AI Features](ai/overview.md)** → AI-powered insights
4. **[Publication Plots](tutorials/publication-ready-plots.md)** → Manuscript-ready figures
5. **[Template Library](data/template-library.md)** → Template details and management

### Power Users & Developers
1. **[CLI Reference](cli/command-reference.md)** → Complete command documentation
2. **[Batch Processing](cli/batch-processing.md)** → Automated workflows
3. **[API Reference (Programming)](reference/api-reference.md)** → Programming interface
4. **[Custom Templates](data/custom-templates.md)** → Creating templates
5. **[Contributing Guide](dev/contributing.md)** → Development guidelines

### Students & Educators
1. **[Basic Tutorial](tutorials/basic-analysis.md)** → Step-by-step learning
2. **[Supported Formats](data/supported-formats.md)** → Data preparation
3. **[Classification Tutorial](tutorials/classification.md)** → Understanding types
4. **[Plotting Guide](tutorials/plotting-visualization.md)** → Creating visualizations
5. **[Troubleshooting](reference/troubleshooting.md)** → Problem solving

## Documentation Structure Overview

```
SNID SAGE Documentation
├── Getting Started
│   ├── Installation
│   ├── Quick Start
│   └── First Analysis
├── User Interfaces
│   ├── GUI Manual
│   ├── CLI Reference
│   └── Configuration
├── Data & Templates
│   ├── File Formats
│   ├── Template Library
│   ├── Custom Templates
│   └── Data Preparation
├── Tutorials
│   ├── Basic Analysis
│   ├── Advanced Techniques
│   ├── AI Integration
│   └── Workflows
├── AI Features
│   ├── Overview
│   ├── Setup
│   └── Analysis Types
├── Reference
│   ├── API Documentation
│   ├── Configuration
│   ├── Troubleshooting
│   └── FAQ
└── Development
    ├── Contributing
    ├── Architecture
    └── Plugin System
```

## Learning Paths

### Path 1: Basic User Journey 

**Documentation Flow:**
1. [Installation](installation/installation.md) → [Quick Start](quickstart/first-analysis.md)
2. [GUI Overview](gui/interface-overview.md) → [Basic Tutorial](tutorials/basic-analysis.md)
3. [Understanding Results](tutorials/basic-analysis.md#understanding-results)
4. [Plotting Guide](tutorials/plotting-visualization.md)
5. [Export Options](tutorials/basic-analysis.md#saving-results)

### Path 2: Advanced Analysis 

**Documentation Flow:**
1. [Advanced Analysis](tutorials/advanced-analysis.md)
2. [Data Preparation](data/data-preparation.md)
3. [Template Management](tutorials/template-management.md)
4. [Configuration Guide](tutorials/configuration-guide.md)
5. [AI Features](ai/overview.md) → [Analysis Types](ai/analysis-types.md)
6. [Publication Plots](tutorials/publication-ready-plots.md)

### Path 3: Automation & Development 

**Documentation Flow:**
1. [CLI Reference](cli/command-reference.md)
2. [Batch Processing](cli/batch-processing.md) → [Optimization](cli/batch-optimization.md)
3. [API Reference (Programming)](reference/api-reference.md)
4. [Advanced Workflows](tutorials/advanced-workflows.md)
5. [Custom Templates](data/custom-templates.md)
6. [Contributing](dev/contributing.md)

## Topic-Based Navigation

### Data Management
- **Input**: [Supported Formats](data/supported-formats.md) → [Data Preparation](data/data-preparation.md)
- **Templates**: [Template Library](data/template-library.md) → [Custom Templates](data/custom-templates.md)
- **Output**: [Results Format](reference/api-reference.md#results) → [Export Options](cli/command-reference.md#output-files)

### Analysis Techniques
- **Basic**: [First Analysis](quickstart/first-analysis.md) → [Basic Tutorial](tutorials/basic-analysis.md)
- **Advanced**: [Advanced Analysis](tutorials/advanced-analysis.md) → [Performance Optimization](reference/performance-tuning.md)
- **Specialized**: [Wind Velocity](gui/interface-overview.md#wind-velocity) → [FWHM Analysis](gui/interface-overview.md#fwhm)

### AI Integration
- **Setup**: [AI Overview](ai/overview.md) → [OpenRouter Setup](ai/openrouter-setup.md)
- **Usage**: [AI Tutorial](tutorials/ai-assisted-analysis.md) → [Analysis Types](ai/analysis-types.md)
- **Advanced**: [Custom Prompts](ai/overview.md#custom-prompts) → [API Integration](ai/overview.md#api-integration)

### Visualization
- **Basics**: [Plotting Tutorial](tutorials/plotting-visualization.md)
- **Interactive**: [GUI Plot Tools](gui/interface-overview.md#interactive-features)
- **Publication**: [Publication Plots](tutorials/publication-ready-plots.md)
- **Customization**: [Plot Themes](gui/interface-overview.md#theme-system)

### Configuration
- **GUI**: [Settings Dialog](gui/interface-overview.md#configuration-dialogs)
- **CLI**: [Config Command](cli/command-reference.md#config)
- **Files**: [Configuration Guide](tutorials/configuration-guide.md)
- **Advanced**: [Performance Tuning](reference/performance-tuning.md)

## Deep Dive Topics

### Understanding SNID Algorithm
1. **Theory**: [SNID Overview](index.md) → [Cross-Correlation](tutorials/advanced-analysis.md#correlation)
2. **Implementation**: [API Reference (Programming)](reference/api-reference.md) → [Source Code](dev/contributing.md)
3. **Optimization**: [Performance Guide](reference/performance-tuning.md)

### Supernova Classification
1. **Types**: [Classification Guide](tutorials/classification.md)
2. **Templates**: [Template Library](data/template-library.md)
3. **Practice**: [Basic Tutorial](tutorials/basic-analysis.md) → [Advanced Analysis](tutorials/advanced-analysis.md)

### Workflow Automation
1. **CLI**: [Command Reference](cli/command-reference.md)
2. **Batch**: [Batch Processing](cli/batch-processing.md)
3. **Scripts**: [Advanced Workflows](tutorials/advanced-workflows.md)
4. **API**: [Programming Interface](reference/api-reference.md)

## Reference Quick Links

### Commands & Functions
- **CLI Commands**: [identify](cli/command-reference.md#identify) | [batch](cli/command-reference.md#batch) | [template](cli/command-reference.md#template) | [config](cli/command-reference.md#config)
- **Core Functions**: [run_snid](reference/api-reference.md#run_snid) | [preprocess_spectrum](reference/api-reference.md#preprocess) | [run_snid_analysis](reference/api-reference.md#analysis)
- **I/O Functions**: [read_spectrum](reference/api-reference.md#io) | [load_templates](reference/api-reference.md#templates) | [write_result](reference/api-reference.md#output)

### Configuration Options
- **Analysis**: [Parameters](tutorials/configuration-guide.md#analysis) | [Templates](tutorials/configuration-guide.md#templates)
- **Preprocessing**: [Options](tutorials/configuration-guide.md#preprocessing) | [Filters](data/data-preparation.md#preprocessing)
- **Output**: [Formats](cli/command-reference.md#output-files) | [Plots](tutorials/plotting-visualization.md)

### Troubleshooting
- **Common Issues**: [FAQ](reference/faq.md) | [Troubleshooting](reference/troubleshooting.md)
- **Error Messages**: [Error Codes](reference/troubleshooting.md#error-messages)
- **Performance**: [Optimization](reference/performance-tuning.md)

## Task-Based Navigation

### "I want to..."

#### Analyze a spectrum
- Single spectrum: [Quick Start](quickstart/first-analysis.md) or [CLI identify](cli/command-reference.md#identify)
- Multiple spectra: [Batch Processing](cli/batch-processing.md)
- With known redshift: [Forced Redshift](tutorials/advanced-analysis.md#forced-redshift)

#### Improve results
- Better preprocessing: [Data Preparation](data/data-preparation.md)
- Filter templates: [Template Selection](tutorials/template-management.md)
- Tune parameters: [Configuration Guide](tutorials/configuration-guide.md)

#### Create visualizations
- Basic plots: [Plotting Tutorial](tutorials/plotting-visualization.md)
- Publication figures: [Publication Plots](tutorials/publication-ready-plots.md)
- Custom themes: [Plot Customization](gui/interface-overview.md#theme-system)

#### Use AI features
- Setup AI: [AI Overview](ai/overview.md) → [OpenRouter Setup](ai/openrouter-setup.md)
- Get insights: [AI Analysis](tutorials/ai-assisted-analysis.md)
- Interactive chat: [Chat Interface](ai/overview.md#interactive-chat-interface)

#### Automate workflows
- Batch analysis: [Batch Processing](cli/batch-processing.md)
- Custom scripts: [API Usage](reference/api-reference.md)
- Pipeline integration: [Advanced Workflows](tutorials/advanced-workflows.md)

#### Contribute or extend
- Report issues: [GitHub Issues](https://github.com/FiorenSt/SNID-SAGE/issues)
- Add templates: [Custom Templates](data/custom-templates.md)
- Contribute code: [Contributing Guide](dev/contributing.md)

## Documentation Map

### Core Documentation (Start Here)
1. **[Main Index](index.md)** - Documentation home
2. **[Installation](installation/installation.md)** - Setup instructions
3. **[Quick Start](quickstart/first-analysis.md)** - First steps

### User Guides (Learn Features)
4. **[GUI Manual](gui/interface-overview.md)** - Graphical interface
5. **[CLI Reference](cli/command-reference.md)** - Command line
6. **[Tutorials](tutorials/)** - Step-by-step guides

### Technical Reference (Deep Details)
7. **[API Documentation](reference/api-reference.md)** - Programming
8. **[Data Formats](data/supported-formats.md)** - File specifications
9. **[Template System](data/template-library.md)** - Template details

### Advanced Topics (Expert Users)
10. **[AI Integration](ai/overview.md)** - AI features
11. **[Performance](reference/performance-tuning.md)** - Optimization
12. **[Development](dev/contributing.md)** - Contributing

## Cross-References

Each documentation page includes:
- **Prerequisites**: What to read first
- **Next Steps**: Where to go next
- **Related Topics**: Similar content
- **See Also**: Additional resources

Example from [Basic Tutorial](tutorials/basic-analysis.md):
```yaml
Prerequisites:
  - Installation complete
  - GUI or CLI accessible
  
Next Steps:
  - Advanced Analysis
  - AI Features
  - Batch Processing
  
Related Topics:
  - Classification Guide
  - Template Management
  - Plotting Tutorial
```

## Tips for Using Documentation

### Search Strategies
1. Use browser search (Ctrl+F) within pages
2. Check the FAQ first for common questions
3. Look for code examples in tutorials
4. Reference sections have detailed specifications

### Learning Approach
1. Start with tutorials for hands-on learning
2. Use reference docs for specific details
3. Check examples in each section
4. Follow learning paths for structured progress

### Getting Help
1. **Documentation**: You are here!
2. **FAQ**: [Frequently Asked Questions](reference/faq.md)
3. **Troubleshooting**: [Problem Solving](reference/troubleshooting.md)
4. **Community**: [GitHub Discussions](https://github.com/FiorenSt/SNID-SAGE/discussions)

**Remember**: Documentation is organized from **general to specific** and **simple to complex**. Start with overview pages and drill down to details as needed. 