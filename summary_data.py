import time

def typewriter_effect(text, delay=0.02):

    for word in text.split():
        yield word + " "
        time.sleep(delay)
    yield "\n"



def generate_summary(df):
    num_rows, num_cols = df.shape
    missing_values = df.isnull().sum()
    total_missing_values = missing_values.sum()
    duplicate_rows = df.duplicated().sum()
    numeric_cols = df.select_dtypes(include=["number"])
    categorial_cols = df.select_dtypes(include=["object"])

    # Yielding each line with typewriter effect
    yield from typewriter_effect(f"📊 **Dataset Overview**\n\n")
    yield from typewriter_effect(f"- This dataset has **{num_rows} rows** and **{num_cols} columns**.\n")
    yield from typewriter_effect(f"- There are **{total_missing_values} missing values** spread across {len(missing_values[missing_values > 0])} columns.\n")
    yield from typewriter_effect(f"- The dataset contains **{duplicate_rows} duplicate rows**.\n\n")
    
    time.sleep(0.5)

    yield from typewriter_effect(f"📌 **Column Data Types**\n\n")
    yield from typewriter_effect(f"- **Numeric Columns**: {len(numeric_cols.columns)}\n")
    yield from typewriter_effect(f"- **Categorical Columns**: {len(categorial_cols.columns)}\n\n")
    
    time.sleep(0.5)

    if not numeric_cols.empty:
        mean_values = numeric_cols.mean()
        median_values = numeric_cols.median()
        std_dev = numeric_cols.std()

        yield from typewriter_effect(f"📈 **Statistics for Numeric Columns**\n\n")
        for col in numeric_cols.columns:
            yield from typewriter_effect(f"- **{col}**: Mean = {mean_values[col]:.2f}, Median = {median_values[col]:.2f}, Std Dev = {std_dev[col]:.2f}\n")
        yield "\n"

        time.sleep(0.5)

    if not categorial_cols.empty:
        yield from typewriter_effect(f"🗂 **Most Frequent Values in Categorical Columns**\n\n")
        for column in categorial_cols.columns:
            most_common = df[column].mode()[0]
            yield from typewriter_effect(f"- **{column}**: Most common value = `{most_common}`\n")
        yield "\n"

        time.sleep(0.5)

    yield from typewriter_effect(f"⚠️ **Missing Values Breakdown**\n\n")
    for col, missing in missing_values.items():
        if missing > 0:
            percent_missing = (missing / num_rows) * 100
            yield from typewriter_effect(f"- **{col}**: {missing} missing values ({percent_missing:.2f}%)\n")
    yield "\n"

    time.sleep(0.5)

    if not numeric_cols.empty:
        yield from typewriter_effect(f"📉 **Outlier Detection (IQR Method)**\n\n")
        for col in numeric_cols.columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col].count()
            if outliers > 0:
                yield from typewriter_effect(f"- **{col}**: {outliers} potential outliers detected.\n")
        yield "\n"

        time.sleep(0.5)

    if len(numeric_cols.columns) > 1:
        yield from typewriter_effect(f"📊 **Correlation Analysis** (Top 3 Strongest Correlations)\n\n")
        correlation_matrix = numeric_cols.corr().abs()
        correlations = (
            correlation_matrix.unstack()
            .sort_values(ascending=False)
            .drop_duplicates()
        )
        top_correlations = correlations[correlations < 1].head(3)

        for (col1, col2), corr_value in top_correlations.items():
            yield from typewriter_effect(f"- **{col1} & {col2}**: Correlation = {corr_value:.2f}\n")
        yield "\n"

    yield from typewriter_effect("**Dataset Summary:**\n\n")  
    yield from typewriter_effect("Here's an overview of the dataset's statistics:\n")  
    yield df.describe()

    yield from typewriter_effect(f"✅ **Summary Completed!** 🎉\n")
