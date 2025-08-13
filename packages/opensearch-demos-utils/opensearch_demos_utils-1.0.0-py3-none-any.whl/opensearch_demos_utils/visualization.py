"""
Visualization utilities for OpenSearch demos optimized for Google Colab.

This module provides common plotting functions for visualizing search results,
aggregations, and cluster metrics in OpenSearch demo notebooks, specifically
optimized for Google Colab rendering.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
import warnings

# Configure matplotlib for Colab
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 100
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'

# Set default style for consistent visualizations
plt.style.use('default')
sns.set_palette("husl")

# Suppress warnings for cleaner output in Colab
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

def _ensure_colab_display():
    """Ensure proper display configuration for Google Colab."""
    try:
        # Check if we're in Colab
        import google.colab
        # Configure for Colab inline display
        from IPython.display import display
        plt.rcParams['figure.figsize'] = (12, 8)
        return True
    except ImportError:
        # Not in Colab, use standard configuration
        return False

# Initialize Colab display if available
COLAB_MODE = _ensure_colab_display()


def plot_search_results(search_results: Dict[str, Any], 
                       title: str = "Search Results Distribution",
                       max_results: int = 20,
                       show_scores: bool = True,
                       figsize: tuple = (12, 8)) -> None:
    """
    Visualize search result distributions including scores and document counts.
    Optimized for Google Colab display.
    
    Args:
        search_results: OpenSearch response dictionary containing hits
        title: Title for the plot
        max_results: Maximum number of results to display
        show_scores: Whether to show relevance scores
        figsize: Figure size as (width, height)
    """
    if not search_results or 'hits' not in search_results:
        print("❌ No search results to visualize")
        return
    
    hits = search_results['hits']['hits'][:max_results]
    
    if not hits:
        print("❌ No hits found in search results")
        return
    
    # Extract data for visualization
    doc_ids = [hit.get('_id', f'doc_{i}')[:10] + '...' if len(hit.get('_id', f'doc_{i}')) > 10 
               else hit.get('_id', f'doc_{i}') for i, hit in enumerate(hits)]
    scores = [hit.get('_score', 0) for hit in hits]
    sources = [hit.get('_source', {}) for hit in hits]
    
    # Create subplots with better spacing for Colab
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
    
    # Plot 1: Relevance scores
    if show_scores and any(score > 0 for score in scores):
        bars = axes[0, 0].bar(range(len(scores)), scores, color='skyblue', alpha=0.8)
        axes[0, 0].set_title('Relevance Scores by Document', fontsize=12)
        axes[0, 0].set_xlabel('Document Index')
        axes[0, 0].set_ylabel('Score')
        
        # Add value labels on bars for better readability
        for i, (bar, score) in enumerate(zip(bars, scores)):
            if score > 0:
                axes[0, 0].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.01,
                               f'{score:.2f}', ha='center', va='bottom', fontsize=8)
    else:
        axes[0, 0].text(0.5, 0.5, 'No scores available\n(Scores may be disabled)', 
                       ha='center', va='center', transform=axes[0, 0].transAxes,
                       fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        axes[0, 0].set_title('Relevance Scores (Not Available)')
    
    # Plot 2: Score distribution histogram
    if show_scores and any(score > 0 for score in scores):
        n_bins = min(10, len(set(scores)))
        axes[0, 1].hist(scores, bins=n_bins, color='lightgreen', alpha=0.8, edgecolor='black')
        axes[0, 1].set_title('Score Distribution', fontsize=12)
        axes[0, 1].set_xlabel('Score Range')
        axes[0, 1].set_ylabel('Frequency')
    else:
        axes[0, 1].text(0.5, 0.5, 'No scores to distribute', 
                       ha='center', va='center', transform=axes[0, 1].transAxes,
                       fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        axes[0, 1].set_title('Score Distribution (Not Available)')
    
    # Plot 3: Document categories/types if available
    categories = []
    for source in sources:
        if 'category' in source:
            categories.append(source['category'])
        elif 'type' in source:
            categories.append(source['type'])
        elif '_index' in source:
            categories.append(source['_index'])
        else:
            categories.append('Unknown')
    
    if categories and len(set(categories)) > 1:
        category_counts = pd.Series(categories).value_counts()
        colors = plt.cm.Set3(np.linspace(0, 1, len(category_counts)))
        wedges, texts, autotexts = axes[1, 0].pie(category_counts.values, 
                                                  labels=category_counts.index, 
                                                  autopct='%1.1f%%',
                                                  colors=colors,
                                                  startangle=90)
        axes[1, 0].set_title('Document Categories', fontsize=12)
        
        # Improve text readability
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
    else:
        axes[1, 0].text(0.5, 0.5, f'Single category: {categories[0] if categories else "Unknown"}', 
                       ha='center', va='center', transform=axes[1, 0].transAxes,
                       fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
        axes[1, 0].set_title('Document Categories')
    
    # Plot 4: Search statistics
    total_hits = search_results['hits']['total']['value']
    max_score = search_results['hits'].get('max_score', 0)
    
    stats_data = {
        'Total Hits': total_hits,
        'Displayed': len(hits),
        'Max Score': max_score if max_score else 0
    }
    
    colors = ['coral', 'gold', 'lightblue']
    bars = axes[1, 1].bar(stats_data.keys(), stats_data.values(), color=colors, alpha=0.8)
    axes[1, 1].set_title('Search Statistics', fontsize=12)
    axes[1, 1].set_ylabel('Count/Score')
    
    # Add value labels on bars
    for bar, value in zip(bars, stats_data.values()):
        height = bar.get_height()
        axes[1, 1].text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{value:.2f}' if isinstance(value, float) else str(value),
                        ha='center', va='bottom', fontweight='bold')
    
    # Rotate x-axis labels for better readability
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)  # Adjust for suptitle
    plt.show()


def create_aggregation_charts(aggregation_results: Dict[str, Any],
                            chart_type: str = 'auto',
                            title: str = "Aggregation Results",
                            figsize: tuple = (12, 6)) -> None:
    """
    Create charts from OpenSearch aggregation results.
    Optimized for Google Colab display.
    
    Args:
        aggregation_results: OpenSearch aggregation response
        chart_type: Type of chart ('bar', 'pie', 'line', 'auto')
        title: Title for the chart
        figsize: Figure size as (width, height)
    """
    if not aggregation_results:
        print("❌ No aggregation results to visualize")
        return
    
    # Extract aggregation data
    agg_data = []
    
    for agg_name, agg_result in aggregation_results.items():
        if 'buckets' in agg_result:
            # Bucket aggregation
            for bucket in agg_result['buckets']:
                key = bucket.get('key', 'Unknown')
                # Handle date keys
                if isinstance(key, (int, float)) and key > 1000000000000:  # Likely timestamp
                    key = pd.to_datetime(key, unit='ms').strftime('%Y-%m-%d')
                
                agg_data.append({
                    'aggregation': agg_name,
                    'key': str(key),
                    'doc_count': bucket.get('doc_count', 0),
                    'value': bucket.get('doc_count', 0)
                })
        elif 'value' in agg_result:
            # Metric aggregation
            agg_data.append({
                'aggregation': agg_name,
                'key': agg_name,
                'doc_count': 1,
                'value': agg_result['value']
            })
    
    if not agg_data:
        print("❌ No valid aggregation data found")
        return
    
    df = pd.DataFrame(agg_data)
    
    # Determine chart type automatically if needed
    if chart_type == 'auto':
        unique_aggs = df['aggregation'].nunique()
        unique_keys = df['key'].nunique()
        if unique_aggs == 1:
            chart_type = 'pie' if unique_keys <= 8 else 'bar'
        else:
            chart_type = 'bar'
    
    # Create the chart with better styling for Colab
    fig, ax = plt.subplots(figsize=figsize)
    
    if chart_type == 'bar':
        if df['aggregation'].nunique() == 1:
            # Single aggregation
            bars = ax.bar(df['key'], df['value'], color='steelblue', alpha=0.8, edgecolor='navy')
            ax.set_xlabel('Categories', fontsize=12)
            ax.set_ylabel('Count/Value', fontsize=12)
            
            # Add value labels on bars
            for bar, value in zip(bars, df['value']):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       f'{value:.0f}' if value == int(value) else f'{value:.2f}',
                       ha='center', va='bottom', fontweight='bold')
        else:
            # Multiple aggregations
            pivot_df = df.pivot_table(index='key', columns='aggregation', values='value', fill_value=0)
            pivot_df.plot(kind='bar', ax=ax, alpha=0.8, width=0.8)
            ax.set_xlabel('Categories', fontsize=12)
            ax.set_ylabel('Count/Value', fontsize=12)
            ax.legend(title='Aggregations', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.xticks(rotation=45, ha='right')
    
    elif chart_type == 'pie':
        if df['aggregation'].nunique() == 1:
            colors = plt.cm.Set3(np.linspace(0, 1, len(df)))
            wedges, texts, autotexts = ax.pie(df['value'], labels=df['key'], autopct='%1.1f%%',
                                             colors=colors, startangle=90)
            
            # Improve text readability
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        else:
            print("⚠️ Pie chart not suitable for multiple aggregations, using bar chart instead")
            create_aggregation_charts(aggregation_results, 'bar', title, figsize)
            return
    
    elif chart_type == 'line':
        if df['aggregation'].nunique() == 1:
            ax.plot(df['key'], df['value'], marker='o', linewidth=3, markersize=8, color='steelblue')
            ax.set_xlabel('Categories', fontsize=12)
            ax.set_ylabel('Count/Value', fontsize=12)
            ax.grid(True, alpha=0.3)
        else:
            pivot_df = df.pivot_table(index='key', columns='aggregation', values='value', fill_value=0)
            pivot_df.plot(kind='line', ax=ax, marker='o', linewidth=2, markersize=6)
            ax.set_xlabel('Categories', fontsize=12)
            ax.set_ylabel('Count/Value', fontsize=12)
            ax.legend(title='Aggregations', bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(True, alpha=0.3)
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.show()


def display_cluster_metrics(cluster_info: Dict[str, Any],
                          cluster_health: Optional[Dict[str, Any]] = None,
                          cluster_stats: Optional[Dict[str, Any]] = None,
                          figsize: tuple = (15, 10)) -> None:
    """
    Display cluster health and performance metrics.
    Optimized for Google Colab display.
    
    Args:
        cluster_info: Basic cluster information
        cluster_health: Cluster health information (optional)
        cluster_stats: Cluster statistics (optional)
        figsize: Figure size as (width, height)
    """
    # Create figure with better layout for Colab
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle('OpenSearch Cluster Metrics', fontsize=16, fontweight='bold', y=0.98)
    
    # Flatten axes for easier indexing
    axes_flat = axes.flatten()
    plot_idx = 0
    
    # Plot 1: Basic cluster information
    if cluster_info:
        info_lines = []
        for key, value in cluster_info.items():
            if isinstance(value, dict):
                info_lines.append(f"📊 {key.replace('_', ' ').title()}:")
                for sub_key, sub_value in list(value.items())[:3]:  # Limit sub-items
                    info_lines.append(f"   • {sub_key.replace('_', ' ').title()}: {sub_value}")
            else:
                display_value = str(value)[:50] + '...' if len(str(value)) > 50 else str(value)
                info_lines.append(f"📋 {key.replace('_', ' ').title()}: {display_value}")
        
        # Limit to first 12 lines for readability
        display_lines = info_lines[:12]
        if len(info_lines) > 12:
            display_lines.append("   ... (truncated)")
        
        axes_flat[plot_idx].text(0.05, 0.95, '\n'.join(display_lines), 
                                transform=axes_flat[plot_idx].transAxes,
                                verticalalignment='top', fontsize=10, fontfamily='monospace',
                                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.7))
        axes_flat[plot_idx].set_title('Cluster Information', fontsize=12, fontweight='bold')
        axes_flat[plot_idx].axis('off')
        plot_idx += 1
    
    # Plot 2: Cluster health status
    if cluster_health:
        status = cluster_health.get('status', 'unknown').lower()
        health_colors = {'green': '#28a745', 'yellow': '#ffc107', 'red': '#dc3545', 'unknown': '#6c757d'}
        
        # Health status with shard information
        health_metrics = {
            'Active': cluster_health.get('active_shards', 0),
            'Relocating': cluster_health.get('relocating_shards', 0),
            'Initializing': cluster_health.get('initializing_shards', 0),
            'Unassigned': cluster_health.get('unassigned_shards', 0)
        }
        
        # Filter out zero values
        health_metrics = {k: v for k, v in health_metrics.items() if v > 0}
        
        if health_metrics and sum(health_metrics.values()) > 0:
            colors = ['#28a745', '#17a2b8', '#ffc107', '#dc3545'][:len(health_metrics)]
            wedges, texts, autotexts = axes_flat[plot_idx].pie(
                health_metrics.values(), 
                labels=[f"{k} Shards" for k in health_metrics.keys()], 
                autopct='%1.0f',
                colors=colors,
                startangle=90
            )
            
            # Improve text readability
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                
            title_color = health_colors.get(status, '#6c757d')
            axes_flat[plot_idx].set_title(f'Shard Distribution\n(Status: {status.upper()})',
                                         fontsize=12, fontweight='bold', color=title_color)
        else:
            # Show status as text when no shard data
            status_color = health_colors.get(status, '#6c757d')
            axes_flat[plot_idx].text(0.5, 0.5, f'Cluster Status\n{status.upper()}',
                                   ha='center', va='center', 
                                   transform=axes_flat[plot_idx].transAxes,
                                   fontsize=16, fontweight='bold',
                                   color=status_color,
                                   bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.8))
            axes_flat[plot_idx].set_title('Cluster Health', fontsize=12, fontweight='bold')
        
        axes_flat[plot_idx].axis('equal')
        plot_idx += 1
    
    # Plot 3: Basic statistics
    stats_data = {}
    
    if cluster_health:
        stats_data['Nodes'] = cluster_health.get('number_of_nodes', 0)
        stats_data['Data Nodes'] = cluster_health.get('number_of_data_nodes', 0)
    
    if cluster_stats and 'indices' in cluster_stats:
        indices_info = cluster_stats['indices']
        if 'count' in indices_info:
            stats_data['Indices'] = indices_info['count']
        if 'docs' in indices_info and 'count' in indices_info['docs']:
            doc_count = indices_info['docs']['count']
            if doc_count > 1000000:
                stats_data['Docs (M)'] = round(doc_count / 1000000, 1)
            elif doc_count > 1000:
                stats_data['Docs (K)'] = round(doc_count / 1000, 1)
            else:
                stats_data['Documents'] = doc_count
    
    if stats_data:
        colors = plt.cm.viridis(np.linspace(0, 1, len(stats_data)))
        bars = axes_flat[plot_idx].bar(stats_data.keys(), stats_data.values(), 
                                      color=colors, alpha=0.8, edgecolor='black')
        axes_flat[plot_idx].set_title('Cluster Statistics', fontsize=12, fontweight='bold')
        axes_flat[plot_idx].set_ylabel('Count')
        
        # Add value labels on bars
        for bar, value in zip(bars, stats_data.values()):
            height = bar.get_height()
            axes_flat[plot_idx].text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                                    f'{value:.1f}' if isinstance(value, float) else str(value),
                                    ha='center', va='bottom', fontweight='bold')
        
        plt.setp(axes_flat[plot_idx].xaxis.get_majorticklabels(), rotation=45, ha='right')
        plot_idx += 1
    
    # Plot 4: Storage information
    if cluster_stats and 'indices' in cluster_stats and 'store' in cluster_stats['indices']:
        store_info = cluster_stats['indices']['store']
        size_bytes = store_info.get('size_in_bytes', 0)
        
        # Convert to appropriate units
        if size_bytes > 1024**3:  # GB
            size_value = size_bytes / (1024**3)
            size_unit = 'GB'
        elif size_bytes > 1024**2:  # MB
            size_value = size_bytes / (1024**2)
            size_unit = 'MB'
        elif size_bytes > 1024:  # KB
            size_value = size_bytes / 1024
            size_unit = 'KB'
        else:
            size_value = size_bytes
            size_unit = 'Bytes'
        
        # Create a simple storage visualization
        axes_flat[plot_idx].bar(['Storage Used'], [size_value], 
                               color='lightcoral', alpha=0.8, edgecolor='darkred')
        axes_flat[plot_idx].set_title(f'Storage Usage', fontsize=12, fontweight='bold')
        axes_flat[plot_idx].set_ylabel(f'Size ({size_unit})')
        
        # Add value label
        axes_flat[plot_idx].text(0, size_value + size_value*0.01,
                                f'{size_value:.2f} {size_unit}',
                                ha='center', va='bottom', fontweight='bold')
        plot_idx += 1
    
    # Hide unused subplots
    for i in range(plot_idx, len(axes_flat)):
        axes_flat[i].axis('off')
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)  # Adjust for suptitle
    plt.show()


def format_search_response_for_display(search_response: Dict[str, Any], 
                                     max_content_length: int = 100) -> pd.DataFrame:
    """
    Convert OpenSearch response to a pandas DataFrame for easy display in Colab.
    
    Args:
        search_response: OpenSearch search response
        max_content_length: Maximum length for text content display
        
    Returns:
        DataFrame with search results formatted for display
    """
    if not search_response or 'hits' not in search_response:
        return pd.DataFrame()
    
    hits = search_response['hits']['hits']
    data = []
    
    for hit in hits:
        row = {
            'ID': hit.get('_id', 'N/A')[:20] + '...' if len(hit.get('_id', '')) > 20 else hit.get('_id', 'N/A'),
            'Score': f"{hit.get('_score', 0):.3f}" if hit.get('_score') else 'N/A',
            'Index': hit.get('_index', 'N/A'),
        }
        
        # Add source fields with truncation for better display
        source = hit.get('_source', {})
        for key, value in source.items():
            if isinstance(value, str):
                if len(value) > max_content_length:
                    row[key.title()] = value[:max_content_length-3] + '...'
                else:
                    row[key.title()] = value
            elif isinstance(value, (list, dict)):
                row[key.title()] = str(value)[:max_content_length] + '...' if len(str(value)) > max_content_length else str(value)
            else:
                row[key.title()] = value
        
        data.append(row)
    
    df = pd.DataFrame(data)
    
    # Style the DataFrame for better Colab display
    if not df.empty:
        print(f"📊 Showing {len(df)} results out of {search_response['hits']['total']['value']} total hits")
    
    return df


def create_comparison_chart(data1: List[float], data2: List[float],
                          labels: List[str], 
                          title1: str = "Dataset 1", title2: str = "Dataset 2",
                          overall_title: str = "Comparison Chart",
                          figsize: tuple = (12, 5)) -> None:
    """
    Create a side-by-side comparison chart for two datasets.
    Optimized for Google Colab display.
    
    Args:
        data1: First dataset values
        data2: Second dataset values  
        labels: Labels for the data points
        title1: Title for first dataset
        title2: Title for second dataset
        overall_title: Overall chart title
        figsize: Figure size as (width, height)
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    fig.suptitle(overall_title, fontsize=14, fontweight='bold', y=1.02)
    
    # First dataset
    bars1 = ax1.bar(labels, data1, color='skyblue', alpha=0.8, edgecolor='navy')
    ax1.set_title(title1, fontsize=12, fontweight='bold')
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, value in zip(bars1, data1):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{value:.2f}' if isinstance(value, float) else str(value),
                ha='center', va='bottom', fontweight='bold')
    
    # Second dataset
    bars2 = ax2.bar(labels, data2, color='lightcoral', alpha=0.8, edgecolor='darkred')
    ax2.set_title(title2, fontsize=12, fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, value in zip(bars2, data2):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{value:.2f}' if isinstance(value, float) else str(value),
                ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.show()


def create_colab_friendly_plot(data: Dict[str, Any], plot_type: str = 'bar', 
                              title: str = "Data Visualization", **kwargs) -> None:
    """
    Create a Colab-optimized plot with consistent styling.
    
    Args:
        data: Dictionary with data to plot
        plot_type: Type of plot ('bar', 'pie', 'line', 'scatter')
        title: Plot title
        **kwargs: Additional plot parameters
    """
    figsize = kwargs.get('figsize', (10, 6))
    fig, ax = plt.subplots(figsize=figsize)
    
    if plot_type == 'bar':
        bars = ax.bar(data.keys(), data.values(), 
                     color=kwargs.get('color', 'steelblue'), 
                     alpha=kwargs.get('alpha', 0.8))
        
        # Add value labels
        for bar, value in zip(bars, data.values()):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                   f'{value:.2f}' if isinstance(value, float) else str(value),
                   ha='center', va='bottom', fontweight='bold')
    
    elif plot_type == 'pie':
        colors = plt.cm.Set3(np.linspace(0, 1, len(data)))
        wedges, texts, autotexts = ax.pie(data.values(), labels=data.keys(), 
                                         autopct='%1.1f%%', colors=colors, startangle=90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
    
    elif plot_type == 'line':
        ax.plot(list(data.keys()), list(data.values()), 
               marker='o', linewidth=3, markersize=8,
               color=kwargs.get('color', 'steelblue'))
        ax.grid(True, alpha=0.3)
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    if plot_type in ['bar', 'line']:
        plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.show()


def plot_aggregation_results(aggregation_response: Dict[str, Any], 
                           aggregation_name: str = None,
                           chart_type: str = 'auto',
                           title: str = None,
                           figsize: tuple = (12, 6)) -> None:
    """
    Specialized function for plotting aggregation results with Colab optimization.
    
    Args:
        aggregation_response: Full OpenSearch aggregation response
        aggregation_name: Specific aggregation to plot (if None, plots first found)
        chart_type: Type of chart ('bar', 'pie', 'line', 'auto')
        title: Custom title for the chart
        figsize: Figure size as (width, height)
    """
    if not aggregation_response or 'aggregations' not in aggregation_response:
        print("❌ No aggregations found in response")
        return
    
    aggregations = aggregation_response['aggregations']
    
    if aggregation_name:
        if aggregation_name not in aggregations:
            print(f"❌ Aggregation '{aggregation_name}' not found")
            return
        target_agg = {aggregation_name: aggregations[aggregation_name]}
    else:
        # Use first aggregation found
        target_agg = {list(aggregations.keys())[0]: list(aggregations.values())[0]}
    
    if not title:
        title = f"Aggregation Results: {list(target_agg.keys())[0]}"
    
    create_aggregation_charts(target_agg, chart_type, title, figsize)


def create_dashboard_view(search_results: Dict[str, Any] = None,
                         aggregation_results: Dict[str, Any] = None,
                         cluster_info: Dict[str, Any] = None,
                         title: str = "OpenSearch Dashboard",
                         figsize: tuple = (16, 12)) -> None:
    """
    Create a comprehensive dashboard view combining multiple visualizations.
    Optimized for Google Colab display.
    
    Args:
        search_results: OpenSearch search response (optional)
        aggregation_results: OpenSearch aggregation response (optional)
        cluster_info: Cluster information (optional)
        title: Dashboard title
        figsize: Figure size as (width, height)
    """
    # Count available data sources
    available_plots = []
    if search_results and 'hits' in search_results and search_results['hits']['hits']:
        available_plots.append('search')
    if aggregation_results:
        available_plots.append('aggregation')
    if cluster_info:
        available_plots.append('cluster')
    
    if not available_plots:
        print("❌ No data available for dashboard")
        return
    
    # Determine layout based on available data
    if len(available_plots) == 1:
        rows, cols = 1, 1
    elif len(available_plots) == 2:
        rows, cols = 1, 2
    else:
        rows, cols = 2, 2
    
    fig, axes = plt.subplots(rows, cols, figsize=figsize)
    fig.suptitle(title, fontsize=18, fontweight='bold', y=0.98)
    
    # Handle single subplot case
    if rows * cols == 1:
        axes = [axes]
    elif rows == 1 or cols == 1:
        axes = axes.flatten()
    else:
        axes = axes.flatten()
    
    plot_idx = 0
    
    # Plot search results summary
    if 'search' in available_plots:
        ax = axes[plot_idx]
        hits = search_results['hits']['hits']
        scores = [hit.get('_score', 0) for hit in hits if hit.get('_score', 0) > 0]
        
        if scores:
            ax.hist(scores, bins=min(10, len(scores)), color='skyblue', alpha=0.7, edgecolor='black')
            ax.set_title('Search Score Distribution', fontsize=12, fontweight='bold')
            ax.set_xlabel('Score')
            ax.set_ylabel('Frequency')
        else:
            ax.text(0.5, 0.5, f'Search Results\n{len(hits)} documents found', 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=14, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
            ax.set_title('Search Results Summary', fontsize=12, fontweight='bold')
        
        plot_idx += 1
    
    # Plot aggregation results
    if 'aggregation' in available_plots and plot_idx < len(axes):
        ax = axes[plot_idx]
        
        # Get first aggregation with buckets
        agg_data = None
        for agg_name, agg_result in aggregation_results.items():
            if 'buckets' in agg_result:
                agg_data = agg_result
                break
        
        if agg_data and 'buckets' in agg_data:
            buckets = agg_data['buckets'][:8]  # Limit to 8 categories for readability
            labels = [bucket['key'] for bucket in buckets]
            values = [bucket['doc_count'] for bucket in buckets]
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
            bars = ax.bar(labels, values, color=colors, alpha=0.8)
            ax.set_title('Top Categories', fontsize=12, fontweight='bold')
            ax.set_ylabel('Document Count')
            
            # Add value labels
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                       str(value), ha='center', va='bottom', fontweight='bold')
            
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plot_idx += 1
    
    # Plot cluster information
    if 'cluster' in available_plots and plot_idx < len(axes):
        ax = axes[plot_idx]
        
        info_text = []
        for key, value in list(cluster_info.items())[:6]:  # Limit items
            if isinstance(value, dict):
                info_text.append(f"{key.replace('_', ' ').title()}:")
                for sub_key, sub_value in list(value.items())[:2]:
                    info_text.append(f"  • {sub_key}: {sub_value}")
            else:
                display_value = str(value)[:30] + '...' if len(str(value)) > 30 else str(value)
                info_text.append(f"{key.replace('_', ' ').title()}: {display_value}")
        
        ax.text(0.05, 0.95, '\n'.join(info_text), 
               transform=ax.transAxes, verticalalignment='top', 
               fontsize=10, fontfamily='monospace',
               bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgreen", alpha=0.7))
        ax.set_title('Cluster Information', fontsize=12, fontweight='bold')
        ax.axis('off')
        plot_idx += 1
    
    # Hide unused subplots
    for i in range(plot_idx, len(axes)):
        axes[i].axis('off')
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)
    plt.show()


def display_colab_tips() -> None:
    """Display helpful tips for using visualizations in Google Colab."""
    tips = """
    📊 OpenSearch Visualization Tips for Google Colab:
    
    ✅ Best Practices:
    • Use %matplotlib inline for proper display
    • Figures are optimized for Colab's display width
    • All plots include value labels for better readability
    • Color schemes are chosen for good contrast
    
    🎨 Customization Options:
    • Adjust figsize parameter for different screen sizes
    • Use chart_type='auto' for smart chart selection
    • Combine multiple visualizations with create_dashboard_view()
    
    🔧 Troubleshooting:
    • If plots don't appear, run: plt.show() after each visualization
    • For interactive plots, consider using plotly instead of matplotlib
    • Large datasets may take longer to render - use max_results parameter
    
    📈 Available Functions:
    • plot_search_results() - Visualize search result patterns
    • create_aggregation_charts() - Chart aggregation data
    • display_cluster_metrics() - Show cluster health
    • format_search_response_for_display() - Create readable DataFrames
    • create_dashboard_view() - Comprehensive overview
    """
    print(tips)