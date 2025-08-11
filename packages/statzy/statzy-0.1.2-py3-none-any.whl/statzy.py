import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
from io import StringIO
import base64
from IPython.display import display, HTML
import math

def summary(df, n=5):

    # Generate combined metadata strings for each column
    meta_row = df.dtypes.astype(str).astype(object)  # Convert to object dtype for string ops

    for col in df.columns:
        non_nulls = df[col].notnull().sum()
        nulls = df[col].isnull().sum()
        unique = df[col].nunique(dropna=True)
        dtype = str(df[col].dtype)
        
        meta_str = (f"{non_nulls} non-nulls"
            f"<br>{nulls} nulls"
            f"<br>{unique} unique"
            f"<br>{dtype}")
        meta_row[col] = meta_str

    meta_df = pd.DataFrame([meta_row], index=['Meta'])
    combined = pd.concat([meta_df, df.head(n)], ignore_index=False)

    print("\n")
    print("Dataset Overview:")
    print("=================")

    print("Shape of the dataset: " + str(df.shape))
    info(df)
    
    display(HTML(combined.to_html(escape=False)))
    # display(combined)  # for Jupyter/Colab
    # print(combined)  # Uncomment for non-notebook use
    
    describe(df)
    
def info(df):    
    # print("\n")
    # print("Additional Information about the dataset:")
    # print("=========================================")

    # print("COLUMN INFORMATION (TRIMMED):")
    # print("------------------------------")
    buffer = StringIO()
    df.info(buf=buffer)
    lines = buffer.getvalue().splitlines()

    # Drop unwanted lines — e.g., memory usage, class info
    # filtered = [line for line in lines 
    #             if 'memory usage' not in line 
    #             and 'object at' not in line]
    # print("\n".join(filtered))
    
    # filtered = []
    # for line in lines:
    #     if line.strip().startswith("#") or "non-null" in line or "Column" in line:
    #         continue  # Skip the detailed column listing
    #     filtered.append(line)
    # print("\n".join(filtered))

    for line in lines:
        if line.strip().startswith("RangeIndex:") or \
           line.strip().startswith("dtypes:") or \
           line.strip().startswith("memory usage:"):
            print(line.strip())

def describe(df):    
    numeric_cols = get_numeric_cols(df)
    cat_cols = get_cat_cols(df)

    print("\nNUMERIC COLUMNS SUMMARY:")
    print("------------------------")
    numeric_data = prepare_table_data_for_numeric_columns(df, numeric_cols)
    numeric_html = render_html_table(numeric_data, numeric_cols)
    display(HTML(numeric_html))

    print("\nCATEGORICAL COLUMNS SUMMARY:")
    print("----------------------------")
    if not cat_cols.empty:
        cat_data = prepare_table_data_for_categorical_columns(df, cat_cols)
        cat_html = render_html_table(cat_data, cat_cols)
        display(HTML(cat_html))
    
    tidy_describe(df)

def get_numeric_cols(df):
    return df.select_dtypes(include=np.number).columns

def get_cat_cols(df):
    return df.select_dtypes(include='object').columns
    
def get_correlation_matrix(df):
    print("\nCorrelation Analysis:")
    print("======================")
    
    # Pair plot (comment if too slow)
    print("\nPAIR PLOT (Numeric Columns):")
    print("----------------------------")
    numeric_cols = get_numeric_cols(df)
    sns.pairplot(df[numeric_cols])
    plt.show()
    
    # corr_matrix = df.corr()
    # plt.figure(figsize=(10, 8))
    # sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
    # plt.title('Correlation Matrix')
    # plt.show()
    
def get_boxplot_by_category(df):
    # Box plots: numeric columns grouped by each categorical column
    print("\nBOX PLOTS: Numeric Columns grouped by Categorical Columns")
    print("---------------------------------------------------------")
    numeric_cols = get_numeric_cols(df)
    cat_cols = get_cat_cols(df)
    for cat_col in cat_cols:
        n = len(numeric_cols)
        cols = min(n, 3)  # max 3 plots per row
        rows = math.ceil(n / cols)

        fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 5 * rows))
        fig.suptitle(f"Box Plots Grouped by '{cat_col}'", fontsize=16)
        
        # Flatten axes for consistent indexing
        axes = np.array(axes).reshape(-1)

        for i, num_col in enumerate(numeric_cols):
            sns.boxplot(x=cat_col, y=num_col, data=df, ax=axes[i])
            axes[i].set_title(f"{num_col} by {cat_col}")
            axes[i].tick_params(axis='x', rotation=45)

        # Turn off any unused subplots
        for j in range(i + 1, len(axes)):
            axes[j].axis('off')

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.show()
    
