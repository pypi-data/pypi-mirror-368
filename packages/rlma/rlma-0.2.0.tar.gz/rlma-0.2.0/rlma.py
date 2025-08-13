#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mutual_info_score
from sklearn.preprocessing import KBinsDiscretizer, LabelEncoder
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.decomposition import PCA
from scipy.stats import spearmanr
from joblib import Parallel, delayed
import plotly.express as px
import plotly.graph_objects as go

def describe_data(arr, var_name='Variable'):
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

def categorize_variable(arr, num_categories=3, strategy='quantile'):
    """
    Categorize numeric or ordinal array into discrete bins.
    Supports any number of categories and strategies ('quantile', 'uniform', 'kmeans').
    Handles binary variables automatically.
    Returns integer category labels.
    """
    arr = np.asarray(arr)
    if set(np.unique(arr)).issubset({0,1}):
        # Binary data remains unchanged
        return arr.astype(int)
    
    discretizer = KBinsDiscretizer(n_bins=num_categories, encode='ordinal', strategy=strategy)
    arr_reshaped = arr.reshape(-1,1)
    categories = discretizer.fit_transform(arr_reshaped).astype(int).flatten()
    return categories

def continuous_similarity_score(x, y):
    """
    Compute similarity score between continuous arrays, scaled 0-1.
    Uses 1 - normalized absolute difference.
    """
    x = np.asarray(x)
    y = np.asarray(y)
    max_range = np.max([np.max(x) - np.min(x), np.max(y) - np.min(y), 1e-8])
    norm_diff = np.abs(x - y) / max_range
    similarity = 1 - norm_diff
    return np.clip(similarity, 0, 1)

def adaptive_alpha(x_cat, y_cat):
    """
    Adaptively determine alpha weight for near matches,
    based on category distribution overlap.
    """
    total = len(x_cat)
    near_matches = np.sum(np.abs(x_cat - y_cat) == 1)
    exact_matches = np.sum(x_cat == y_cat)
    if near_matches == 0:
        return 0
    alpha = near_matches / (near_matches + exact_matches)
    return np.clip(alpha, 0.1, 0.9)  # keep alpha sensible

def compute_rmi(x, y, num_categories=3, alpha=None, hybrid=True, plot=False, var_names=('X', 'Y')):
    """
    Compute Robust Linear Matching Index (RMI) between x and y.
    - Supports numeric, binary, ordinal data.
    - num_categories: number of categories for discretization.
    - alpha: near-match weight; if None, computed adaptively.
    - hybrid: if True, combine categorical matches with continuous similarity.
    - plot: display descriptive stats and match heatmaps.
    """
    x = np.asarray(x)
    y = np.asarray(y)
    
    # Describe data if plot enabled
    if plot:
        describe_data(x, var_names[0])
        describe_data(y, var_names[1])
    
    # Categorize variables
    x_cat = categorize_variable(x, num_categories)
    y_cat = categorize_variable(y, num_categories)
    
    if alpha is None:
        alpha = adaptive_alpha(x_cat, y_cat)
    
    # Calculate categorical match scores
    exact_matches = np.sum(x_cat == y_cat)
    near_matches = np.sum(np.abs(x_cat - y_cat) == 1)
    total = len(x_cat)
    
    cat_score = (exact_matches + alpha * near_matches) / total
    
    if not hybrid:
        rmi_score = cat_score
    else:
        # Calculate continuous similarity average
        cont_sim = continuous_similarity_score(x, y).mean()
        # Combine categorical and continuous similarity scores equally weighted
        rmi_score = 0.5 * cat_score + 0.5 * cont_sim
    
    if plot:
        # Heatmap of category matches
        contingency = pd.crosstab(x_cat, y_cat)
        plt.figure(figsize=(6,5))
        sns.heatmap(contingency, annot=True, fmt='d', cmap='YlGnBu')
        plt.xlabel(f'{var_names[1]} Categories')
        plt.ylabel(f'{var_names[0]} Categories')
        plt.title(f'Category Match Counts: {var_names[0]} vs {var_names[1]}')
        plt.show()
        
        # Category distribution plot
        fig, axes = plt.subplots(1,2, figsize=(10,4))
        sns.countplot(x=x_cat, ax=axes[0], palette='pastel')
        axes[0].set_title(f'{var_names[0]} Categories')
        sns.countplot(x=y_cat, ax=axes[1], palette='pastel')
        axes[1].set_title(f'{var_names[1]} Categories')
        plt.show()
        
        # Scatter of continuous similarity
        plt.figure(figsize=(6,4))
        sns.scatterplot(x=x, y=y)
        plt.title(f'Scatter plot of {var_names[0]} vs {var_names[1]}')
        plt.show()
    
    return rmi_score

