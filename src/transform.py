import pandas as pd

def standardize_column_names(df) -> pd.DataFrame: 
    """
        This function standardizes the column names of the input dataframe to a consistent format.

        Args:
            df (pd.DataFrame): The input dataframe with original column names.
        Returns:
            pd.DataFrame: A new dataframe with standardized column names.
    """
    rename_map = {
        "Merchant_ID": "merchant_id",
        "Merchant_Name": "merchant_name",
        "Date": "period_date",
        "Card_Type": "card_type",
        "Turnover": "turnover_amount",
        "Service_Charge": "msc_amount",
        "Scheme_Cost": "Scheme_cost",
        "Interchange": "Interchange",
        "Partner": "partner_id",
        "VAT_Number": "VAT Number",
        "Country": "country",
        "Currency": "currency",
        "Product": "product",
        "currency_name": "currency",
        "currency_value": "Rate",
        "Year": "year",
        "month": "month"}

    df = df.rename(columns=rename_map)
    return df

def validate_data_types(df) -> pd.DataFrame:
    """
        This function validates and converts the data types of the columns in the 
        input dataframe according to a predefined mapping.

        Args:
            df (pd.DataFrame): The input dataframe with original data types.
        Returns:
            pd.DataFrame: A new dataframe with standardized data types.
    """
    column_datatype_map = {
        "merchant_id": "str",
        "merchant_name": "str",
        "period_date": "datetime",
        "card_type": "str",
        "turnover_amount": "float64",
        "msc_amount": "float64",
        "Scheme_cost": "float64", #assuming it should be float, rather than int 
        "Interchange": "float64", #same here
        "partner_id": "str",
        "VAT Number": "str",
        "country": "str",
        "currency": "str",
        "product": "str",
        "currency": "str",
        "Rate": "float64",
        "year": "int32", 
        "month": "int32"}
    
    for column, expected_dtype in column_datatype_map.items():
        if column in df.columns:
            actual_dtype = df[column].dtype
            if actual_dtype != expected_dtype:
                try: 
                    if expected_dtype == "datetime":
                        df[column] = pd.to_datetime(df[column])
                        continue
                    df[column] = df[column].astype(expected_dtype)
                except Exception as e:
                    print(f"Could not convert column '{column}' to data type {expected_dtype}: {e}")
                
    return df

def check_nans_transactions_and_merchants(df_transactions_or_merchants):
    """
        This function checks for the presence of NaN values in the transactions or merchants
        dataframes. It prints a message is any NaN values are found, instructing the user to
        investigate the data further.

        Args:
            df_transactions_or_merchants (pd.DataFrame): The input dataframe to check for NaN values.
        Returns: 
            None
    """
    if df_transactions_or_merchants.isna().any().any():
        print("There are NaN values in the transactions data. Consider investigating it.")
    elif df_transactions_or_merchants.isna().any().any():
        print("There are NaN values in the merchant data. Consider investigating it.")
        
def check_and_fill_nans_and_missing_values_currency_rates(df_currency_rates) -> pd.DataFrame:
    """
        This function checks for the presence of NaN values in the currency rates dataframe.
        If NaN values are found, it specifically checks the "Rate" column (currency rate)
        for missing values and applies both forward and backward filling to fill the missing rates.
        The function also ensures that the dataframe has a complete grid of currency, year, and month
        combinations, to avoid missing rows.

        In the case of missing values in other columns, it prints a message, prompting the user
        to investigate the data further.

        Args:
            df_currency_rates (pd.DataFrame): The input dataframe containing currency rates.
        Returns:
            pd.DataFrame: A new dataframe, either having missing rates filled or not, depending
                          on if the original dataframe had missing values or not.
    """
    
    #Define scope of potentially missing rows
    all_currencies = df_currency_rates["currency"].unique()
    all_relevant_years = range(df_currency_rates["year"].min(), df_currency_rates["year"].max() + 1)
    all_months = range(1,13)

    #Make a grid of all possible combinations of currency, year, and month
    #to ensure completeness.
    grid = pd.MultiIndex.from_product(
        [all_currencies, all_relevant_years, all_months],
        names = ["currency", "year", "month"]
    ).to_frame(index=False)

    #Merge the grid with original.
    #This will introduce NaNs for missing rows
    df_rates_complete = pd.merge(grid, df_currency_rates, on=["currency", "year", "month"], how="left")

    df = df_rates_complete

    # Check if any NaNs exist in the whole dataframe
    if df.isna().any().any():
        # Specifically check the Rate column
        if "Rate" in df.columns and df["Rate"].isna().any():
            print("Missing values for 'Rate' found. Sorting and forward filling on 'currency', 'year', and 'month'...")

            if "month" in df:
                if "year" in df:
                    df = df.sort_values(["currency", "year", "month"])
                else:
                    print("No 'year' column. Sorting by currency and month...")
                    df = df.sort_values(["currency", "month"])
            else:
                print("No 'month' column. Sorting by currency only...")
                df = df.sort_values(["currency"])

            # Forward and backward fill missing rates from previous values.
            df["Rate"] = df.groupby("currency")["Rate"].ffill().bfill()
            
        else:
            print("NaNs exist, but not in the 'Rate' column. Investigate other columns!")
            
    return df 

