import pandas as pd
import numpy as np
import re

prod_file = "Palay and Corn- Volume of Production in Metric Tons by Ecosystem-Croptype, Quarter, Semester, Region and Province, 1987-2026.csv"
price_file = "Cereals- Farmgate Prices by Geolocation, Commodity, Year and Period.csv"

def inspect_and_group_variables(file_path, dataset_label):
    # Load dataset skipping top PSA banner
    df = pd.read_csv(file_path, skiprows=1, na_values="..", thousands=",")
    
    print("=" * 70)
    print(f"DATASET ANALYSIS: {dataset_label.upper()}")
    print("=" * 70)
    
    # 1. Exact Shape
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"Duplicate Rows: {df.duplicated().sum()}\n")
    
    # 2. Identify Non-Time Identifier Columns vs. Time Columns
    # Regular expression matches 4-digit years (e.g., 2010, 2010 Q1, 2010 Semester 1)
    time_cols = [c for c in df.columns if re.search(r"\b(19|20)\d{2}\b", str(c))]
    id_cols = [c for c in df.columns if c not in time_cols]
    
    table_rows = []
    
    # Process Non-Time Identifier Columns
    for col in id_cols:
        dtype = str(df[col].dtype)
        missing_count = df[col].isna().sum()
        missing_pct = (missing_count / len(df)) * 100
        
        issues = []
        if missing_count > 0:
            issues.append(f"{missing_count} NaNs ({missing_pct:.1f}%)")
        if col == "Geolocation":
            issues.append("Contains leading dots (..) for administrative levels")
            target_q = "Q1, Q2, Q3 (Spatial Granularity)"
        else:
            target_q = "Q1, Q2 (Filtering & Categorization)"
            
        table_rows.append({
            "Variable / Column Group": col,
            "Data Type": dtype,
            "Missing Values": f"{missing_count} ({missing_pct:.1f}%)",
            "Quality Issues": "; ".join(issues) if issues else "None identified",
            "Target Question": target_q
        })
        
    # Aggregate Time-Series Columns (e.g., Years / Quarters 2010–2026)
    if time_cols:
        # Limit analysis to target analytical window (2010 to 2026)
        target_time_cols = [c for c in time_cols if any(str(yr) in c for yr in range(2010, 2027))]
        cols_to_analyze = target_time_cols if target_time_cols else time_cols
        
        time_sub_df = df[cols_to_analyze]
        total_time_cells = time_sub_df.size
        total_time_nans = time_sub_df.isna().sum().sum()
        missing_pct = (total_time_nans / total_time_cells) * 100
        
        # Check overall data type across these columns
        dtypes_found = set(time_sub_df.dtypes.astype(str))
        dtype_str = ", ".join(dtypes_found)
        
        start_period = cols_to_analyze[0]
        end_period = cols_to_analyze[-1]
        
        issues = [f"{total_time_nans} total NaNs ({missing_pct:.1f}%) across all time cells"]
        if "object" in dtypes_found:
            issues.append("Some time columns contain non-numeric formatting or unparsed strings")
            
        table_rows.append({
            "Variable / Column Group": f"Time-Series Data ({start_period} to {end_period}) [{len(cols_to_analyze)} columns]",
            "Data Type": dtype_str,
            "Missing Values": f"{total_time_nans} ({missing_pct:.1f}% overall)",
            "Quality Issues": "; ".join(issues),
            "Target Question": "Q1, Q2, Q3 (Production & Prices over time)"
        })
        
    var_table = pd.DataFrame(table_rows)
    return df, var_table

# Run compact inspection
df_prod, var_table_prod = inspect_and_group_variables(prod_file, "Palay & Corn Production")
df_price, var_table_price = inspect_and_group_variables(price_file, "Cereals Farmgate Prices")

# Print Compact Variable Tables
print("PRODUCTION DATASET VARIABLE TABLE:")
print(var_table_prod.to_markdown(index=False))

print("\nPRICES DATASET VARIABLE TABLE:")
print(var_table_price.to_markdown(index=False))
