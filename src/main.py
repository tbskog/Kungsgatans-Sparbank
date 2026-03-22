import pandas as pd
from load import load_file
from transform import (standardize_column_names, 
                       validate_data_types,
                       check_nans_transactions_and_merchants,
                       check_and_fill_nans_and_missing_values_currency_rates,
                       cross_check_currencies_between_merchants_and_currency_rates,
                       combine_tables,
                       convert_monetary_values_to_SEK_and_remove_local)
from compute_tasks import (q1_compute_total_turnover_SEK,
                           q2_merchant_count_per_partner_and_rank_by_revenue,
                           q3_service_charge_rate_per_card_type,
                           q4_optimize_for_1M_REV_INCREASE)


def main():
    ###   Load   ###
    df_trans_stat_2024 = load_file('transaction_stats_2024_monthly.zip')
    df_trans_stat_2025 = load_file('transaction_stats_2025_monthly.zip')
    df_merchant_list =   load_file('acquiring_bank_merchants.csv')
    df_currencies =      load_file('FX.xlsx')

    ###   Transform   ###
    df_trans_stat_2025 = standardize_column_names(df_trans_stat_2025)
    df_trans_stat_2025 = validate_data_types(df_trans_stat_2025)
    check_nans_transactions_and_merchants(df_trans_stat_2025)

    df_trans_stat_2024 = standardize_column_names(df_trans_stat_2024)
    df_trans_stat_2024 = validate_data_types(df_trans_stat_2024)
    check_nans_transactions_and_merchants(df_trans_stat_2024)

    df_merchant_list = standardize_column_names(df_merchant_list)
    df_merchant_list = validate_data_types(df_merchant_list)
    check_nans_transactions_and_merchants(df_merchant_list)

    df_currencies = standardize_column_names(df_currencies)
    df_currencies = validate_data_types(df_currencies)
    df_currencies = check_and_fill_nans_and_missing_values_currency_rates(df_currencies)
    df_currencies = cross_check_currencies_between_merchants_and_currency_rates(df_merchant_list, df_currencies)

    lst_of_transaction_dfs = [df_trans_stat_2024, 
                              df_trans_stat_2025]
    
    df_unified = combine_tables(lst_of_transaction_dfs,
                                df_merchant_list,
                                df_currencies)
    
    df_unified_SEK = convert_monetary_values_to_SEK_and_remove_local(df_unified)

    ###   Compute tasks   ###
    df_total_turnover_SEK = q1_compute_total_turnover_SEK(df_unified_SEK)

    (df_ranked_by_turnover, 
     df_top_five_merchant_count_per_partner) = q2_merchant_count_per_partner_and_rank_by_revenue(df_unified_SEK)
    
    (df_card_type_service_charge, 
     df_card_type_correlation_msc_turnover) = q3_service_charge_rate_per_card_type(df_unified_SEK)
    
    (df_card_service_charge_increase_comparison, 
     relative_increase_pct, 
     total_net_rev_change) = q4_optimize_for_1M_REV_INCREASE(df_unified_SEK)

    ###   Answers in Terminal  ###
    print("------------------------------------------------------------------")
    print("\nAnswer to Q1:\n\n", df_total_turnover_SEK, "\n\n")
    print("------------------------------------------------------------------")
    print("\nAnswer to Q2:\n")
    print("Which partner has the most merchants?\n\n", df_top_five_merchant_count_per_partner)
    print("\nWhich partner generates the most revenue? (in SEK) [Expected Table]\n\n", df_ranked_by_turnover)
    print("\n------------------------------------------------------------------")
    print("\nAnswer to Q3:\n\n", df_card_type_service_charge, "\n\n")
    print("Correlation analysis service charge and turnover per card type:\n", df_card_type_correlation_msc_turnover)
    print("\n------------------------------------------------------------------")
    print("\nAnswer to Q4:\n\n", df_card_service_charge_increase_comparison)
    print("\n")
    print(f"Service Charge Increase over all cards [%]: {relative_increase_pct:.6f}%") 
    print(f"Total Net Revenue Change: {total_net_rev_change:,.2f} SEK")

if __name__ == "__main__":
    main()