def prepare_table_data_for_numeric_columns(df, numeric_cols):
    """Prepare all data for the summary table for numeric columns"""
    data = {}
    
    desc = df[numeric_cols].describe().round(2)
    
    # Add summary statistics
    for idx in desc.index:
        data[idx] = {col: desc.loc[idx, col] for col in numeric_cols}
    
    # Add visualizations
    data['Histogram'] = {col: get_histogram(df, col) for col in numeric_cols}
    data['Box Plot'] = {col: get_boxplot(df, col) for col in numeric_cols}
    
    plt.close('all')
    return data
    
def prepare_table_data_for_categorical_columns(df, cat_cols):
    """Prepare all data for the summary table for categorical columns"""
    try:
        data = {}
        desc = df[cat_cols].describe()

        # Add summary statistics for categorical columns
        # for idx in desc.index:
        #     if idx != 'top':  # Skip 'top' row as it's redundant with Top 3 Values
        #         data[idx] = {col: desc.loc[idx, col] for col in cat_cols}
                
        if 'count' in desc.index:
            data['count'] = {col: desc.loc['count', col] for col in cat_cols}
        # data['Missing %'] = {col: f"{(df[col].isnull().sum() / len(df) * 100):.1f}%" for col in cat_cols}
        # if 'freq' in desc.index:
        #     data['freq'] = {col: desc.loc['freq', col] for col in cat_cols}
            
        data['Frequency Chart'] = {col: get_frequency_chart(df, col) for col in cat_cols}
        # if 'unique' in desc.index:
        #     data['unique'] = {col: desc.loc['unique', col] for col in cat_cols}
        data['Top 3 Values'] = {col: f"{df[col].value_counts().head(3).to_dict()}" for col in cat_cols}
        
        return data
    except Exception as e:
        print(f"Error in prepare_table_data_for_categorical_columns: {e}")
        print(f"cat_cols: {cat_cols}")
        print(f"cat_cols type: {type(cat_cols)}")
        return {}
    
def get_histogram(df, numeric_col):
    fig, ax = plt.subplots(figsize=(2, 1.5))
    sns.histplot(df[numeric_col], ax=ax, bins=10, edgecolor='black', kde=False)
    ax.set_title(numeric_col, fontsize=8)
    ax.tick_params(axis='both', labelsize=6)
    ax.set_xlabel('')
    ax.set_ylabel('')
    histogram_image = plot_to_base64(fig)
    plt.close(fig)
    return histogram_image
    
