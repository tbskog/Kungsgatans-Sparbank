# Kungsgatans-Sparbank
# Case: Transaction Analytics & Pricing Simulation
## Context
You have in the Repo four data files representing a simplified payments/acquiring dataset:

### Transaction statistics (2024,2025) (e.g., turnover, fees/revenue, dates, card types, merchant IDs)
| Column name            | Type   | Description |
|------------------------|--------|-------------|
| period_date            | date   | Date representing the transaction period ( month start). |
| merchant_id            | string | Unique identifier for the merchant. |
| card_type              | string | Card category (e.g. Debit, Credit, Domestic, International). |
| turnover_amount        | float  | Total transaction value for the period, in original currency. |
| msc_amount             | float  | Merchant Service Charge charged on the transactions, in original currency. |
| Scheme_cost      | int    | Cost for the transaction |
| Interchange      | int    | Cost for the transaction |


### Merchant list (merchant metadata, including partner attachment)

| Column name        | Type   | Description |
|--------------------|--------|-------------|
| merchant_id        | string | Unique identifier for the merchant. |
| merchant_name      | string | Display name of the merchant. |
| VAT Number           | string | Legal entity |
| partner_id         | string | Identifier of the partner the merchant is attached to. |
| country            | string | Country where the merchant is registered or operates. |
| currency           | string | ISO currency code (e.g. SEK, EUR, NOK). |

### Currency table (FX rates needed to convert amounts to SEK)
| Column name        | Type   | Description |
|--------------------|--------|-------------|
| currency        | string |ISO currency code|
| Rate        | Decimal |  |
| year        | INT |  |
| month        | INT |  |



Goal: Produce clear, reproducible answers (supported by code) to the questions below.


### Requirements


In a coding language of your choice.
Your solution should be replicable, well‑structured, and easy to review.

Deliverables
Provide the following:

Do a pull request on the given repo containing:

README.md with instructions to run the solution
Source code (scripts/modules)


### Expectation

The solution runs end‑to‑end from raw input files to final outputs.
Assumptions are documented (especially around “revenue”, currency conversion rules, and missing values).

Evaluation Criteria
We will assess:

Correctness of results and reasoning
Code quality (structure, naming, modularity, readability)
Reproducibility (clear run instructions, deterministic outputs)
Data handling (joins, edge cases, currency conversion, validation)
Clarity of communication (how well you present findings)

---------------------------------------------------------------------------------------------------------------
## Tasks / Questions
### 1) Total Turnover per year in SEK
Compute total Turnover per year, converted into SEK using the provided currency table.
Expected output

A table like: year | Turnover_sek  
Document assumptions (e.g., what constitutes “Turnover”, which FX rate to apply, how dates are interpreted)


### 2) Partner comparison: merchant count vs revenue
Merchants are attached to partners.  

Which partner has the most merchants?  
Which partner generates the most revenue? (in SEK)  

Expected output  

A table of partners ranked by:

merchant count
revenue (SEK)


### 3) Service_Charge rate per card type + relationship to turnover
Compute the Service_Charge rate per card type, then analyze the relationship between turnover and Service_Charge.
Expected output

Table: card_type | Service_Charge_rate     
Analysis of relationship between turnover and Service_Charge:  
Note: The dataset provides Service_Charge amount and turnover, Service_Charge rate can be derived as Service_Charge / turnover. 

### 4) Pricing simulation / optimization
Simulate changes in pricing(Service_Charge rate). Based on the rate per card type, propose adjustments that:  

Increase net revenue by 1,000,000 mSEK per year, while  
Minimizing the percentage increase in Service_Charge rate  

Note: Net Revenue is given by Service_charge-Schemecost-Interchange  

#### Expected output

A clearly described method (i.e. optimization approach)
Proposed new rates per card type
Before/after comparison showing:

total net revenue change
overall Service_Charge rate impact (and how you define “overall”)
per-card-type impacts

#### Notes & guidance

You may choose reasonable constraints, such as:

max change per card type (e.g., ±X bps)
keeping some card types unchanged
avoiding extreme changes that would be unrealistic

We keep it simple, an explainable approach is better :) 





