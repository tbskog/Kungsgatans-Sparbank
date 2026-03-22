# Transaction analysis case solution

This repo contains my solution to the case "Transaction Analytics & Pricing Simulation" at Kungsgatan Sparbank. The solution can be run end-to-end with a single command after setup.

## Setup

Create and activate a virtual environment:

```bash
conda create -n sparbank-case-oliver-c python=3.11
conda activate sparbank-case-oliver-c
```

Install required dependencies:

```bash
pip install -r requirements.txt
```

---

## Run the Solution

Run the full transaction analysis pipeline. This will execute the full pipeline and print the results for all four questions to the console.

Navigate to the project root and run:
```bash
python src/main.py
```

## Data

The solution expects input data to be located in the root directory provided in the repository.

# Overview
The solution implements an end-to-end pipeline to answer the four questions:

* **Q1:** Total turnover SEK per year
* **Q2:** Partner comparison: merchant count vs revenue
* **Q3:** Service_Charge rate per card type + relationship to turnover
* **Q4:** Pricing simulation / optimization

## General assumptions
* Firstly, it's assumed that the datasets to be ingested always come with the same column names. 
* It's also assumed that the column naming in the main repo are standard for us. Thus, the raw datasets' column names are standardized according to the column naming provided in the main repo.
* I have to assume that the original data is 'correct'. However, an outlier analysis may be beneficial.
* I also assume that the transactional data is correct as is.

## Exploratory analysis
* Do the merchants use multiple currencies?
    * Analysis said no.
* Are all exchange rates in the transaction table present in the currency rate table?
    * No, BGN is not present in the currency rate table.
        * BGN is pegged to Euro since 1999, 1 EUR = 1.95583 BGN

# Q1: Total turnover SEK per year

## Assumptions
* Total turnover is defined as the total transactional value as provided by sum of "turnover_amount" in the transaction         statistics table, after converting each local currency to SEK.
* Currency rates from local currency to SEK are provided in the currency table. It is assumed that the present rates and dates (months) in the table are correct. 
    * The rates are provided per month, thus there is a 'forced' assumption that the rate of the 1st day of the month applies to the whole month, since each transaction is per month as well.
* It is assumed that missing currency rates can be exchanged by the latest available currency rate. However, an API or other method for extracting 'true' rates would be better.

## Results
* The total turnover in SEK, per year is provided in a dataframe.

# Q2: Partner comparison: merchant count vs revenue

## Assumptions
* It's assumed that the question refers to the revenue generated over the time period
    that is provided by the transactional data. In other words, which partner has generated the most revenue over the period 2024-2025.
* The same applies to the number of merchants each partner is connected to.
    * Assumption may skew the result if some partners have lost their merchants from 2024-2025

## Results
* The top five partners with the most merchants are provided in a dataframe.
    * Top 1 is "Partner003", during 2024-2025
* The partners that generates the most revenue (2024-2025) is also provided in a dataframe.

# Q3: Service_Charge rate per card type + relationship to turnover

## Assumptions
* It's assumed that the question refers to the time period given by the provided transactional data. In other words, compute the service charge rate per card type between 2024-2025.
    * In case there was a service charge shift between 2024 & 2025, the result will be the average service charge rate for the given period.

## Result
* Service charges per card type are provided in a dataframe.
* Correlation analysis concludes that there is a linear relationship between turnover and service charge per card type.
    * I.e. there is (and was during 2024-2025) a fixed rate for each card type.

# Q4: Pricing simulation / optimization

## Assumptions
* Firstly, it's assumed that "1,000,000 mSEK" is a typo for "1 MSEK".
* It's assumed that it's most reliable to use only the latest year's transactions and net revenues.
    * and not average, for example.
* It's assumed that the card scheme cost and interchange cost are fixed, and won't change upcoming year.
* It's assumed to be best to distribute the percentage increase in service charge rate across all cards, equally.
    * With respect to customer churn, having a fixed bps (or %) increase negatively impacts cheaper card types (gets a higher % increase than expensive ones) and having a relative bps increase negatively impacts more expensive cards.
        * However, the relative bps increase seems most fair. A customer churn analysis (e.g. A/B groups) would be beneficial.

## Optimization method description
The proposed method utilizes the bisection method (or binary search) to find the optimal increase in service charge rate (SCR). As stated under 'assumptions', the increased SCR is applied equally across all card types and the optimization method is constrained to not apply an increase in SCR over 5%. The bisection method, and this optimization method, continously divides the constrained parameter space (['low', 'high'] = [0%, 5%]) and checks if the midpoint satisfies the objective (Net revenue increase = 1 MSEK ± 0.01 SEK). If not, the midpoint becomes the new 'low' or 'high' in the parameter space, ultimately narrowing the search until convergence.

## Result
The optimization method successfully found a Service Charge Rate Increase across all cards. Results are presented below:

    - Service Charge Rate Increase over all cards: 
        - 0.001967%

    - bps change per card (rounded) | Net Revenue Impact:
        - Amex:          0.0043 bps | 275,174.64 SEK
        - MC_CREDIT:     0.0030 bps | 185,549.44 SEK
        - MC_DEBIT:      0.0017 bps | 106,735.67 SEK
        - OTHER:         0.0024 bps | 150,570.33 SEK
        - VISA_CREDIT:   0.0028 bps | 177,980.69 SEK
        - VISA_DEBIT:    0.0016 bps | 103,989.24 SEK

# Possible improvements
* The solution runs end-to-end for the specific files provided. An improvement would be to implement an automated pipeline that ingests all raw files in a directory.
* The result should probably be loaded as a .csv (or other format) into a specific folder. Due to this uncertainty, all results are printed in the terminal at the moment. 