def permutation_test(x, y, n_perm=1000, num_categories=3, alpha=None, hybrid=True, random_state=None, plot=False):
    """
    Permutation test for RMI significance.
    Returns p-value and permutation distribution.
    """
    rng = np.random.default_rng(random_state)
    observed = compute_rmi(x, y, num_categories, alpha, hybrid)
    perm_stats = np.zeros(n_perm)
    for i in range(n_perm):
        y_perm = rng.permutation(y)
        perm_stats[i] = compute_rmi(x, y_perm, num_categories, alpha, hybrid)
    p_val = (np.sum(perm_stats >= observed) + 1) / (n_perm + 1)
    
    if plot:
        plt.figure(figsize=(8,4))
        sns.histplot(perm_stats, bins=30, color='lightgray', kde=True)
        plt.axvline(observed, color='red', linestyle='--', label=f'Observed RMI = {observed:.3f}')
        plt.title('Permutation Test Distribution')
        plt.xlabel('RMI under Null')
        plt.ylabel('Frequency')
        plt.legend()
        plt.show()
    
    return {'p_value': p_val, 'observed_rmi': observed, 'perm_distribution': perm_stats}

def batch_rlma(X_df, y, num_categories=3, alpha=None, hybrid=True, n_perm=1000,
               random_state=None, n_jobs=1, plot=False):
    """
    Batch RLMA for multiple IVs in X_df against y.
    Runs permutation tests in parallel if n_jobs > 1.
    Returns DataFrame with variables, RMIs, p-values.
    """
    def single_rlma(col):
        rmi = compute_rmi(X_df[col], y, num_categories, alpha, hybrid)
        perm_res = permutation_test(X_df[col], y, n_perm, num_categories, alpha, hybrid, random_state)
        return {'Variable': col, 'RMI': rmi, 'p_value': perm_res['p_value']}
    
    results = Parallel(n_jobs=n_jobs)(delayed(single_rlma)(col) for col in X_df.columns)
    df_results = pd.DataFrame(results).sort_values(by='RMI', ascending=False).reset_index(drop=True)
    
    if plot:
        fig = px.bar(df_results, x='Variable', y='RMI',
                     title='Batch RLMA Scores per Variable',
                     labels={'RMI': 'Robust Linear Matching Index'})
        fig.show()
    
    return df_results

def composite_rlma(X_df, y, method='pca', num_categories=3, alpha=None, hybrid=True,
                  n_perm=1000, random_state=None, plot=False):
    """
    Composite RLMA combining all IVs into one predictor via PCA, Ridge, or RF.
    Runs permutation test on composite predictor.
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
        raise ValueError("Invalid method; choose 'pca', 'ridge', or 'rf'")
    
    rmi_val = compute_rmi(X_comp, y_np, num_categories, alpha, hybrid)
    
    perm_rmis = np.zeros(n_perm)
    for i in range(n_perm):
        y_perm = rng.permutation(y_np)
        if method == 'pca':
            X_comp_perm = X_comp  # PCA doesn't change by y
        elif method == 'ridge':
            ridge_perm = Ridge(alpha=1.0, random_state=random_state)
            ridge_perm.fit(X_np, y_perm)
            X_comp_perm = ridge_perm.predict(X_np)
        else:  # rf
            rf_perm = RandomForestRegressor(random_state=random_state)
            rf_perm.fit(X_np, y_perm)
            X_comp_perm = rf_perm.predict(X_np)
        perm_rmis[i] = compute_rmi(X_comp_perm, y_perm, num_categories, alpha, hybrid)
    
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
    
    return {'rmi_result': rmi_val, 'perm_p_value': emp_p, 'perm_distribution': perm_rmis}

def variable_importance(X_df, y, model='rf', random_state=None):
    """
    Compute variable importance scores using Ridge or Random Forest.
    Returns DataFrame with variables and importances.
    """
    X_np = np.asarray(X_df)
    y_np = np.asarray(y)
    if model == 'ridge':
        mdl = Ridge(alpha=1.0, random_state=random_state)
        mdl.fit(X_np, y_np)
        importances = np.abs(mdl.coef_)
    elif model == 'rf':
        mdl = RandomForestRegressor(random_state=random_state)
        mdl.fit(X_np, y_np)
        importances = mdl.feature_importances_
    else:
        raise ValueError("model must be 'ridge' or 'rf'")
    df_imp = pd.DataFrame({'Variable': X_df.columns, 'Importance': importances})
    return df_imp.sort_values(by='Importance', ascending=False).reset_index(drop=True)

def classical_associations(x, y):
    """
    Compute classical association metrics:
    - Spearman correlation and p-value
    - Mutual Information (discrete bins)
    """
    x = np.asarray(x)
    y = np.asarray(y)
    spearman_corr, spearman_p = spearmanr(x, y)
    
    # Discretize for MI
    num_bins = min(10, len(np.unique(x)))
    x_disc = categorize_variable(x, num_categories=num_bins)
    y_disc = categorize_variable(y, num_categories=num_bins)
    mi = mutual_info_score(x_disc, y_disc)
    
    return {'spearman_corr': spearman_corr, 'spearman_p': spearman_p, 'mutual_info': mi}

# Placeholder for CLI interface (future)
def cli_interface():
    print("RLMA CLI interface coming soon!")

# ------------------- END OF MODULE -------------------
