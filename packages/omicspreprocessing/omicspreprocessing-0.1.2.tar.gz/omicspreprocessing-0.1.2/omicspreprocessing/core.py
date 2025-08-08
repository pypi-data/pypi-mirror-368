import math
from statistics import mean
from typing import Any, Dict, List, Optional, Tuple, Callable
from multiprocessing.pool import Pool

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

from scipy.stats import f_oneway, ttest_ind, shapiro, kstest, ks_2samp
from statsmodels.stats.multitest import fdrcorrection
import scikit_posthocs as sp

from sklearn import metrics
from sklearn.model_selection import RepeatedStratifiedKFold

import itertools

def raw_median_centering_normalization(df: pd.DataFrame, general_median: float):
    """
    Perform column-wise median centering normalization on a DataFrame using an external reference median.

    This function normalizes each column of the input DataFrame by scaling its values so that
    the column's median matches the specified `general_median`. This is useful when adjusting
    datasets to a common scale based on a known or reference distribution.

    Parameters:
    ----------
    df : pd.DataFrame
        A pandas DataFrame containing numerical data to normalize. It is assumed that the
        DataFrame is indexed and contains no non-numeric columns.

    general_median : float
        The reference median value from another distribution that each column should be normalized to.

    Returns:
    -------
    pd.DataFrame
        A new DataFrame of the same shape as `df` with normalized values such that the
        median of each column is approximately equal to `general_median`.

    Notes:
    -----
    - Columns containing NaN values will be normalized ignoring the NaNs in median computation.
    - The index and column names of the original DataFrame are preserved.
    """
    print(df.shape)
    matrix = df.to_numpy()
    columns_names = df.columns
    rownames = df.index

    def normalize(temp: np.ndarray):
        temp_median = np.median(temp[~np.isnan(temp)])
        normalized_temp = temp * general_median / temp_median
        return normalized_temp

    final_matrix = np.apply_along_axis(normalize, 0, matrix)
    final_df = pd.DataFrame(final_matrix)
    final_df.index = rownames
    final_df.columns = columns_names
    return final_df


def do_shapiro_test(df, column_to_do_test):
    """
    Perform the Shapiro-Wilk test for normality on a specific column of a DataFrame.

    This function applies the Shapiro-Wilk test to determine whether the values in the
    specified column are normally distributed. It is suitable for small sample sizes
    (n < 5000) and prints both the test statistic and the interpretation based on
    a significance level of 0.05.

    Parameters:
    ----------
    df : pd.DataFrame
        The DataFrame containing the data to test.

    column_to_do_test : str
        The name of the column in `df` on which to perform the Shapiro-Wilk test.

    Returns:
    -------
    None
        This function prints the results to the console but does not return anything.

    Notes:
    -----
    - The null hypothesis (H0) of the Shapiro-Wilk test is that the data is normally distributed.
    - A p-value greater than 0.05 suggests normality (fail to reject H0).
    - A p-value less than or equal to 0.05 suggests deviation from normality (reject H0).
    """
    stat, p_value = shapiro(df[column_to_do_test])
    print(f"Test Statistic: {stat}, p-value: {p_value}")

    # Interpretation
    alpha = 0.05
    if p_value > alpha:
        print("Data looks normally distributed (fail to reject H0)")
    else:
        print("Data does not look normally distributed (reject H0)")


def do_smirnov_test(df, column_to_do_test):
    """
    Perform the Kolmogorov-Smirnov test for normality on a specific column of a DataFrame.

    This function applies the one-sample Kolmogorov-Smirnov (K-S) test to compare the
    empirical distribution of the specified column with a standard normal distribution.

    Parameters:
    ----------
    df : pd.DataFrame
        The DataFrame containing the data to test.

    column_to_do_test : str
        The name of the column in `df` to test for normality.

    Returns:
    -------
    None
        The function prints the test statistic, p-value, and an interpretation based on
        a significance level of 0.05.

    Notes:
    -----
    - The null hypothesis (H0) is that the data comes from a standard normal distribution.
    - A p-value > 0.05 suggests the data may be normally distributed (fail to reject H0).
    - A p-value ≤ 0.05 indicates the data does not follow a normal distribution (reject H0).
    - This test assumes the data is already standardized; otherwise, results may be misleading.
    """

    stat, p_value = kstest(df[column_to_do_test], "norm")
    print(f"Test Statistic: {stat}, p-value: {p_value}")

    # Interpretation
    alpha = 0.05
    if p_value > alpha:
        print("Data looks normally distributed (fail to reject H0)")
    else:
        print("Data does not look normally distributed (reject H0)")


def compare_two_distributions(data1, data2):
    """
    Compare two empirical distributions using the two-sample Kolmogorov-Smirnov (KS) test.

    This function tests whether the two input datasets are drawn from the same continuous distribution.
    It prints the KS test statistic, the p-value, and an interpretation based on a significance
    level of 0.05.

    Parameters:
    ----------
    data1 : array-like
        The first sample distribution (e.g., list, NumPy array, or pandas Series).

    data2 : array-like
        The second sample distribution.

    Returns:
    -------
    None
        This function prints the KS statistic, p-value, and an interpretation of the test result.

    Notes:
    -----
    - Null hypothesis (H0): The two distributions are identical.
    - A p-value > 0.05 suggests that the two distributions are similar (fail to reject H0).
    - A p-value ≤ 0.05 indicates that the two distributions are statistically different (reject H0).
    - This test is non-parametric and sensitive to differences in both location and shape of the distributions.
    """
    # KS Test
    stat, p_value = ks_2samp(data1, data2)

    print(f"KS Statistic: {stat}, p-value: {p_value}")

    # Interpretation
    alpha = 0.05
    if p_value > alpha:
        print("The two distributions are similar (fail to reject H0)")
    else:
        print("The two distributions are different (reject H0)")


