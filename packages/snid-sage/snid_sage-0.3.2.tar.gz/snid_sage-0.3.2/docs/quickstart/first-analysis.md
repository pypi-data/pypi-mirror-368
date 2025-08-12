# Your First Analysis with SNID SAGE

Welcome to SNID SAGE! This guide will walk you through your first supernova spectrum analysis in just 5 minutes using the GUI interface.

## What You'll Learn

- How to load and analyze a spectrum
- Choosing the best cluster when multiple options exist
- Understanding basic results
- Simple visualization
- Next steps for deeper exploration

## Get Sample Data

You'll need a supernova spectrum to follow along. We recommend SN 2024ggi:

1. **Download**: [tns_2024ggi.dat from TNS](https://www.wis-tns.org/object/2024ggi)
2. **Save**: Create a `data/` folder and save the file there
3. **Note**: Look for the ASCII spectrum file (ending in `.dat`) in the "Spectra" section

## Step-by-Step Analysis

### Step 1: Launch SNID SAGE
```bash
snid-sage
```

### Step 2: Load Your Spectrum
1. Click the **"Load Spectrum"** button (grey button at top)
2. Navigate to your `data/` folder
3. Select `tns_2024ggi.dat`
4. The spectrum appears in the plot area

### Step 3: Preprocess Your Data
1. Click **"Preprocessing"** button (amber - now enabled)
2. Choose **"Quick SNID Preprocessing"** (automatic)
3. Review the cleaned spectrum

### Step 4: Run Analysis
1. Click **"SNID Analysis"** button (magenta - now enabled)
2. Wait 10-30 seconds for analysis to complete
3. Results appear automatically

### Step 5: Choose Your Cluster (If Available)
If SNID SAGE finds multiple viable clusters, a **Cluster Selection Dialog** will appear:

**🎯 What You'll See:**
- **3D Interactive Plot**: Shows all clusters in redshift vs type vs correlation space
- **Cluster Dropdown**: Click "▼ Select Cluster" in top-left to see all options
- **Top Matches Panel**: Right side shows spectrum overlays for the selected cluster
- **Automatic Selection**: Best cluster is pre-selected (marked with ⭐ BEST)

**🔍 How to Choose:**
- **Hover** over clusters to highlight them
- **Click** on any cluster to select it
- **Use dropdown** to see all clusters with their types and redshifts
- **Review matches** in the right panel to see template quality
- **Click "Confirm Selection"** when satisfied

**💡 Pro Tips:**
- **Best cluster is usually correct** - the automatic selection is reliable
- **Check the matches panel** - better template overlays indicate better classification
- **Close dialog** to use automatic selection if unsure
- **Multiple clusters** often indicate ambiguous cases (e.g., II vs TDE)

## Understanding Your Results

The analysis provides a clear classification:

**🎯 FINAL CLASSIFICATION:**
- **Type**: Main supernova type (e.g., II, Ia, Ib, Ic)
- **Quality**: High/Medium/Low confidence level
- **Subtype**: Detailed classification (e.g., IIn, IIP, norm)

**📏 MEASUREMENTS:**
- **Redshift**: Determined redshift with uncertainty
- **Age**: Days from maximum light with uncertainty

**🏆 TEMPLATE MATCHES:**
A ranked list of best matching templates showing:
- Template name and type
- RLAP-Cos score (correlation quality)
- Individual redshift and age estimates

## Basic Visualization

- **Zoom**: Mouse wheel or box selection
- **Pan**: Click and drag
- **Reset View**: Double-click
- **Toggle Views**: Switch between flux and flattened views

## Quick Tips

- **Keyboard Shortcuts**: 
  - `Ctrl+O` - Load spectrum
  - `Ctrl+Enter` - Quick preprocessing + analysis
- **Button Colors**: Grey → Amber → Magenta → Purple (workflow progression)
- **Status Bar**: Check for progress updates and messages

## CLI Analysis (Alternative Method)

You can also analyze the same spectrum using the command line interface, which provides the same functionality as the GUI with default settings.

### Basic CLI Command
```bash
# Analyze the same spectrum using CLI
snid data/tns_2024ggi.dat --output-dir results/

# Or with explicit templates directory
snid identify data/tns_2024ggi.dat templates/ --output-dir results/
```

### What This Does
The CLI command performs the **exact same steps** as the GUI:
1. **Automatic preprocessing** - Same default settings as GUI
2. **Template matching** - Uses all available templates
3. **GMM clustering** - Automatic cluster selection (no user dialog)
4. **Results generation** - Same output format as GUI

### CLI Output
The command produces the same comprehensive results:

**🎯 FINAL CLASSIFICATION:**
- **Type**: Main supernova type (e.g., II, Ia, Ib, Ic)
- **Quality**: High/Medium/Low confidence level
- **Subtype**: Detailed classification (e.g., IIn, IIP, norm)

**📏 MEASUREMENTS:**
- **Redshift**: Determined redshift with uncertainty
- **Age**: Days from maximum light with uncertainty

**🏆 TEMPLATE MATCHES:**
- Ranked list of best matching templates
- RLAP-Cos scores and individual estimates

### CLI Options

**Processing Modes:**
```bash
# Minimal mode - main result file only
snid data/tns_2024ggi.dat --output-dir results/ --minimal

# Complete mode - all outputs + plots
snid data/tns_2024ggi.dat --output-dir results/ --complete

# Default mode - balanced outputs 
snid data/tns_2024ggi.dat --output-dir results/
```

**Preprocessing Options:**
```bash
# With smoothing
snid data/tns_2024ggi.dat --output-dir results/ --savgol-window 11 --savgol-order 3

# Remove telluric features
snid data/tns_2024ggi.dat --output-dir results/ --aband-remove --skyclip
```

**Analysis Options:**
```bash
# Custom redshift range
snid data/tns_2024ggi.dat --output-dir results/ --zmin 0.0 --zmax 0.1

# Force specific redshift
snid data/tns_2024ggi.dat --output-dir results/ --forced-redshift 0.02435

# Filter by type
snid data/tns_2024ggi.dat --output-dir results/ --type-filter Ia II
```

### Key Differences from GUI

| Feature | GUI | CLI |
|---------|-----|-----|
| **Cluster Selection** | Interactive dialog | Automatic selection |
| **Progress Display** | Real-time progress bar | Progress bar + status |
| **Visualization** | Interactive plots | Saved plot files |
| **User Control** | Step-by-step workflow | Single command |
| **Output** | Display + files | Files only |

### CLI Advantages
- **Automation** - Perfect for scripts and batch processing
- **Consistency** - Same results every time
- **Speed** - No interactive delays
- **Server-friendly** - No GUI required
- **Auto-discovery** - Automatically finds templates directory

## Next Steps

Now that you've completed your first analysis, explore:

- **[GUI Complete Guide](../gui/interface-overview.md)** - All interface features
- **[Understanding Results](../tutorials/basic-analysis.md)** - Detailed result interpretation
- **[CLI Reference](../cli/command-reference.md)** - Command-line interface
- **[AI Features](../ai/overview.md)** - AI-powered analysis

## Need Help?

- **Buttons disabled?** Follow the workflow: Load → Preprocess → Analyze
- **Poor results?** Check signal-to-noise and wavelength coverage
- **More help**: See [FAQ](../reference/faq.md) or [Troubleshooting](../reference/troubleshooting.md)

## Congratulations!

You've successfully completed your first SNID SAGE analysis! You can now:
- Load and analyze supernova spectra
- Interpret basic classification results
- Use the GUI interface effectively
- Generate basic visualizations

Ready for more? Check out our [tutorials](../tutorials/) for advanced features and techniques. 