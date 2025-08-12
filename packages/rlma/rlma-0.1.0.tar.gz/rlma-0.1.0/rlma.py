#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor

def describe_data(arr, var_name='Variable'):
    """
    Print descriptive statistics and plot histogram and boxplot of a numeric array.
    """
    arr = np.asarray(arr)
    print(f"\nDescriptive Statistics for '{var_name}':")
    print(f"Count: {len(arr)}")
    print(f"Mean: {np.mean(arr):.3f}")
    print(f"Median: {np.median(arr):.3f}")
    print(f"Std Dev: {np.std(arr):.3f}")
    print(f"Min: {np.min(arr):.3f}")
    print(f"Max: {np.max(arr):.3f}")
    print(f"25th Percentile: {np.percentile(arr, 25):.3f}")
    print(f"75th Percentile: {np.percentile(arr, 75):.3f}")

    plt.figure(figsize=(12,4))
    plt.subplot(1,2,1)
    sns.histplot(arr, kde=True, bins=20, color='skyblue')
    plt.title(f'Histogram of {var_name}')
    plt.subplot(1,2,2)
    sns.boxplot(x=arr, color='lightgreen')
    plt.title(f'Boxplot of {var_name}')
    plt.show()

def categorize_variable_percentile(arr, num_categories=3):
    """
    Categorize a numeric array into discrete levels based on percentiles.
    Default splits into 3 categories: Low (<=33rd), Moderate (33rd-66th), High (>66th).
    Returns an array of category labels: 0 (Low), 1 (Moderate), 2 (High).
    """
    arr = np.asarray(arr)
    if num_categories != 3:
        raise NotImplementedError("Only 3-category version implemented")
    
    p33 = np.percentile(arr, 33)
    p66 = np.percentile(arr, 66)
    
    categories = np.zeros_like(arr, dtype=int)
    categories[arr <= p33] = 0  # Low
    categories[(arr > p33) & (arr <= p66)] = 1  # Moderate
    categories[arr > p66] = 2  # High
    
    return categories

def plot_category_match(x_cat, y_cat, var_x='X', var_y='Y'):
    """
    Plot a heatmap showing counts of category matches between x_cat and y_cat.
    """
    import matplotlib.ticker as ticker

    contingency = pd.crosstab(x_cat, y_cat)
    plt.figure(figsize=(6,5))
    sns.heatmap(contingency, annot=True, fmt='d', cmap='YlGnBu')
    plt.xlabel(f'{var_y} Categories')
    plt.ylabel(f'{var_x} Categories')
    plt.title(f'Category Match Counts: {var_x} vs {var_y}')
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.gca().yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.show()

def rmi_single_pair(x, y, num_categories=3, alpha=0.5, plot=False, var_names=('X', 'Y')):
    """
    Compute Robust Linear Matching Index (RMI) between two variables x and y.
    - Supports continuous and binary data.
    - alpha: weight for near matches (categories adjacent).
    - plot: if True, plot category match heatmap and distributions.
    - var_names: tuple of (x_name, y_name) for labeling plots.
    """
    x = np.asarray(x)
    y = np.asarray(y)
    
    # Describe data
    if plot:
        describe_data(x, var_names[0])
        describe_data(y, var_names[1])
    
    # Handle binary variables (only categories 0 or 1)
    unique_x = np.unique(x)
    unique_y = np.unique(y)
    if set(unique_x).issubset({0,1}):
        x_cat = x
    else:
        x_cat = categorize_variable_percentile(x, num_categories)
    if set(unique_y).issubset({0,1}):
        y_cat = y
    else:
        y_cat = categorize_variable_percentile(y, num_categories)

    if plot:
        # Plot category match heatmap
        plot_category_match(x_cat, y_cat, var_x=var_names[0], var_y=var_names[1])

        # Plot category distributions side by side
        fig, axes = plt.subplots(1,2, figsize=(10,4))
        sns.countplot(x=x_cat, ax=axes[0], palette='pastel')
        axes[0].set_title(f'{var_names[0]} Categories')
        sns.countplot(x=y_cat, ax=axes[1], palette='pastel')
        axes[1].set_title(f'{var_names[1]} Categories')
        plt.show()

    # Count matches
    exact_matches = np.sum(x_cat == y_cat)
    near_matches = np.sum(np.abs(x_cat - y_cat) == 1)
    total = len(x_cat)

    score = (exact_matches + alpha * near_matches) / total
    return score