def do_normalize_with_target_df(z_scored_value, average_target, std_target):
    """
    Convert a z-scored value to the scale of a target distribution.

    This function takes a standardized (z-scored) value and transforms it to a value
    in a target distribution with a specified mean and standard deviation. It performs
    the inverse z-score transformation:

        normalized_value = mean_target + z * std_target

    Parameters:
    ----------
    z_scored_value : float
        The z-scored (standardized) value to be mapped to the target distribution.

    average_target : float
        The mean (μ) of the target distribution.

    std_target : float
        The standard deviation  of the target distribution.

    Returns:
    -------
    float
        The normalized value on the scale of the target distribution.

    Example:
    -------
    do_normalize_with_target_df(1.5, 100, 15)
    122.5
    """
    return average_target + (z_scored_value * std_target)


def get_replicate_number(
    df: pd.DataFrame, column_name: str = "Sample_name"
) -> pd.DataFrame:
    """
    Add a 'replicate' column to the DataFrame by assigning replicate numbers within groups.

    For each group defined by the unique values in the specified `column_name`, this function
    assigns sequential replicate numbers starting from 1. It adds a new column called 'replicate'
    to the returned DataFrame.

    Parameters:
    ----------
    df : pd.DataFrame
        The input DataFrame containing the data to process.

    column_name : str, optional
        The column to group by when determining replicates. Default is 'Sample_name'.

    Returns:
    -------
    pd.DataFrame
        A new DataFrame with an additional 'replicate' column indicating the replicate number
        within each group.

    Raises:
    ------
    ValueError
        If the input is not a DataFrame or the specified column does not exist.

    Notes:
    -----
    - Replicate numbers start at 1.
    - This function preserves the original DataFrame structure but returns a modified copy.
    """
    if isinstance(df, pd.DataFrame) and column_name in df.columns:
        try:

            all_grps = []
            splitted_df = df.groupby(column_name)
            group_names = df[column_name].unique().tolist()

            for grp in group_names:
                sub_df = splitted_df.get_group(grp)
                sub_df["replicate"] = list(range(len(sub_df)))
                all_grps.append(sub_df)
            final_df = pd.concat(all_grps)
            final_df["replicate"] = final_df["replicate"] + 1
            return final_df
        except:
            print("The replicate column was not added")
            return df
    else:
        raise ValueError("Error: Check the data frame with the column selected")


def check_path_exist(func):
    import os
    def wrapper(path: str, *args, **kwargs):
        if os.path.exists(path):
            print("###")
            print(f"Reading the file {path}")
            try:
                df = func(path, *args, **kwargs)
                print(f"{path} loaded with success!")
                return df
            except:
                print(f"# ERROR in OPENING {path}")
                return [f"error in reading the file {path} probably opened somewhere"]
        else:
            print(f"{path} does not exist")
            pass

    return wrapper


def show_spent_time(func):
    """
    Decorator to measure and display the execution time of a function.

    This decorator wraps any function and prints the time it took to execute,
    which can be helpful for performance monitoring or benchmarking.

    Usage:
    ------
    @show_spent_time
    def some_function(...):
        ...

    Parameters:
    ----------
    func : callable
        The function whose execution time is to be measured.

    Returns:
    -------
    callable
        A wrapped version of the original function that prints the time spent during execution.
    """
    import time

    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        time_spent = end - start
        print(f"The time spent: {time_spent}")
        return res

    return wrapper


def unnest_proteingroups(df: pd.DataFrame) -> pd.DataFrame:
    """
    Unnest rows in a DataFrame where the index contains multiple protein group identifiers.

    This function assumes that the DataFrame index contains semicolon-separated (`;`)
    protein group identifiers (e.g., "P12345;P67890"). It splits these compound index values
    and creates a separate row for each individual protein group, while duplicating the
    associated row values.

    Parameters:
    ----------
    df : pd.DataFrame
        Input DataFrame with protein group identifiers in the index,
        potentially in the form "A;B;C".

    Returns:
    -------
    pd.DataFrame
        A new DataFrame where each protein group identifier appears in a separate row.
        The index will contain individual protein IDs, and the original data will be duplicated accordingly.

    Example:
    -------
    >>> df.index = ['P12345;P67890']
    >>> df = unnest_proteingroups(df)
    >>> df.index
    Index(['P12345', 'P67890'], dtype='object')
    """
    temp_df = df
    temp_df["index"] = temp_df.index.str.split(";")
    temp_df = temp_df.explode("index")
    temp_df = temp_df.set_index("index")
    return temp_df


def get_cv_from_melted_df(
    melted_df: pd.DataFrame, protein_col="Proteins_names", value_col="value"
) -> pd.DataFrame:
    """
    Calculate the coefficient of variation (CV) for each protein from a long-format DataFrame.

    The function groups the data by protein names, computes the standard deviation and mean
    of the specified values, and then calculates the CV as std/mean.

    Parameters:
    ----------
    melted_df : pd.DataFrame
        A long-format DataFrame containing protein names and corresponding values.

    protein_col : str, optional
        The column name containing protein identifiers. Default is 'Proteins_names'.

    value_col : str, optional
        The column name containing numeric values for which the CV is calculated. Default is 'value'.

    Returns:
    -------
    pd.DataFrame
        A DataFrame with columns: 'std', 'mean', 'cv', and 'Gene names' (protein identifiers).
        The 'Gene names' column is copied from the index.
    """
    cv_df = melted_df.groupby(protein_col)[value_col].agg(["std", "mean"])
    cv_df["cv"] = cv_df["std"] / cv_df["mean"]
    cv_df["Gene names"] = cv_df.index
    return cv_df


