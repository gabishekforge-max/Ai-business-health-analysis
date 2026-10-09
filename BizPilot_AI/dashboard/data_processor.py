import pandas as pd
import numpy as np


REQUIRED_COLUMNS = {
    'Date',
    'Product',
    'Category',
    'Quantity',
    'Unit_Price',
    'Cost_Price',
    'Revenue',
    'Stock'
}


def process_business_csv(file_input):

    # --------------------------------------------------
    # 1. READ CSV FILE
    # --------------------------------------------------
    try:
        df = pd.read_csv(
            file_input,
            encoding='utf-8-sig',
            sep=','
        )

    except UnicodeDecodeError:
        try:
            df = pd.read_csv(
                file_input,
                encoding='latin1',
                sep=','
            )
        except Exception as e:
            return None, f"Could not parse CSV file: {str(e)}"

    except Exception as e:
        return None, f"Could not parse CSV file: {str(e)}"


    # --------------------------------------------------
    # 2. CHECK EMPTY FILE
    # --------------------------------------------------
    if df.empty:
        return None, "Uploaded CSV file is completely empty."


    # --------------------------------------------------
    # 3. CLEAN COLUMN NAMES
    # --------------------------------------------------
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace('\ufeff', '', regex=False)
    )


    # --------------------------------------------------
    # 4. CHECK REQUIRED COLUMNS
    # --------------------------------------------------
    missing_cols = REQUIRED_COLUMNS - set(df.columns)

    if missing_cols:
        return None, (
            "Missing required columns: "
            + ", ".join(sorted(missing_cols))
        )


    # --------------------------------------------------
    # 5. REMOVE EMPTY ROWS
    # --------------------------------------------------
    df.dropna(how='all', inplace=True)


    # --------------------------------------------------
    # 6. REMOVE DUPLICATE ROWS
    # --------------------------------------------------
    df.drop_duplicates(inplace=True)


    # --------------------------------------------------
    # 7. CONVERT DATE
    # --------------------------------------------------
    try:
        df['Date'] = pd.to_datetime(
            df['Date'],
            errors='coerce'
        )

    except Exception:
        return None, "Date column could not be processed."


    # Check invalid dates
    if df['Date'].isnull().any():
        return None, "Date column contains invalid date format."


    # --------------------------------------------------
    # 8. NUMERIC COLUMNS
    # --------------------------------------------------
    num_cols = [
        'Quantity',
        'Unit_Price',
        'Cost_Price',
        'Revenue',
        'Stock'
    ]


    for col in num_cols:

        # Remove commas and currency symbols
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(',', '', regex=False)
            .str.replace('₹', '', regex=False)
            .str.replace('$', '', regex=False)
            .str.strip()
        )

        df[col] = pd.to_numeric(
            df[col],
            errors='coerce'
        )


    # --------------------------------------------------
    # 9. HANDLE MISSING NUMERIC VALUES
    # --------------------------------------------------
    df['Quantity'] = df['Quantity'].fillna(0)
    df['Unit_Price'] = df['Unit_Price'].fillna(0.0)
    df['Cost_Price'] = df['Cost_Price'].fillna(0.0)
    df['Revenue'] = df['Revenue'].fillna(0.0)
    df['Stock'] = df['Stock'].fillna(0)


    # --------------------------------------------------
    # 10. CALCULATE TOTAL COST
    # --------------------------------------------------
    df['Total_Cost'] = (
        df['Quantity'] *
        df['Cost_Price']
    )


    # --------------------------------------------------
    # 11. CALCULATE PROFIT
    # --------------------------------------------------
    df['Profit'] = (
        df['Revenue'] -
        df['Total_Cost']
    )


    # --------------------------------------------------
    # 12. CALCULATE PROFIT MARGIN
    # --------------------------------------------------
    df['Profit_Margin'] = np.where(
        df['Revenue'] > 0,
        (df['Profit'] / df['Revenue']) * 100,
        0.0
    )


    # --------------------------------------------------
    # 13. RESET INDEX
    # --------------------------------------------------
    df.reset_index(
        drop=True,
        inplace=True
    )


    # --------------------------------------------------
    # 14. RETURN PROCESSED DATA
    # --------------------------------------------------
    return df, None