def permutation_test(x, y, n_perm=1000, num_categories=3, alpha=0.5, random_state=None, plot=False):
    """
    Perform permutation test for RMI significance.
    Returns dict with empirical p-value and null distribution.
    Optionally plots permutation distribution with observed statistic.
    """
    rng = np.random.default_rng(random_state)
    observed_rmi = rmi_single_pair(x, y, num_categories, alpha)
    perm_rmis = np.zeros(n_perm)
    for i in range(n_perm):
        y_perm = rng.permutation(y)
        perm_rmis[i] = rmi_single_pair(x, y_perm, num_categories, alpha)
    emp_p = (np.sum(perm_rmis >= observed_rmi) + 1) / (n_perm + 1)

    if plot:
        plt.figure(figsize=(8,4))
        sns.histplot(perm_rmis, bins=30, kde=True, color='lightgray')
        plt.axvline(observed_rmi, color='red', linestyle='--', label=f'Observed RMI = {observed_rmi:.3f}')
        plt.title('Permutation Test Distribution')
        plt.xlabel('RMI under Null (Permutations)')
        plt.ylabel('Frequency')
        plt.legend()
        plt.show()

    return {'emp_p': emp_p, 'observed_rmi': observed_rmi, 'perm_distribution': perm_rmis}

def batch_pairwise_rlma(X_df, y, n_perm=1000, num_categories=3, alpha=0.5, random_state=None, plot=False):
    """
    Run RLMA on all columns in X_df against y.
    Returns a DataFrame with RMI and p-values.
    If plot=True, plots RMI values for all variables.
    """
    results = []
    for col in X_df.columns:
        rmi = rmi_single_pair(X_df[col], y, num_categories, alpha)
        perm = permutation_test(X_df[col], y, n_perm, num_categories, alpha, random_state)
        results.append({'Variable': col, 'RMI': rmi, 'p_value': perm['emp_p']})
    df_results = pd.DataFrame(results).sort_values(by='RMI', ascending=False).reset_index(drop=True)

    if plot:
        plt.figure(figsize=(10,5))
        sns.barplot(data=df_results, x='Variable', y='RMI', palette='viridis')
        plt.xticks(rotation=45)
        plt.title('Batch RLMA: RMI Scores per Variable')
        plt.show()

    return df_results

def composite_rlma(X_df, y, method='ridge', n_perm=1000, num_categories=3, alpha=0.5, random_state=None, plot=False):
    """
    Composite RLMA using predicted composite IV from PCA, Ridge, or Random Forest.
    - method: 'pca', 'ridge', or 'rf'
    Returns dict with RMI and permutation test results.
    Optionally plots permutation distribution.
    """
    rng = np.random.default_rng(random_state)
    X_np = np.asarray(X_df)
    y_np = np.asarray(y)

    if method == 'pca':
        pca = PCA(n_components=1)
        X_comp = pca.fit_transform(X_np).flatten()
    elif method == 'ridge':
        ridge = Ridge(alpha=1.0, random_state=random_state)
        ridge.fit(X_np, y_np)
        X_comp = ridge.predict(X_np)
    elif method == 'rf':
        rf = RandomForestRegressor(random_state=random_state)
        rf.fit(X_np, y_np)
        X_comp = rf.predict(X_np)
    else:
        raise ValueError("method must be 'pca', 'ridge', or 'rf'")

    rmi_val = rmi_single_pair(X_comp, y_np, num_categories, alpha)

    perm_rmis = np.zeros(n_perm)
    for i in range(n_perm):
        y_perm = rng.permutation(y_np)
        if method == 'pca':
            X_comp_perm = X_comp
        elif method == 'ridge':
            ridge_perm = Ridge(alpha=1.0, random_state=random_state)
            ridge_perm.fit(X_np, y_perm)
            X_comp_perm = ridge_perm.predict(X_np)
        elif method == 'rf':
            rf_perm = RandomForestRegressor(random_state=random_state)
            rf_perm.fit(X_np, y_perm)
            X_comp_perm = rf_perm.predict(X_np)
        perm_rmis[i] = rmi_single_pair(X_comp_perm, y_perm, num_categories, alpha)

    emp_p = (np.sum(perm_rmis >= rmi_val) + 1) / (n_perm + 1)

    if plot:
        plt.figure(figsize=(8,4))
        sns.histplot(perm_rmis, bins=30, kde=True, color='lightgray')
        plt.axvline(rmi_val, color='red', linestyle='--', label=f'Observed Composite RMI = {rmi_val:.3f}')
        plt.title('Permutation Test Distribution - Composite RLMA')
        plt.xlabel('RMI under Null (Permutations)')
        plt.ylabel('Frequency')
        plt.legend()
        plt.show()

    return {'rmi_result': rmi_val, 'perm_result': {'emp_p': emp_p, 'perm_distribution': perm_rmis}}