def get_boxplot(df, col):
    #########################################################################################
    # Calculate stats
    #########################################################################################
    series = df[col].dropna()
    
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower_whisker_limit = q1 - 1.5 * iqr
    upper_whisker_limit = q3 + 1.5 * iqr
    # Determine actual whisker ends (largest points within the 1.5*IQR fences)
    whisker_min = series[series >= lower_whisker_limit].min()
    whisker_max = series[series <= upper_whisker_limit].max()
    
    stats = {
        'min': series.min(),
        'whisker_min': whisker_min,
        'p5': series.quantile(0.05),
        'q1': series.quantile(0.25),
        'median': series.median(),
        'q3': series.quantile(0.75),
        'p95': series.quantile(0.95),
        'whisker_max': whisker_max,
        'max': series.max(),
        'mean': series.mean(),
        'std': series.std()
    }

    fig, ax = plt.subplots(figsize=(3, 3))
    ax.set_facecolor('white')  # or 'none' for transparent background
    
    # Draw horizontal boxplot, show mean as red dot, no fliers (outliers)
    sns.boxplot(x=series, 
                ax=ax, 
                showmeans=True,                                             # mean
                meanprops=dict(marker='o', markerfacecolor='red', markeredgecolor='red', markersize=6),
                
                showfliers=True,
                flierprops=dict(marker='o', color='black', markersize=5),   # outliers (dots)
                
                medianprops=dict(color='black'),                            # median line
                
                showcaps=True,
                capprops=dict(linewidth=1),                                 # caps (ends of whiskers)
                boxprops=dict(linewidth=1, facecolor='#f0f4f8'),                                 # box
                whiskerprops=dict(linewidth=1),                             # whiskers (lines)
                
                orient='h',                                                 # horizontal
    )
    
    # Remove y-axis ticks and spines
    ax.set_xticklabels([])
    ax.set_xlabel('')
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    # Set x-axis limits slightly wider than min/max for padding
    xpad = (stats['max'] - stats['min']) * 0.1
    ax.set_xlim(stats['min'] - xpad, stats['max'] + xpad)
    
    #########################################################################################
    # Annotate min, lower whisker, Q1, median, Q3, upper whisker, max, p5, p95, mean
    #########################################################################################
    y_text = 0.9
    y_text_offset = 0.3
    toggle = True
    label_color = 'black'
    outlier_color = 'red'
    label_font_size = 14
    label_va = 'bottom'
    label_ha = 'center'
    
    # min and Lower whisker
    y_text = toggle_offset(y_text, y_text_offset, toggle); toggle = not toggle
    if stats['min'] < lower_whisker_limit:
        # min (outlier)
        ax.text(stats['min'], y_text, f"min\n(outlier)\n{format_decimal_if_needed(stats['min'])}", ha=label_ha, va=label_va, fontsize=label_font_size, color=outlier_color)
        
        # lower whisker
        y_text = toggle_offset(y_text, y_text_offset, toggle); toggle = not toggle
        ax.text(stats['whisker_min'], y_text, f"{format_decimal_if_needed(stats['whisker_min'])}", ha=label_ha, va=label_va, fontsize=label_font_size, color=label_color)
    else:
        # min
        ax.text(stats['min'], y_text, f"min\n{format_decimal_if_needed(stats['min'])}", ha=label_ha, va=label_va, fontsize=label_font_size, color=label_color)
    
    # Annotate Q1, median, Q3
    for key in ['q1', 'median', 'q3']:
        val = stats[key]
        val_str = format_decimal_if_needed(val)
        # label = f"{key}\n{val_str}"    
        label = f"{val_str}"
        y_text = toggle_offset(y_text, y_text_offset, toggle); toggle = not toggle
        ax.text(val, y_text, label, ha=label_ha, va=label_va, fontsize=label_font_size, color=label_color)

    # Upper whisker and max
    y_text = toggle_offset(y_text, y_text_offset, toggle); toggle = not toggle
    if stats['max'] > upper_whisker_limit:
        # upper whisker
        ax.text(stats['whisker_max'], y_text, f"{format_decimal_if_needed(stats['whisker_max'])}", ha=label_ha, va=label_va, fontsize=label_font_size, color=label_color)
        
        # max (outlier)
        y_text = toggle_offset(y_text, y_text_offset, toggle); toggle = not toggle
        ax.text(stats['max'], y_text, f"max\n(outlier)\n{format_decimal_if_needed(stats['max'])}", ha=label_ha, va=label_va, fontsize=label_font_size, color=outlier_color)
    else:
        # max
        ax.text(stats['max'], y_text, f"max\n{format_decimal_if_needed(stats['max'])}", ha=label_ha, va=label_va, fontsize=label_font_size, color=label_color)    
        
    #########################################################################################
    # Annotate p5, p95, mean
    #########################################################################################
    # Plot dots for p5, p95
    ax.plot(stats['p5'], 0, marker='o', color='purple', markersize=5, zorder=5)
    ax.plot(stats['p95'], 0, marker='o', color='purple', markersize=5, zorder=5)
    
    # Annotate p5, p95, mean
    ax.text(stats['p5'], -0.4, f"p5\n{format_decimal_if_needed(stats['p5'])}", ha=label_ha, va=label_va, fontsize=12, color='purple')
    ax.text(stats['p95'], -0.4, f"p95\n{format_decimal_if_needed(stats['p95'])}", ha=label_ha, va=label_va, fontsize=12, color='purple')
    ax.text(stats['mean'], -0.4, f"mean\n{format_decimal_if_needed(stats['mean'])}", ha=label_ha, va=label_va, fontsize=12, color='red')
    
    #########################################################################################
    # Standard Deviation
    #########################################################################################
    std1_low = stats['mean'] - stats['std']
    std1_high = stats['mean'] + stats['std']
    std2_low = stats['mean'] - 2 * stats['std']
    std2_high = stats['mean'] + 2 * stats['std']

    # ±1 std
    ax.axvspan(std1_low, std1_high, color='blue', alpha=0.1, label=f'±1σ ({format_decimal_if_needed(stats["std"])})\n{format_decimal_if_needed(std1_low)} - {format_decimal_if_needed(std1_high)}') # Shade ±1 std range (light blue)

    # ±2 std
    ax.axvspan(std2_low, std2_high, color='green', alpha=0.05, label=f'±2σ \n{format_decimal_if_needed(std2_low)} - {format_decimal_if_needed(std2_high)}') # Shade ±2 std range (light green)

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.45), ncol=2, frameon=False)

    #########################################################################################
    # Title
    #########################################################################################
    ax.set_title(col, fontsize=18, loc='center', fontweight='bold', color='black', pad=40)

    #########################################################################################
    # Return plot image
    #########################################################################################
    plt.tight_layout()
    plot_image = plot_to_base64(fig)
    plt.close(fig)
    return plot_image

