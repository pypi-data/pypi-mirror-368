#!/usr/bin/env python3
"""
Plot redshift distribution per object type for NGSF data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def plot_redshift_by_type(csv_file: str, output_dir: str = "plots"):
    """Plot redshift distribution per object type."""
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Load data
    print("Loading NGSF data...")
    df = pd.read_csv(csv_file)
    
    # Filter for entries with both redshift and object_type
    valid_data = df[df['redshift'].notna() & df['object_type'].notna()].copy()
    
    print(f"Total entries with redshift and object_type: {len(valid_data)}")
    print(f"Unique object types: {valid_data['object_type'].nunique()}")
    
    # Get top object types by count
    top_types = valid_data['object_type'].value_counts().head(15)
    print(f"\nTop 15 object types:")
    for obj_type, count in top_types.items():
        print(f"  {obj_type}: {count} entries")
    
    # Filter for top types only
    top_data = valid_data[valid_data['object_type'].isin(top_types.index)]
    
    # Set up the plot
    plt.figure(figsize=(16, 12))
    
    # Create subplots
    fig, axes = plt.subplots(3, 5, figsize=(20, 12))
    axes = axes.flatten()
    
    # Plot each object type
    for i, (obj_type, count) in enumerate(top_types.items()):
        if i >= len(axes):
            break
            
        ax = axes[i]
        type_data = top_data[top_data['object_type'] == obj_type]['redshift']
        
        # Create histogram
        ax.hist(type_data, bins=20, alpha=0.7, edgecolor='black', linewidth=0.5)
        ax.set_title(f'{obj_type}\n({count} entries)', fontsize=10)
        ax.set_xlabel('Redshift')
        ax.set_ylabel('Count')
        
        # Add statistics
        mean_z = type_data.mean()
        median_z = type_data.median()
        ax.axvline(mean_z, color='red', linestyle='--', alpha=0.8, label=f'Mean: {mean_z:.3f}')
        ax.axvline(median_z, color='orange', linestyle='--', alpha=0.8, label=f'Median: {median_z:.3f}')
        ax.legend(fontsize=8)
        
        # Set reasonable x limits
        if len(type_data) > 0:
            ax.set_xlim(0, min(type_data.max() * 1.1, 0.5))  # Cap at 0.5 for readability
    
    # Remove empty subplots
    for i in range(len(top_types), len(axes)):
        fig.delaxes(axes[i])
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/redshift_by_object_type_histograms.png', dpi=300, bbox_inches='tight')
    print(f"\nSaved histogram plot to: {output_dir}/redshift_by_object_type_histograms.png")
    
    # Create a box plot
    plt.figure(figsize=(16, 8))
    
    # Prepare data for box plot (limit to top 10 types for readability)
    top_10_types = top_types.head(10)
    box_data = top_data[top_data['object_type'].isin(top_10_types.index)]
    
    # Create box plot
    sns.boxplot(data=box_data, x='object_type', y='redshift', ax=plt.gca())
    plt.xticks(rotation=45, ha='right')
    plt.title('Redshift Distribution by Object Type (Box Plot)', fontsize=14, pad=20)
    plt.xlabel('Object Type')
    plt.ylabel('Redshift')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/redshift_by_object_type_boxplot.png', dpi=300, bbox_inches='tight')
    print(f"Saved box plot to: {output_dir}/redshift_by_object_type_boxplot.png")
    
    # Create violin plot
    plt.figure(figsize=(16, 8))
    sns.violinplot(data=box_data, x='object_type', y='redshift', ax=plt.gca())
    plt.xticks(rotation=45, ha='right')
    plt.title('Redshift Distribution by Object Type (Violin Plot)', fontsize=14, pad=20)
    plt.xlabel('Object Type')
    plt.ylabel('Redshift')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/redshift_by_object_type_violin.png', dpi=300, bbox_inches='tight')
    print(f"Saved violin plot to: {output_dir}/redshift_by_object_type_violin.png")
    
    # Create summary statistics table
    print("\n=== REDSHIFT STATISTICS BY OBJECT TYPE ===")
    stats = []
    for obj_type in top_10_types.index:
        type_data = top_data[top_data['object_type'] == obj_type]['redshift']
        if len(type_data) > 0:
            stats.append({
                'Object Type': obj_type,
                'Count': len(type_data),
                'Mean': type_data.mean(),
                'Median': type_data.median(),
                'Std': type_data.std(),
                'Min': type_data.min(),
                'Max': type_data.max(),
                'Q25': type_data.quantile(0.25),
                'Q75': type_data.quantile(0.75)
            })
    
    stats_df = pd.DataFrame(stats)
    stats_df = stats_df.sort_values('Count', ascending=False)
    
    # Save statistics to CSV
    stats_df.to_csv(f'{output_dir}/redshift_statistics_by_type.csv', index=False)
    print(f"Saved statistics to: {output_dir}/redshift_statistics_by_type.csv")
    
    # Print summary
    print("\nTop 10 Object Types - Redshift Statistics:")
    print(stats_df.to_string(index=False, float_format='%.4f'))
    
    # Create overall redshift distribution
    plt.figure(figsize=(12, 8))
    
    # Main histogram
    plt.subplot(2, 2, 1)
    plt.hist(valid_data['redshift'], bins=50, alpha=0.7, edgecolor='black', linewidth=0.5)
    plt.title('Overall Redshift Distribution')
    plt.xlabel('Redshift')
    plt.ylabel('Count')
    
    # Log scale version
    plt.subplot(2, 2, 2)
    plt.hist(valid_data['redshift'], bins=50, alpha=0.7, edgecolor='black', linewidth=0.5)
    plt.yscale('log')
    plt.title('Overall Redshift Distribution (Log Scale)')
    plt.xlabel('Redshift')
    plt.ylabel('Count (log)')
    
    # Cumulative distribution
    plt.subplot(2, 2, 3)
    sorted_redshifts = np.sort(valid_data['redshift'])
    cumulative = np.arange(1, len(sorted_redshifts) + 1) / len(sorted_redshifts)
    plt.plot(sorted_redshifts, cumulative)
    plt.title('Cumulative Redshift Distribution')
    plt.xlabel('Redshift')
    plt.ylabel('Cumulative Fraction')
    plt.grid(True, alpha=0.3)
    
    # Redshift vs object type count
    plt.subplot(2, 2, 4)
    type_counts = valid_data['object_type'].value_counts().head(10)
    plt.bar(range(len(type_counts)), type_counts.values)
    plt.xticks(range(len(type_counts)), type_counts.index, rotation=45, ha='right')
    plt.title('Object Type Counts')
    plt.xlabel('Object Type')
    plt.ylabel('Count')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/redshift_overview.png', dpi=300, bbox_inches='tight')
    print(f"Saved overview plot to: {output_dir}/redshift_overview.png")
    
    print(f"\nAll plots saved to: {output_dir}/")
    print(f"Total entries analyzed: {len(valid_data)}")
    print(f"Redshift range: {valid_data['redshift'].min():.4f} to {valid_data['redshift'].max():.4f}")
    print(f"Mean redshift: {valid_data['redshift'].mean():.4f}")
    print(f"Median redshift: {valid_data['redshift'].median():.4f}")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Plot redshift distribution by object type")
    parser.add_argument("--metadata", default="ngsf_tns_crossmatching.csv",
                       help="NGSF metadata CSV file")
    parser.add_argument("--output", default="plots",
                       help="Output directory for plots")
    
    args = parser.parse_args()
    
    plot_redshift_by_type(args.metadata, args.output)

if __name__ == "__main__":
    main() 