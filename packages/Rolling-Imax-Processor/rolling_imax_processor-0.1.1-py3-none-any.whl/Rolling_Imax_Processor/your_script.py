import os
import re
import pandas as pd
from collections import defaultdict

# ========== [2] UTILITY FUNCTIONS ==========
def classify_intensity(val):
    if val == 0 or pd.isna(val):
        return None
    return f'I{min(int(val), 60)}'

def extract_date_from_filename(filename):
    match = re.search(r'(\d{2}[.\-]\d{2}[.\-]\d{4})', filename)
    if match:
        try:
            return pd.to_datetime(match.group(1), dayfirst=True)
        except:
            return pd.NaT
    return pd.NaT

def read_excel(file_path):
    ext = file_path.lower().split('.')[-1]
    engine = 'xlrd' if ext == 'xls' else 'openpyxl'
    return pd.read_excel(file_path, engine=engine)

def fill_empty_with_zero(df):
    """Replace blanks, NaN, NaT with 0."""
    return df.replace(r'^\s*$', 0, regex=True).fillna(0)

# ========== [3] PROCESS A SINGLE FILE ==========
def process_file(file_path, file_name):
    df = read_excel(file_path)

    if 'Intensity (1min)' not in df.columns or 'DateTime' not in df.columns:
        print(f"⚠️ Skipping (missing columns): {file_name}")
        return None

    # Clean and prepare
    df['Intensity (1min)'] = df['Intensity (1min)'].replace(999999, pd.NA)
    df = df.dropna(subset=['Intensity (1min)', 'DateTime'])
    df['Timestamp'] = pd.to_datetime(df['DateTime'], errors='coerce')
    df = df.dropna(subset=['Timestamp'])
    df = df.sort_values('Timestamp')

    # Classification
    df['Intensity_Class'] = df['Intensity (1min)'].apply(classify_intensity)
    df = df.dropna(subset=['Intensity_Class'])

    imax_detailed = []
    prev_imax_val = pd.NA
    prev_imax_time = pd.NaT

    for i in range(1, 61):
        class_label = f'I{i}'
        df_class = df[df['Intensity_Class'] == class_label].copy().reset_index(drop=True)

        if len(df_class) >= 2:
            df_class['Rolling_Sum_2'] = df_class['Intensity (1min)'].rolling(window=2).sum()
            max_val = df_class['Rolling_Sum_2'].max()
            max_row = df_class[df_class['Rolling_Sum_2'] == max_val].iloc[0]
            max_time = max_row['Timestamp']
            prev_imax_val = max_val
            prev_imax_time = max_time

        elif len(df_class) == 1:
            max_val = df_class['Intensity (1min)'].iloc[0]
            max_time = df_class['Timestamp'].iloc[0]
            prev_imax_val = max_val
            prev_imax_time = max_time

        else:
            # No data for this class, carry forward previous Imax
            max_val = prev_imax_val
            max_time = prev_imax_time

        if pd.notna(max_val) and max_val == 0:
            max_val = pd.NA

        imax_detailed.append({
            'Intensity_Class': class_label,
            'Timestamp': max_time,
            'Rolling_Sum_2_Max': max_val,
            'Source_File': file_name
        })

    detailed_df = pd.DataFrame(imax_detailed)
    date = extract_date_from_filename(file_name)
    detailed_df['Date'] = date
    detailed_df['Month'] = date.strftime('%Y-%m') if pd.notnull(date) else 'Unknown'

    # 🔹 Divide Rolling_Sum_2_Max by numeric part of Intensity_Class
    detailed_df['Rolling_Sum_2_Max'] = detailed_df.apply(
        lambda row: row['Rolling_Sum_2_Max'] / int(row['Intensity_Class'][1:])
        if pd.notna(row['Rolling_Sum_2_Max']) else row['Rolling_Sum_2_Max'],
        axis=1
    )

    return detailed_df

# ========== [4] PROCESS ALL FILES GROUPED BY MONTH ==========
def process_all_files_by_month(base_dir):
    monthly_data = defaultdict(list)

    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(('.xls', '.xlsx')) and 'Processed' not in root:
                file_path = os.path.join(root, file)
                print(f"📂 Processing: {file_path}")

                try:
                    result_df = process_file(file_path, file)
                    if result_df is not None:
                        month_key = result_df['Month'].iloc[0]
                        monthly_data[month_key].append(result_df)

                except Exception as e:
                    print(f"❌ Error processing {file}: {e}")

    return monthly_data

# ========== [5] CREATE PIVOT TABLE ==========
def create_pivot(df):
    pivot = df.pivot_table(
        index='Date',
        columns='Intensity_Class',
        values='Rolling_Sum_2_Max',
        aggfunc='max'
    ).reset_index()

    all_classes = [f'I{i}' for i in range(1, 61)]
    for col in all_classes:
        if col not in pivot.columns:
            pivot[col] = 0

    ordered_cols = ['Date'] + all_classes
    pivot = pivot[ordered_cols]

    return pivot

# ========== [6] SAVE RESULTS ==========
def save_monthly_and_master(monthly_data, output_dir):
    all_months_combined = []

    for month, dfs in sorted(monthly_data.items()):
        combined = pd.concat(dfs, ignore_index=True)

        combined = combined.sort_values(
            ['Date', 'Intensity_Class'],
            key=lambda col: col.map(lambda x: int(x[1:]) if isinstance(x, str) and x.startswith('I') else x)
        )

        combined = fill_empty_with_zero(combined)

        month_filename = f"summary_{month}.xlsx"
        combined.to_excel(os.path.join(output_dir, month_filename), index=False)
        print(f"📘 Saved monthly summary: {month_filename}")

        pivot = create_pivot(combined)
        pivot = fill_empty_with_zero(pivot)
        pivot_filename = f"pivot_summary_{month}.xlsx"
        pivot.to_excel(os.path.join(output_dir, pivot_filename), index=False)
        print(f"📗 Saved monthly pivot: {pivot_filename}")

        all_months_combined.append(combined)

    if all_months_combined:
        master = pd.concat(all_months_combined, ignore_index=True)
        master = master.sort_values(
            ['Date', 'Intensity_Class'],
            key=lambda col: col.map(lambda x: int(x[1:]) if isinstance(x, str) and x.startswith('I') else x)
        )
        master = fill_empty_with_zero(master)

        master_file = os.path.join(output_dir, 'master_monthly_summary_cleaned.xlsx')
        master.to_excel(master_file, index=False)
        print(f"\n📙 Master summary saved: master_monthly_summary_cleaned.xlsx")

        master_pivot = create_pivot(master)
        master_pivot = fill_empty_with_zero(master_pivot)
        master_pivot_file = os.path.join(output_dir, 'master_monthly_pivot_summary.xlsx')
        master_pivot.to_excel(master_pivot_file, index=False)
        print(f"📕 Master pivot summary saved: master_monthly_pivot_summary.xlsx")
    else:
        print("⚠️ No data to save.")

# ========== [7] MAIN ==========
def main(base_dir=None, output_dir=None):
    if base_dir is None:
        base_dir = input("Enter the base directory path for your data: ").strip()
    if output_dir is None:
        output_dir = os.path.join(base_dir, 'Processed_Monthly_Cleaned')
    os.makedirs(output_dir, exist_ok=True)

    print("🚀 Starting processing (Rolling Imax for I1–I60 with division by class number)...\n")
    monthly_data = process_all_files_by_month(base_dir)
    save_monthly_and_master(monthly_data, output_dir)
    print("\n✅ All done.")

# ========== RUN ==========
if __name__ == '__main__':
    main()