def cross_check_currencies_between_merchants_and_currency_rates(df_merchants: pd.DataFrame, 
                                                                df_currency_rates: pd.DataFrame):
    """
        This function cross checks currencies between the currency rate dataset and the merchant
        dataset. If a currency is missing in the currency dataset, the user will be prompted to
        investigate further. However, if the missing currency is Bulgarian Leva "BGN" then the 
        function will apply the fixed rate 1 EURO = 1.95583 BGN, which has been set since 1999.

        Args:
            df_merchants (pd.DataFrame): The input dataframe of merchants
            df_currency_rates (pd.DataFrame): The input dataframe of currency rates
        Returns:
            If BGN missing: Returns a new DataFrame containing values for BGN
            Otherwise: None
    """
    
    def add_BGN_to_currency_rates(df_currency_rates_with_euro: pd.DataFrame) -> pd.DataFrame:
        """
            Internal function for applying the fixed rate 1 EURO = 1.95583 BGN, in case
            BGN is missing the currency rate dataset. The Function requires the input dataset
            to contain values for EURO.

            Args:
                df_currency_rates_with_euro (pd.DataFrame): Input dataframe of currency rates
                                                            containing at least EURO.
            Returns:
                pd.DataFrame: A new dataframe containing currency BGN
        """

        df = df_currency_rates_with_euro
        #Offical fixed peg of EUR to BGN
        FIXED_RATE_EUR_TO_BGN = 1.95583

        bgn_df = df[df["currency"] == 'EUR'].copy()

        bgn_df["currency"] = "BGN"
        bgn_df["Rate"] = bgn_df["Rate"] * FIXED_RATE_EUR_TO_BGN

        df_with_bgn = pd.concat([df, bgn_df], ignore_index=True).sort_values(["currency", 
                                                                            "year",
                                                                            "month"])

        return df_with_bgn
    

    #Create an unique set of currencies from both dataframes
    currencies_in_merchants_df = set(df_merchants["currency"].unique())
    currencies_in_currency_df = set(df_currency_rates["currency"].unique())

    #Find currencies missing in the currency rates data.
    only_in_merchants = currencies_in_merchants_df - currencies_in_currency_df

    #Message the user about discrepancies
    #If only BGN is missing, fill it using the fixed peg.
    if only_in_merchants:
        if only_in_merchants == {"BGN"}:
            print(f"BGN is missing in the currency rates data. Applying fixed peg to fill the missing values...")
            df_currency_rates = add_BGN_to_currency_rates(df_currency_rates)
            return df_currency_rates

        else:
            print(f"There are currencies missing in the currency rates data: {only_in_merchants}.")
    else:
        print("All currencies checks out.")

def combine_tables(list_of_transaction_dfs: list[pd.DataFrame],
                   df_merchants: pd.DataFrame,
                   df_currency_rates: pd.DataFrame) -> pd.DataFrame:
    """
        Helper function to combine tables. The column "products" is dropped.

        Args:
            list_of_transaction_dfs (list[pd.Dataframes]): A list of transaction dataframes to be combined.
            df_merchants (pd.DataFrame): The input merchants dataframe
            df_currency_rates (pd.DataFrame): The input dataframe containing currency rates. 
        Returns:
            pd.DataFrame: A unified DataFrame
    """
    
    df_transactions_combined = pd.concat(list_of_transaction_dfs, ignore_index=True)

    # Extract year and month from "period_date" and drop it.
    df_transactions_combined["year"] = df_transactions_combined["period_date"].dt.year
    df_transactions_combined["month"] = df_transactions_combined["period_date"].dt.month
    df_transactions_combined.drop(columns=["period_date"], inplace=True)

    # Merge transactions dataset with merchants dataset 
    df_merged_trans_merchant= pd.merge(df_transactions_combined, df_merchants, on="merchant_id", how="left")

    # Merge above dataset with currency rates
    df_unified = pd.merge(df_merged_trans_merchant, df_currency_rates, on=["year", "month", "currency"], how="left")

    #Drop the "products" column, it is not needed. Duplicates form due to merchants having multiple products.
    df_unified = df_unified.drop(columns=["product"])
    df_unified = df_unified.drop_duplicates()

    if df_unified.isna().any().any():
        print("There are NaNs in the unified dataset. Consider investigating it.")
    if df_unified.duplicated().any():
        print("There are duplicates in the dataset. Dropping them...")
        df_unified.drop_duplicates()

    return df_unified

def convert_monetary_values_to_SEK_and_remove_local(df_unified):
    """
        Function to convert local currencies to SEK and 
        then dropping those local monetary columns

        Args:
            df_unified (pd.DataFrame): A unified dataframe of transactions, currencies, and merchants
        Returns:
            pd.DataFrame: The unified dataframe with monetary values in SEK, without local currencies.

    """
    df = df_unified.copy()

    #Convert currencies to SEK
    df["turnover_SEK"] = df["turnover_amount"] * df["Rate"]
    df["msc_amount_SEK"] = df["msc_amount"] * df["Rate"]
    df["Scheme_cost_SEK"] = df["Scheme_cost"] * df["Rate"]
    df["Interchange_SEK"] = df["Interchange"] * df["Rate"]

    #Drop local monetary columns, currenies, and rates since they are not necessary anymore
    df = df.drop(columns={"turnover_amount", 
                          "msc_amount", 
                          "Scheme_cost", 
                          "Interchange",
                          "currency", 
                          "Rate"})

    return df




