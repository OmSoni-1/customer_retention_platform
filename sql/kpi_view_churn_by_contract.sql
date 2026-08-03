CREATE OR REPLACE VIEW vw_churn_by_contract_kpi AS
SELECT
    contract_name,
    customer_count,
    churned_count,
    ROUND((churned_count / customer_count) * 100, 2) AS churn_rate_percentage
FROM (
    SELECT
        contract AS contract_name,
        COUNT(DISTINCT customer_id)::numeric AS customer_count,
        SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END)::numeric AS churned_count
    FROM customer_churn
    GROUP BY contract
) x;