def protein_remover_by_sparcity(
    df: pd.DataFrame, minimum_samples_inside=20
) -> pd.DataFrame:
    """
    Remove proteins from the DataFrame based on sparsity threshold.

    Proteins (rows) with fewer than `minimum_samples_inside` non-NA values across samples (columns)
    are removed from the DataFrame.

    Parameters:
    ----------
    df : pd.DataFrame
        Input DataFrame with proteins as the index and samples as columns.

    minimum_samples_inside : int, optional
        Minimum number of samples (columns) in which a protein must have non-NA values
        to be retained. Proteins with fewer non-NA samples are removed.
        Default is 20.

    Returns:
    -------
    pd.DataFrame
        Filtered DataFrame containing only proteins meeting the sparsity criterion.
    """
    df = df.copy()
    nan_count = len(df.columns) - df.isna().sum(axis=1)
    df.drop(index=nan_count[nan_count < minimum_samples_inside].index, inplace=True)
    return df


def intersection(lst1: list, lst2: list):
    """
    Return the intersection of two lists as a list of unique elements present in both.

    Parameters:
    ----------
    lst1 : list
        The first list.
    lst2 : list
        The second list.

    Returns:
    -------
    list
        A list containing the unique elements common to both `lst1` and `lst2`.
    """
    return list(set(lst1) & set(lst2))


