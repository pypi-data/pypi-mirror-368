"""
Statistical Analysis Tools for Genomic Data
"""
import numpy as np
from scipy import stats

def t_test(group1, group2):
    """Perform independent t-test between two groups."""
    t_stat, p_val = stats.ttest_ind(group1, group2)
    return t_stat, p_val

def anova(*groups):
    """Perform one-way ANOVA across multiple groups."""
    f_stat, p_val = stats.f_oneway(*groups)
    return f_stat, p_val

def chi_square(observed, expected):
    """Perform chi-square test."""
    chi2, p_val = stats.chisquare(f_obs=observed, f_exp=expected)
    return chi2, p_val

def bonferroni_correction(p_values):
    """Apply Bonferroni correction to a list of p-values."""
    corrected = np.minimum(np.array(p_values) * len(p_values), 1.0)
    return corrected
