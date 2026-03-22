import pandas as pd

#Formatting floats to comma separated thousands with two decimals.
pd.options.display.float_format = '{:,.2f}'.format

def q1_compute_total_turnover_SEK(df_unified_SEK: pd.DataFrame) -> pd.DataFrame:
    """
        Function that returns the answer to Q1.

        Args:
            df_unified_SEK (pd.DataFrame): The unified dataframe in SEK
        Returns:
            pd.DataFrame: The expected table: year | Turnover_sek
            pd.DataFrame: df_unified with an additional column converting turnover to SEK ("turnover_SEK)
    """
    df = df_unified_SEK.copy()

    #Sum total turnover in SEK and refactor dataframe to answer
    df_yearly_turnover = df.groupby("year")["turnover_SEK"].sum().reset_index()
    df_yearly_turnover.columns = ["year", "total_turnover_SEK"]

    return df_yearly_turnover

def q2_merchant_count_per_partner_and_rank_by_revenue(df_unified_SEK: pd.DataFrame) -> pd.DataFrame:
    """
        Function that returns the answer to Q2.

        Args:
            df_unified_SEK (pd.DataFrame): df_unified_SEK (pd.DataFrame): The unified dataframe in SEK
        Returns:
            pd.DataFrame: The expected table, a partner-ranked table by total revenue (Partner_ID  | Merchant count | Total Revenue (SEK)).
            pd.DataFrame: Top 5 partners, ranked by merchant count.
    """
    df = df_unified_SEK.copy()

    df_subset = df[["partner_id", "merchant_id", "turnover_SEK"]]

    df_grouped_by_partner = df_subset.groupby("partner_id").agg({
        "merchant_id": "nunique",
        "turnover_SEK": "sum"
    })

    df_ranked_by_turnover = df_grouped_by_partner.sort_values(by="turnover_SEK", ascending=False).reset_index()

    df_top_five_merchant_count_per_partner = df_grouped_by_partner.sort_values(by="merchant_id", ascending=False).reset_index().head()


    df_ranked_by_turnover.columns = df_top_five_merchant_count_per_partner.columns \
                                  = ["Partner_ID", "Merchant count", "Total Revenue (SEK)"]

    df_ranked_by_turnover.index = range(1, len(df_ranked_by_turnover) + 1)
    df_ranked_by_turnover.index.name = "Rank"
    pd.options.display.float_format = '{:,.2f}'.format

    return df_ranked_by_turnover, df_top_five_merchant_count_per_partner

def q3_service_charge_rate_per_card_type(df_unified_SEK: pd.DataFrame) -> pd.DataFrame:
    """
        Function that returns the answer to Q3.

        Args:
            df_unified_SEK (pd.DataFrame): The unified dataframe in SEK
        Returns:
            pd.DataFrame: The expected table: card_type | Service_Charge_rate
            pd.DataFrame: Table of Pearson's correlation coefficient between 
                          turnover and service charge per card type (card_type | correlation_coeff_msc_turnover)
    """
    
    df = df_unified_SEK.copy()

    df_subset = df[["card_type", "msc_amount_SEK", "turnover_SEK"]]

    df_grouped_card_type = df_subset.groupby("card_type").agg({
        "msc_amount_SEK": "sum",
        "turnover_SEK": "sum"
    })

    df_grouped_card_type["service_charge_rate [%]"] = (
        df_grouped_card_type["msc_amount_SEK"] / df_grouped_card_type["turnover_SEK"] * 100)

    df_grouped_card_type = df_grouped_card_type.sort_values("service_charge_rate [%]", ascending=False).reset_index()

    df_card_service_charge = df_grouped_card_type[["card_type", "service_charge_rate [%]"]]

    correlations = df_subset.groupby("card_type").apply(
        lambda x: x["turnover_SEK"].corr(x["msc_amount_SEK"])
    )

    df_card_type_correlation_msc_turnover = correlations.reset_index()
    df_card_type_correlation_msc_turnover.columns = ["card_type", "correlation_coeff_msc_turnover"]
    df_card_type_correlation_msc_turnover = df_card_type_correlation_msc_turnover.sort_values("correlation_coeff_msc_turnover", ascending=False)
    
    return df_card_service_charge, df_card_type_correlation_msc_turnover