def get_frequency_chart(df, col):
    """Generate frequency bar chart for categorical column"""
    
    fig, ax = plt.subplots(figsize=(4, 2.5))
    
    value_counts = df[col].value_counts()
    
    # Create bar chart
    bars = ax.bar(range(len(value_counts)), value_counts.values, alpha=0.7)
    ax.set_xticks(range(len(value_counts)))
    ax.set_xticklabels(value_counts.index, rotation=45, ha='right', fontsize=8)
    ax.set_xlabel(f'{col}\n({len(value_counts)} unique)', fontsize=15)
    ax.set_ylabel('Count', fontsize=15)
    ax.set_yticks([])  # Hide y-axis ticks
    ax.set_yticklabels([])  # Hide y-axis labels
    ax.tick_params(axis='y', labelsize=8)
    
    # Add value labels on bars
    for bar, count in zip(bars, value_counts.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(value_counts.values) * 0.01,
                str(count), ha='center', va='bottom', fontsize=12)
    
    #########################################################################################
    # Return plot image
    #########################################################################################
    plt.tight_layout()
    plot_image = plot_to_base64(fig)
    plt.close(fig)
    return plot_image

def format_decimal_if_needed(x, decimals=1):
    if x == int(x):
        return str(int(x))
    else:
        return f"{x:.{decimals}f}"

def toggle_offset(y_text, y_text_offset, toggle):
    if toggle:
        return y_text - y_text_offset
    else:
        return y_text + y_text_offset

def plot_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    # return f"<img src='data:image/png;base64,{b64}' width='150'>"
    return f"<img src='data:image/png;base64,{b64}' style='width:100%; height:auto;'>"
    
def render_html_table(data, columns, table_style="border='1' style='border-collapse: collapse; text-align: center;'"):
    """Convert tabular data to HTML table"""
    # Header
    header = f"<tr><th></th>{''.join(f'<th><b>{col}</b></th>' for col in columns)}</tr>"
    
    # Data rows
    rows = []
    for row_name, row_data in data.items():
        cells = f"<td><b>{row_name}</b></td>{''.join(f'<td>{row_data[col]}</td>' for col in columns)}"
        rows.append(f"<tr>{cells}</tr>")
    
    return f"<table {table_style}>{header}{''.join(rows)}</table>"
    
def tidy_describe(df):
    desc = df.describe().round(2)

    # For each column, combine all rows into one multi-line string
    combined = desc.apply(
        lambda col: "\n".join(f"{idx}: {val}" for idx, val in col.items())
    )

    # Convert Series to DataFrame for nicer display
    combined_df = pd.DataFrame(combined).T  # single row with columns as columns

    return combined_df.style.background_gradient(cmap='Blues')