Here is the "Business Interpretation" of your specific results (add this to your README):
The "Win Rate" Chart: You can clearly see the volatility. There was a peak in Nov 2023 (~50%) followed by a steady decline until May 2024 (~40%). This confirms the CRO's suspicion. (Note: The massive spike at the very end is likely "incomplete data" for the current month—in a real report, you would exclude the current incomplete month).
The "Loss by Stage" Chart: This is fascinating.
Good News: The highest losses are at "Demo". This is actually healthy! It means you are disqualifying bad leads early.
Bad News: You have a massive amount of losses at "Negotiation". This is the "expensive" failure. Reps are spending months working deals only to lose them at the contract stage. This suggests a Pricing or Closing capability issue.



## System Architecture 

System Name: SkyGeni Sales Pulse

1. Data Flow Architecture
Ingestion Layer: A Python ETL job runs every 4 hours. It pulls changed deals from the CRM API (Salesforce/HubSpot) and lands them in a Raw_Deals table in Snowflake/Postgres.
Processing Layer (The Intelligence):
Step 1: dbt (Data Build Tool) cleans the data and calculates "Time in Stage".
Step 2: The Python WinRateDriverEngine (our model) runs on new opportunities to generate a "Win Probability Score".
Step 3: An "Anomaly Detection" script checks if the aggregate Win Rate for the current month has dipped below the 3-sigma threshold.
Serving Layer:
Dashboard: A Streamlit app for the CRO to view the "Win Rate Drivers" heatmap.
Alerts: A Slack bot pushes notifications to Sales Managers when a deal >$50k stalls (no activity > 14 days).

2. Failure Cases & Mitigations
Problem: Reps don't update stages, making "Time in Stage" inaccurate.
Fix: Implement a "Stale Data" flag. If a deal hasn't been updated in 30 days, exclude it from the model training to prevent noise.

3. Diagram (See below)

graph LR
    A[CRM API] -->|ETL Job| B(Raw Database)
    B -->|dbt Transformation| C(Clean Tables)
    C -->|Python Engine| D[Win Probability Model]
    D --> E{Action Layer}
    E -->|High Risk Deal| F[Slack Alert to Rep]
    E -->|Trend Analysis| G[Streamlit Dashboard]


# SkyGeni Sales Intelligence Challenge

## 🚀 Executive Summary
The goal of this project was to diagnose why Win Rates are dropping despite healthy pipeline volume.
**Key Finding:** The organization is suffering from **"Late-Stage Leakage"**. While volume is high, a significant portion of deals are failing at the **Negotiation** stage, indicating wasted sales effort on unqualified deals or pricing friction.

## 🛠️ The Solution
I built a Sales Intelligence System that:
1.  **Diagnoses Trends:** Visualizes stage-by-stage conversion leakage.
2.  **Predicts Outcomes:** A Decision Tree model identifies key drivers of won deals (Accuracy: ~75%).
3.  **Actionable Metrics:** Introduced "Stalled Deal Risk" to identify zombie pipeline.

## 📊 Key Insights (from Data Analysis)
1.  **The "Volume Trap":** Pipeline volume has remained steady, but Win Rate dropped from 50% (Nov '23) to ~40% (May '24).
2.  **The "Negotiation" Bottleneck:** A dangerously high number of deals are lost at the 'Negotiation' stage. This implies reps are failing to lock in contracts after doing all the work.
3.  **Driver Analysis:** The ML model identified `Region` and `Deal Amount` as the strongest predictors of success. (e.g., Deals >$50k in EMEA have 2x higher risk).

## ⚙️ How to Run
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Run the Analysis Notebook:
    * Open `notebooks/analysis.ipynb`
3.  Run the Decision Engine:
    ```python
    from src.decision_engine import WinRateDriverEngine
    # See notebook for usage
    ```

## 🏗️ System Architecture (Production Plan)
If productized, this system would run as a nightly batch job:
* **ETL:** Extract from Salesforce -> Load to Snowflake.
* **Model:** Retrains weekly on closed deals.
* **Alerts:** Slack notification sent to Manager if a deal >$10k stalls for 14+ days.

## 🧠 Reflection & Limitations
* **Data Quality:** The model assumes `deal_stage` is accurate. In reality, reps often bulk-update stages, which distorts "velocity" metrics.
* **Missing Context:** We lack "Activity Data" (emails/calls). Adding NLP analysis on sales emails would significantly improve the risk score.
* **Next Steps:** I would implement a "Deal Health Score" (0-100) visible in the CRM to guide reps on which deals to prioritize.