def q4_optimize_for_1M_REV_INCREASE(df_unified_SEK: pd.DataFrame) -> pd.DataFrame:
    """
        Function that returns the answer to Q4.
        The optimization method utilizes the bisection method (or binary search) to find the optimal service charge rate to
        increase the net revenue by 1 MSEK. Foundationally, it uses the same percentage increase
        over all cards and finds the minimal percentage increase to fulfill the objective (reaching +1 MSEK net revenue.)

        Args:
            df_unified_SEK (pd.DataFrame): The unified dataframe in SEK
        Returns:
            pd.DataFrame: A resulting table showing the effect on each card when increasing service charge rate
                          by the optimized value. 
            float: The increase in service charge over all cards in unit parts per million [ppm].
            float: The total net revenue change, due to the increase in service charge.

    """

    def simulate_revenue(multiplier, df):
        """
            Helper function to simulate revenue based on a multiplier on service charge ("msc_amount_SEK").

            Args:
                multiplier (float): Representing the multiplyer for the service charge (service charge rate increase)
                df (pd.DataFrame): A dataset of monetary values per card type.

            Returns:
                float: The simulated net revenue
        """
        temp_df = df.copy()
        
        #Apply the percentage increase to the service charge
        temp_df["new_msc"] = temp_df["msc_amount_SEK"] * multiplier
        
        #Recalculate Net Revenue with the same fixed costs
        temp_df["new_net_rev"] = (
            temp_df["new_msc"] - 
            temp_df["Scheme_cost_SEK"] - 
            temp_df["Interchange_SEK"]
        )
        
        return temp_df["new_net_rev"].sum()
    
    df = df_unified_SEK.copy()
    
    #Group by card and sum all monetary values
    baseline = df.groupby("card_type").agg({
        "turnover_SEK": "sum",
        "msc_amount_SEK": "sum",
        "Scheme_cost_SEK": "sum",
        "Interchange_SEK": "sum"
    }).reset_index()

    # Calculate the net revenue for each card
    baseline["net_revenue_SEK"] = (
        baseline["msc_amount_SEK"] - 
        baseline["Scheme_cost_SEK"] - 
        baseline["Interchange_SEK"]
    )

    CURRENT_TOTAL_NET_REV = baseline["net_revenue_SEK"].sum() #The current 'true' net revenue
    TARGET_NET_REV = CURRENT_TOTAL_NET_REV + 1_000_000 #The target net revenue (+1 MSEK)

    #Bisection method / binary search 
    low = 1.0        #0% increase (lower bound)
    high = 1.05       #5% increase (upper bound)
    tolerance = 0.01 #We want to be within 0.01 SEK of the 1M goal

    for i in range(50):  #Assuming 50 iterations will be enough
        
        mid = (low + high) / 2
        simulated_rev = simulate_revenue(mid, baseline)
        
        if abs(simulated_rev - TARGET_NET_REV) < tolerance:
            break
        
        if simulated_rev < TARGET_NET_REV:
            low = mid
        else:
            high = mid

   
    relative_increase_pct = (mid - 1) * 100 # The relative increase across all cards
    total_net_rev_change = simulated_rev - CURRENT_TOTAL_NET_REV

    #Create the final comparison table
    baseline["Proposed_MSC_Rate [%]"] = (baseline["msc_amount_SEK"] * mid)  / baseline["turnover_SEK"] * 100
    baseline["Current_MSC_Rate [%]"] = baseline["msc_amount_SEK"]  / baseline["turnover_SEK"] * 100
    baseline["Net change [bps]"] = (baseline["Proposed_MSC_Rate [%]"] - baseline["Current_MSC_Rate [%]"]) * 100
    baseline["Net_Revenue_Impact"] = (baseline["msc_amount_SEK"] * mid) - baseline["msc_amount_SEK"] 

    #Subset for presenting
    df_card_service_charge_increase_comparison = baseline[["card_type", 
                                                           "Current_MSC_Rate [%]", 
                                                           "Proposed_MSC_Rate [%]", 
                                                           "Net change [bps]", 
                                                           "Net_Revenue_Impact"]]
    
    return df_card_service_charge_increase_comparison, relative_increase_pct, total_net_rev_change