def log2fold_change_calculator(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the log2 fold change of intensities column-wise relative to the column mean.

    For each value in the DataFrame, this function subtracts the mean of its column,
    resulting in log2 fold changes relative to the average intensity across all samples per column.

    Parameters:
    ----------
    df : pd.DataFrame
        A DataFrame of log-transformed intensity values with samples as columns.

    Returns:
    -------
    pd.DataFrame
        A DataFrame of the same shape as `df`, containing log2 fold changes for each entry.
    """
    numpy_mat = df.to_numpy()
    res = numpy_mat - np.nanmean(numpy_mat, axis=0)
    res = pd.DataFrame(res)
    res.columns = df.columns
    res.index = df.index
    return res


def log2fold_change_calculator_LOO(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate leave-one-out (LOO) log2 fold changes column-wise relative to the mean excluding the current sample.

    For each sample (row), this function computes the mean of all other samples (excluding the current one)
    for each column, then calculates the difference between the sample’s value and this leave-one-out mean.

    Parameters:
    ----------
    df : pd.DataFrame
        A DataFrame of log-transformed intensity values with samples as rows and features as columns.

    Returns:
    -------
    pd.DataFrame
        A DataFrame of the same shape as `df`, containing the LOO log2 fold changes.
    """
    meidan_df_ar = df.to_numpy()
    result = np.zeros((meidan_df_ar.shape[0], meidan_df_ar.shape[1]))
    for i in range(meidan_df_ar.shape[0]):
        avs = np.delete(meidan_df_ar, np.s_[i], 0)  # delete row i of the matrix (LOO)
        means = avs.mean(axis=0)  # means across the columns after deleing row i
        result[i,] = (meidan_df_ar - means)[
            i,
        ]  # for vector i the difference to mean without considering that row
    result = pd.DataFrame(result)
    result.columns = df.columns
    result.index = df.index
    return result


def post_hoc_ANOVA(
    ANOVA_df: pd.DataFrame, protein_list, group_col="Brain region", p_adjust="fdr_bh"
):
    """
    Perform post-hoc pairwise t-tests after ANOVA for multiple proteins.

    For each protein in `protein_list`, this function performs a post-hoc pairwise t-test
    using the specified grouping column in the `ANOVA_df` DataFrame, applying multiple
    testing correction as specified by `p_adjust`.

    Parameters:
    ----------
    ANOVA_df : pd.DataFrame
        DataFrame where rows are samples and columns are protein measurements.

    protein_list : list
        List of protein column names in `ANOVA_df` to perform the post-hoc tests on.

    group_col : str, optional
        Name of the metadata column in `ANOVA_df` used to group samples for testing.
        Default is `'Brain region'`.

    p_adjust : str, optional
        Method for p-value adjustment for multiple comparisons. Default is `'fdr_bh'`
        (Benjamini-Hochberg false discovery rate).

    Returns:
    -------
    list of dict
        A list where each element is a dictionary with keys:
        - `'protein'`: the protein name,
        - `'post_hoc_res'`: the DataFrame of adjusted p-values from the post-hoc test.

    Notes:
    -----
    - Requires `sp.posthoc_ttest` from the `scikit-posthocs` package.
    """

    list_dictionaries = []
    for protein in protein_list:
        post_hoc = sp.posthoc_ttest(
            ANOVA_df, val_col=protein, group_col=group_col, p_adjust=p_adjust
        )
        dic = {"protein": protein, "post_hoc_res": post_hoc}

        list_dictionaries.append(dic)

    return list_dictionaries


def log_transform_intensities(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply log10 transformation to intensity values in the DataFrame.

    Zeros are replaced with NaN before transformation to avoid -inf values.

    Parameters:
    ----------
    df : pd.DataFrame
        DataFrame containing intensity values (must be numeric).

    Returns:
    -------
    pd.DataFrame
        DataFrame of the same shape with log10-transformed intensities. Zeros replaced by NaN.
    """
    df = np.log10(df.replace(0, np.nan))
    return df


def log2_transform_intensities(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply log2 transformation to intensity values in the DataFrame.

    Zeros are replaced with NaN before transformation to avoid -inf values.

    Parameters:
    ----------
    df : pd.DataFrame
        DataFrame containing intensity values (numeric).

    Returns:
    -------
    pd.DataFrame
        DataFrame of the same shape with log2-transformed intensities. Zeros replaced by NaN.
    """
    df = np.log2(df.replace(0, np.nan))
    return df


def calculate_median_z_scores(df: pd.DataFrame):
    """
    Calculate column-wise median-centered z-scores for a DataFrame.

    For each column, the z-score is computed by subtracting the column median and dividing
    by the column standard deviation, ignoring NaNs.

    Parameters:
    ----------
    df : pd.DataFrame
        Input DataFrame with numerical values. NaNs and infinite values will be handled.

    Returns:
    -------
    pd.DataFrame
        DataFrame of the same shape with median-centered z-scores computed column-wise.
    """
    print(df.shape)
    unimputerd_matrix = df.to_numpy()
    columns_names = df.columns
    rownames = df.index
    unimputerd_matrix[~np.isfinite(unimputerd_matrix)] = None

    def z_score_vector(temp: np.ndarray):
        temp_sd = np.nanstd(temp)
        temp_median = np.median(temp[~np.isnan(temp)])
        temp = (temp - temp_median) / temp_sd
        return temp

    final_matrix = np.apply_along_axis(z_score_vector, 0, unimputerd_matrix)
    final_df = pd.DataFrame(final_matrix)
    final_df.index = rownames
    final_df.columns = columns_names
    return final_df


def custom_imputation(input: pd.DataFrame) -> pd.DataFrame:
    """
    Custom imputation for triplicate samples in proteomics data.

    Rules:
    - If only one replicate out of three is expressed (non-NaN/non-zero), set all three replicates to zero.
    - If exactly two replicates are expressed and one is missing, impute the missing value with the median of the two expressed replicates.

    Assumptions:
    - Input DataFrame has samples as the index, with replicate identifiers '_1', '_2', '_3' suffixing sample names.
    - Columns correspond to proteins.

    Parameters:
    ----------
    df : pd.DataFrame
        DataFrame with samples as index and proteins as columns. Sample names must include '_1', '_2', or '_3' to identify replicates.

    Returns:
    -------
    pd.DataFrame
        DataFrame with the same shape as input but with missing replicate values imputed or zeroed as per the rules.
    """
    input = input.transpose()
    protein_list = input.columns.tolist()
    input["meta_data"] = input.index.str.replace("_[1-3]", "", regex=True)
    for protein in protein_list:
        kk = input[[protein, "meta_data"]].groupby("meta_data").count()
        for j in range(len(kk.index)):
            # if only one replicate out of 3 has positive intensity we will put 0 for all
            if kk.iloc[j, 0] < 2:
                input.loc[input["meta_data"] == kk.index[j], protein] = 0
            # if only one intensity out of 3 is None we will fill out with median of other 2
            if kk.iloc[j, 0] == 2:
                med = input.loc[input["meta_data"] == kk.index[j], protein].median()
                input.loc[input["meta_data"] == kk.index[j], protein] = input.loc[
                    input["meta_data"] == kk.index[j], protein
                ].fillna(med)
    input = input.drop(["meta_data"], axis=1)
    input = input.transpose()
    return input


def impute_normal_down_shift_distribution(
    unimputerd_df: pd.DataFrame,
    column_wise: bool = True,
    width: float = 0.3,
    downshift: float = 1.8,
    seed: int = 100,
) -> pd.DataFrame:
    """
    Perform missing value imputation by replacing NaNs with values drawn from a normal distribution
    shifted downward relative to the observed data distribution.

    The imputed distribution has mean shifted down by `downshift` standard deviations and scaled by `width`.

    Parameters:
    ----------
    unimputerd_df : pd.DataFrame
        DataFrame with missing values (NaNs) to be imputed.

    column_wise : bool, optional
        If True, imputation is done separately for each column using that column's statistics.
        If False, global mean and std across the entire DataFrame are used. Default is True.

    width : float, optional
        Scale factor for the standard deviation of the imputed distribution relative to the sample std.

    downshift : float, optional
        Number of standard deviations by which to downshift the mean of the imputed distribution.

    seed : int, optional
        Random seed for reproducibility.

    Returns:
    -------
    pd.DataFrame
        DataFrame with imputed values replacing NaNs.

    Reference:
    ---------
    Imputation method inspired by:
    https://rdrr.io/github/jdreyf/jdcbioinfo/man/impute_normal.html#google_vignette
    """
    import numpy as np

    print(unimputerd_df.shape)
    data = unimputerd_df.to_numpy(dtype=float)
    columns_names = unimputerd_df.columns
    rownames = unimputerd_df.index

    # Replace non-finite values with np.nan for consistent handling
    data[~np.isfinite(data)] = np.nan

    main_mean = np.nanmean(data)
    main_std = np.nanstd(data)

    np.random.seed(seed)

    def impute_normal_per_vector(temp: np.ndarray) -> np.ndarray:
        if column_wise:
            temp_mean = np.nanmean(temp)
            temp_sd = np.nanstd(temp)
        else:
            temp_mean = main_mean
            temp_sd = main_std

        shrinked_sd = width * temp_sd
        downshifted_mean = temp_mean - downshift * temp_sd
        n_missing = np.count_nonzero(np.isnan(temp))
        # Impute missing values with random draws from the shifted normal distribution
        temp[np.isnan(temp)] = np.random.normal(
            loc=downshifted_mean, scale=shrinked_sd, size=n_missing
        )
        return temp

    final_matrix = np.apply_along_axis(impute_normal_per_vector, 0, data)
    final_df = pd.DataFrame(final_matrix, index=rownames, columns=columns_names)
    return final_df


def anova_test(
    inputDF: pd.DataFrame, protein_peptide: List[str], metaDataColumn: str
) -> pd.DataFrame:
    """
    Perform one-way ANOVA tests for each protein/peptide across groups defined in metadata.

    Parameters:
    ----------
    inputDF : pd.DataFrame
        DataFrame where rows are samples/patients and columns are proteins/peptides.

    protein_peptide : List[str]
        List of protein/peptide column names to perform ANOVA on.

    metaDataColumn : str
        Name of the metadata column in `inputDF` that contains group labels for ANOVA.

    Returns:
    -------
    pd.DataFrame
        DataFrame with columns:
        - 'F_tests': ANOVA F-statistics per protein/peptide,
        - 'p_values': Corresponding p-values,
        - 'means_pergroup': List of group means per protein/peptide,
        - 'Majority protein IDs': Protein/peptide names,
        - 'fdr': FDR-adjusted p-values using Benjamini-Hochberg correction.
    """
    F_tests, p_values, mean_grps = [], [], []

    for gene in protein_peptide:
        # Extract relevant columns and drop duplicated columns and NA rows
        columns = [gene, metaDataColumn]
        grp = inputDF[columns].loc[:, ~inputDF[columns].columns.duplicated()].copy()
        grp = grp.dropna()

        # Group values by metaDataColumn for ANOVA
        grouped_values = grp.groupby(metaDataColumn)[gene].apply(list)
        group_means = grp.groupby(metaDataColumn)[gene].mean()
        average = list(group_means)

        # Perform ANOVA only if at least 2 groups exist
        if grp[metaDataColumn].nunique() >= 2:
            F, p = f_oneway(*grouped_values)
        else:
            F, p = 1, 1  # Default values when ANOVA cannot be performed

        F_tests.append(F)
        p_values.append(p)
        mean_grps.append(average)

    # Create result DataFrame
    p_df = pd.DataFrame(
        {
            "F_tests": F_tests,
            "p_values": p_values,
            "means_pergroup": mean_grps,
            "Majority protein IDs": protein_peptide,
        }
    )

    # Filter out rows with NaN p-values
    p_df = p_df[p_df["p_values"].notna()]

    # Multiple testing correction with FDR (Benjamini-Hochberg)
    _, fdr_corrected_pvals = fdrcorrection(
        p_df["p_values"], alpha=0.05, method="indep", is_sorted=False
    )
    p_df["fdr"] = fdr_corrected_pvals

    return p_df


def ROC_curve_analysis(
    labels: np.ndarray, scores: np.ndarray, curve_title: str, plot: bool = True
) -> float:
    """
    Compute and optionally plot the ROC curve for binary classification.

    Parameters:
    ----------
    labels : np.ndarray
        Array of true binary labels (0 or 1), where 1 indicates the positive class.

    scores : np.ndarray
        Array of predicted scores or probabilities for the positive class.
        Higher scores indicate higher likelihood of positive class.

    curve_title : str
        Title or label for the ROC curve plot.

    plot : bool, optional
        Whether to plot the ROC curve. Default is True.

    Returns:
    -------
    float
        Area Under the Curve (AUC) of the ROC curve.
    """
    fpr, tpr, thresholds = metrics.roc_curve(labels, scores)
    roc_auc = metrics.auc(fpr, tpr)

    if plot:
        display = metrics.RocCurveDisplay(
            fpr=fpr, tpr=tpr, roc_auc=roc_auc, estimator_name=curve_title
        )
        display.plot()
        plt.show()

    return roc_auc


def median_centering_ms1(merged_ms1_df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize MS1 intensity samples by median centering with batch-specific correction factors.

    This function computes the median intensity per sample considering only peptides
    detected in more than 70% of samples to avoid bias from low-abundance peptides.
    Each sample's intensities are then scaled by a correction factor so that all medians
    align to the global mean median.

    Parameters:
    ----------
    merged_ms1_df : pd.DataFrame
        DataFrame with proteins/peptides as rows and samples as columns containing intensity values.

    Returns:
    -------
    pd.DataFrame
        Normalized DataFrame with the same shape as input, with each sample scaled by its correction factor.
    """
    # Select peptides present in >70% of samples
    peptides_filter = merged_ms1_df.count(axis=1) > 0.7 * len(merged_ms1_df.columns)
    medians = merged_ms1_df.loc[peptides_filter].median(axis=0).to_dict()

    # Global mean median across samples
    mean_median = pd.Series(medians.values()).mean()

    df = merged_ms1_df.copy()

    for sample_name in merged_ms1_df.columns:
        correction_factor = mean_median / medians[sample_name]
        print(f"Correction factor for {sample_name}: {correction_factor:.3f}")
        df[sample_name] = df[sample_name] * correction_factor

    return df


def t_test(x: Tuple[float, ...], y: Tuple[float, ...]) -> Tuple[float, float]:
    """
    Perform an independent two-sample t-test between two numerical groups.

    Parameters:
    ----------
    x : tuple of floats
        First group of numerical observations.
    y : tuple of floats
        Second group of numerical observations.

    Returns:
    -------
    t_stat : float
        The computed t-statistic.
    p_value : float
        The two-tailed p-value for the test.
    """
    t_stat, p_value = ttest_ind(x, y, equal_var=False)  # Welch's t-test by default
    return t_stat, p_value


def one_vs_all_t_test(
    inputDF: pd.DataFrame,
    protein_peptide: List[str],
    favoriteentity: str,
    metaDataColumn: str,
) -> pd.DataFrame:
    """
    Perform a one-vs-all independent t-test for each protein/peptide comparing
    the favorite entity group against all other groups.

    Parameters:
    ----------
    inputDF : pd.DataFrame
        DataFrame with patients/samples as rows and proteins/peptides as columns.
    protein_peptide : List[str]
        List of protein/peptide column names on which to perform the t-tests.
    favoriteentity : str
        The group of interest (e.g., 'chordoma') to compare against all others.
    metaDataColumn : str
        Column name in inputDF that contains group labels for each sample.

    Returns:
    -------
    pd.DataFrame
        DataFrame containing t-statistics, p-values, group means, sample sizes,
        FDR-adjusted p-values, and direction ('up'/'down') indicating if favoriteentity
        group is higher or lower than other groups.
    """
    F_tests, p_values = [], []
    mean_grp1, mean_grp2 = [], []
    num_grp1, num_other_grps = [], []

    for gene in protein_peptide:
        # Subset relevant columns and drop NA rows
        df = inputDF[[gene, metaDataColumn]].dropna()

        # Groups for the test
        g1 = df[df[metaDataColumn] == favoriteentity][gene]
        g2 = df[df[metaDataColumn] != favoriteentity][gene]

        # Perform t-test
        f, p = t_test(tuple(g1), tuple(g2))

        F_tests.append(f)
        p_values.append(p)
        mean_grp1.append(g1.mean())
        mean_grp2.append(g2.mean())
        num_grp1.append(len(g1))
        num_other_grps.append(len(g2))

    p_df = pd.DataFrame(
        {
            "t_statistics": F_tests,
            "p_values": p_values,
            "means_group1": mean_grp1,
            "means_group2": mean_grp2,
            "num_samples_groups_interest": num_grp1,
            "num_sample_other_groups": num_other_grps,
            "Gene Names": protein_peptide,
        }
    )

    # Filter out any rows with NaN p-values
    p_df = p_df[p_df["p_values"].notna()]

    # Adjust p-values for multiple testing using FDR (Benjamini-Hochberg)
    _, fdr_corrected_pvals = fdrcorrection(
        p_df["p_values"], alpha=0.05, method="indep", is_sorted=False
    )
    p_df["fdr"] = fdr_corrected_pvals

    # Determine direction of change
    p_df["up_down"] = [
        "up" if m1 >= m2 else "down"
        for m1, m2 in zip(p_df["means_group1"], p_df["means_group2"])
    ]

    return p_df


def univariate_ROC_analysis_by_CV_permutation(
    pre: pd.DataFrame,
    favoriteentity: str,
    kFold: int = 5,
    repeats: int = 10,
    threshold: float = 0.5,
    scores: str = "scores",
    labels: str = "labels",
) -> float:
    """
    Compute the stability percentage of ROC AUCs above a given threshold using repeated stratified k-fold cross-validation.

    Parameters:
    ----------
    pre : pd.DataFrame
        DataFrame containing prediction scores and true labels.
        Must include columns named as specified by `scores` and `labels`.

    favoriteentity : str
        The label considered as the positive class.

    kFold : int, optional
        Number of folds for cross-validation. Default is 5.

    repeats : int, optional
        Number of repeated cross-validation runs. Default is 10.

    threshold : float, optional
        Threshold for considering AUC as stable. Default is 0.5.

    scores : str, optional
        Column name in `pre` containing the prediction scores. Default is 'scores'.

    labels : str, optional
        Column name in `pre` containing the true labels. Default is 'labels'.

    Returns:
    -------
    float
        Percentage of AUCs that are above `threshold` or below `1 - threshold` across all CV splits.
    """
    # Extract scores and labels
    x = pre[scores].to_numpy()
    y = pre[labels].copy()

    # Binarize labels: favoriteentity = 1, others = 0
    y = y.apply(lambda lbl: 1 if lbl == favoriteentity else 0).to_numpy()

    skf = RepeatedStratifiedKFold(n_splits=kFold, n_repeats=repeats, random_state=42)
    aucs = []

    for train_index, test_index in skf.split(x, y):
        # Compute AUC on training split (or you may want test split)
        auc = ROC_curve_analysis(
            y[train_index], x[train_index], curve_title="", plot=False
        )
        aucs.append(auc)

    aucs_df = pd.DataFrame({"auc": aucs}).dropna()

    # Count AUCs above threshold or below (1-threshold)
    fulfilled = aucs_df[
        (aucs_df["auc"] > threshold) | (aucs_df["auc"] < (1 - threshold))
    ].shape[0]

    total = kFold * repeats
    stability_percent = (fulfilled / total) * 100

    return stability_percent


def plot_cv_per_condition(
    df: pd.DataFrame,
    condition: str,
    Samplename2TMTchannel: Dict[str, list],
    data_Set_name: str,
) -> None:
    """
    Plot cumulative histogram of coefficient of variation (CV) percentages for a given condition
    using Reporter intensity corrected channels.

    Parameters:
    -----------
    df : pd.DataFrame
        The TMT evidence or proteinGroup DataFrame.

    condition : str
        The name of the condition to analyze.

    Samplename2TMTchannel : dict
        Dictionary mapping condition names to lists of TMT channel names.

    data_Set_name : str
        The dataset name repeated after "Reporter intensity corrected" columns.
        Used to filter relevant intensity columns.

    Returns:
    --------
    None
        Displays the cumulative histogram plot of CV percentages.
    """
    sub_Df = _extract_values_per_group(
        df, condition, Samplename2TMTchannel, data_Set_name
    )
    mean = sub_Df.filter(regex="Reporter intensity corrected [1-9]+").mean(axis=1)
    stds = sub_Df.filter(regex="Reporter intensity corrected [1-9]+").std(axis=1)
    cvs = stds / mean
    plot = plt.hist(
        cvs * 100,
        cumulative=True,
        bins=np.linspace(0, 100, 1000),
        histtype="step",
        density=True,
        label=condition,
    )
    plt.legend()
    plt.xlim([0, 100])
    plt.xlabel("% CV")
    plt.ylabel("Cumulative frequency")


def seaborn_volcano(df,fc_thresh = 0.25,
                     p_thresh = 0.05,
                     xaxis=1,
                     draw_dashed_lines = True,
                     p_value_col = "p_values",
                     foldchange_col = "delta_mean",
                     gene_col = "Gene Names",
                     title="Volcano Plot",
                     where_to_save = None ):
    """
    Create a volcano plot using Seaborn to visualize statistical significance
    (p-values) versus magnitude of change (fold change) for features such as genes or proteins.

    The plot highlights three categories of points:
      - "up": Fold change above `fc_thresh` and p-value ≤ `p_thresh`
      - "down": Fold change below `-fc_thresh` and p-value ≤ `p_thresh`
      - "ns": Not significant

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing at least the columns specified in
        `p_value_col`, `foldchange_col`, and `gene_col`.
    fc_thresh : float, default=0.25
        Fold change threshold for significance classification.
        Values greater than this (in absolute value) are considered significant if p-value passes.
    p_thresh : float, default=0.05
        P-value threshold for statistical significance.
    xaxis : float, default=1
        X-axis range limit for plotting threshold lines.
    draw_dashed_lines : bool, default=True
        Whether to draw dashed threshold lines for fold change and p-value cutoffs.
    p_value_col : str, default="p_values"
        Column name in `df` containing p-values.
    foldchange_col : str, default="delta_mean"
        Column name in `df` containing fold change values.
    gene_col : str, default="Gene Names"
        Column name in `df` containing gene/protein identifiers for labeling.
    title : str, default="Volcano Plot"
        Title for the plot.
    where_to_save : str or None, default=None
        File path to save the plot. If None, the plot is displayed instead.

    Returns
    -------
    None
        Displays or saves the volcano plot.

    Notes
    -----
    - p-values are transformed to `-log10(p)` for the y-axis.
    - Only points meeting significance thresholds are labeled.
    - Color scheme:
        - Red: "up" (significant positive fold change)
        - Blue: "down" (significant negative fold change)
        - Grey: "ns" (not significant)
    """

    
    df = df.copy()
    df["neg_log10_pval"] = -np.log10(df[p_value_col])

    # Classify points
    def classify(row):
        if row[foldchange_col] > fc_thresh and row[p_value_col] <= p_thresh:
            return "up"
        elif row[foldchange_col] < -fc_thresh and row[p_value_col] <= p_thresh:
            return "down"
        else:
            return "ns"

    df["type"] = df.apply(classify, axis=1)

    # --- Plot volcano ---
    plt.figure(figsize=(10, 8))
    ax = sns.scatterplot(
        data=df,
        x=foldchange_col,
        y="neg_log10_pval",
        hue="type",
        palette={"up": "red", "down": "blue", "ns": "grey"},
        alpha=0.7
    )

    # Thresholds
    y_cutoff = -np.log10(p_thresh)
    y_max = df["neg_log10_pval"].max()

    # Horizontal p-value cutoff line (short)
    if draw_dashed_lines:
        ax.hlines(
            y=y_cutoff,
            xmin=-xaxis,
            xmax=-fc_thresh,
            colors="black",
            linestyles="--"
        )

        ax.hlines(
            y=y_cutoff,
            xmin=fc_thresh,
            xmax=xaxis,
            colors="black",
            linestyles="--"
        )

        # Vertical fold-change cutoff lines (short)
        ax.vlines(
            x=fc_thresh,
            ymin=y_cutoff,
            ymax=y_max,
            colors="black",
            linestyles="--"
        )
        ax.vlines(
            x=-fc_thresh,
            ymin=y_cutoff,
            ymax=y_max,
            colors="black",
            linestyles="--"
        )

    # Label top 5 most significant points
    top_labels = df[df.p_values <= p_thresh]
    for _, row in top_labels.iterrows():
        ax.text(
            row[foldchange_col],
            row["neg_log10_pval"],
            row[gene_col],
            fontsize=12,
            ha="right"
        )

    ax.set(
        xlabel="log2(Fold Change)",
        ylabel=f"-log10{p_value_col}",
        title=title
    )
    plt.tight_layout()
    if where_to_save:
        plt.savefig(where_to_save)
    else:
        plt.show()



def make_pair_combinations(items):
    """
    Generate all unique pairwise combinations from a list of items.

    Parameters
    ----------
    items : list
        List of elements (e.g., strings, numbers) from which to create pairs.

    Returns
    -------
    list of list
        A list containing all possible unique pairs, where each pair is represented
        as a two-element list. Order within each pair follows the original input order.

    Examples
    --------
    >>> make_pair_combinations(["A", "B", "C"])
    [['A', 'B'], ['A', 'C'], ['B', 'C']]

    Notes
    -----
    - Uses `itertools.combinations`, so no repeated elements and no reversed duplicates.
    - If `items` has fewer than 2 elements, the result will be an empty list.
    """
    pairs = list(itertools.combinations(items, 2))
    return [list(x) for x in pairs]



def median_centering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize samples by centering their distributions using median scaling.

    Each sample (column) is multiplied by a correction factor defined as the ratio
    of the average median of reference channels to the sample median. This aligns
    sample medians around the same central value.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame of batch intensities with samples as columns and features (e.g., reporter channels)
        as rows. Zero values are treated as missing and ignored in median calculations.

    Returns:
    --------
    pd.DataFrame
        Median-centered DataFrame with the same shape as input.
    """
    # Replace zeros with NaN to exclude them from median calculation
    df = df.replace(0, np.nan)

    # Select rows with at most 3 missing values to calculate reliable medians per column
    valid_rows = df.isna().sum(axis=1) <= 3
    medians = df.loc[valid_rows].median(axis=0)

    print("Sample medians used for correction factor calculation:")
    print(medians)

    # Calculate correction factor and apply per sample (column)
    correction_factors = medians.mean() / medians
    normalized_df = df * correction_factors

    return normalized_df


def volcanoplot(
    df: pd.DataFrame, cutoff: Optional[float] = None, save_path: Optional[str] = None
) -> None:
    """
    Create and optionally save an interactive volcano plot using Plotly.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing at least the following columns:
        - 'delta_mean': log2 fold change values (x-axis).
        - 'pP_VALUE': -log10 transformed p-values or Q-values (y-axis).
        - 'type': categorical variable for coloring points (e.g., 'up', 'down', 'ns').
        - 'proteins': names for hover labels.

    cutoff : float, optional
        Y-axis cutoff to add a horizontal reference line (e.g., significance threshold).

    save_path : str, optional
        If provided, saves the interactive plot as an HTML file to this path.

    Returns:
    --------
    None
        Displays the interactive plot.
    """
    fig = px.scatter(
        df, x="delta_mean", y="pP_VALUE", color="type", hover_name="proteins"
    )
    if cutoff:
        fig.add_hline(y=cutoff)
    if save_path:
        fig.write_html(save_path)
    fig.show()


def _extract_values_per_group_per_protein(
    df: pd.DataFrame,
    group_name: str,
    protein_name: str,
    Samplename2TMTchannel,
    data_Set_name,
):
    group_channels = [str(x) for x in Samplename2TMTchannel[group_name]]
    group_channels = [str(f"{x} {data_Set_name}") for x in group_channels]
    columns_names = [str(f"Reporter intensity corrected {x}") for x in group_channels]
    return tuple(df.loc[protein_name, columns_names].dropna())


def _extract_values_per_group(
    df: pd.DataFrame, group_name: str, Samplename2TMTchannel, data_Set_name
):
    group_channels = [str(x) for x in Samplename2TMTchannel[group_name]]
    group_channels = [str(f"{x} {data_Set_name}") for x in group_channels]
    columns_names = [str(f"Reporter intensity corrected {x}") for x in group_channels]
    return df.loc[:, columns_names]


def get_t_across_all_proteins(
    df: pd.DataFrame,
    group_1_name: str,
    group_2_name: str,
    data_Set_name: str,
    Samplename2TMTchannel: Dict[str, Any],
) -> pd.DataFrame:
    """
    Perform t-tests across all proteins between two groups and return statistics with FDR correction.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with proteins as index and samples as columns.

    group_1_name : str
        Name of the first group to compare.

    group_2_name : str
        Name of the second group to compare.

    data_Set_name : str
        Dataset identifier used in value extraction.

    Samplename2TMTchannel : dict
        Mapping of sample names to TMT channel lists.

    Returns:
    --------
    pd.DataFrame
        DataFrame with columns:
        - 'proteins': protein names
        - 'p_values': p-values from t-test
        - 't_statistics': t statistics
        - 'g1_mean': mean of group 1
        - 'g2_mean': mean of group 2
        - 'FDR_correction': adjusted p-values (FDR)
        - 'pP_VALUE': transformed adjusted p-values (using _pfunclog)
        - 'delta_mean': difference of means (g1_mean - g2_mean)
        - 'type': 'up' if delta_mean > 0 else 'down'
    """
    protein_names = df.index.to_list()
    final_df = pd.DataFrame({"proteins": protein_names})

    # Initialize columns with None or NaN
    final_df["p_values"] = pd.NA
    final_df["t_statistics"] = pd.NA
    final_df["g1_mean"] = pd.NA
    final_df["g2_mean"] = pd.NA

    for i, protein_name in enumerate(final_df["proteins"]):
        g1_tuple = _extract_values_per_group_per_protein(
            df, group_1_name, protein_name, Samplename2TMTchannel, data_Set_name
        )
        g2_tuple = _extract_values_per_group_per_protein(
            df, group_2_name, protein_name, Samplename2TMTchannel, data_Set_name
        )
        try:
            t_stat, p_val, mean_g1, mean_g2 = _t_test(g1_tuple, g2_tuple)
            final_df.at[i, "p_values"] = p_val
            final_df.at[i, "t_statistics"] = t_stat
            final_df.at[i, "g1_mean"] = mean_g1
            final_df.at[i, "g2_mean"] = mean_g2
        except Exception:
            # You can optionally log the error here
            continue

    # Drop rows with missing key results
    final_df = final_df.dropna(subset=["p_values", "g1_mean", "g2_mean"])

    # FDR correction
    pvals = pd.to_numeric(final_df["p_values"]).to_numpy()
    _, fdr_corrected_pvals = fdrcorrection(
        pvals, alpha=0.05, method="indep", is_sorted=False
    )
    final_df["FDR_correction"] = fdr_corrected_pvals

    # Apply p-value transformation (assumed _pfunclog function)
    final_df["pP_VALUE"] = final_df["FDR_correction"].apply(_pfunclog)

    # Compute difference of means and direction
    final_df["delta_mean"] = final_df["g1_mean"] - final_df["g2_mean"]
    final_df["type"] = final_df["delta_mean"].apply(lambda x: "up" if x > 0 else "down")

    return final_df


def unnest_proteingroups(df: pd.DataFrame) -> pd.DataFrame:
    """
    Split multi-protein group entries in the DataFrame index (separated by ';')
    into separate rows, duplicating associated data for each protein group.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with protein groups as the index, where some index entries may contain
        multiple protein names separated by semicolons (';').

    Returns:
    --------
    pd.DataFrame
        Expanded DataFrame where each protein group has its own row, with data duplicated
        accordingly. The new index will be the individual protein group names.
    """
    # Create a copy to avoid modifying original DataFrame
    temp_df = df.copy()

    # Split the index strings by ';' into lists
    temp_df["protein_group_split"] = temp_df.index.str.split(";")

    # Explode the lists so each element gets its own row
    temp_df = temp_df.explode("protein_group_split")

    # Set the exploded protein group as the new index
    temp_df = temp_df.set_index("protein_group_split")

    # Optionally rename the index name if you want
    temp_df.index.name = "protein_group"

    return temp_df


def _t_test(x: tuple, y: tuple) -> tuple:
    """
    Performs t_test from two numerical tuples as the two groups
    :returns : F_statistics and P_values as a tuple

    """
    avg1 = mean(x)
    avg2 = mean(y)
    F, p = ttest_ind(x, y)
    return F, p, avg1, avg2


def _log(x):
    try:
        return math.log2(x)
    except:
        return 0


def _pfunclog(x):
    try:
        return math.log10(1 / x)
    except:
        return None


def make_cv_plot(df: pd.DataFrame) -> None:
    """
    Create and display a cumulative distribution plot of the coefficient of variation (CV).

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing a 'cv' column representing coefficient of variation values
        (expected as decimal fractions, e.g., 0.05 for 5%).

    Raises:
    -------
    ValueError:
        If the 'cv' column is not present in the DataFrame.
    """

    if not "cv" in df.columns:
        raise ValueError("cv should be in the columns")

    df = df.dropna(subset=["cv"])
    plt.hist(
        df["cv"] * 100,
        cumulative=True,
        bins=np.linspace(0, 100, 1000),
        histtype="step",
        density=True,
    )
    plt.legend()
    plt.xlim([0, 100])
    plt.xlabel("% CV")
    plt.ylabel("Cumulative frequency")
    plt.tight_layout()
