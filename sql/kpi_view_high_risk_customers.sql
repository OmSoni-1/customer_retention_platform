CREATE OR REPLACE VIEW vw_high_risk_customers AS
SELECT
    cc.customer_id,
    cc.tenure,
    cc.contract,
    cc.monthly_charges,
    cst.churn_score,
    cst.churn_category,
    RANK() OVER (
        PARTITION BY cc.churn
        ORDER BY cc.monthly_charges DESC
    ) AS revenue_rank
FROM customer_churn cc
INNER JOIN services cs ON cs.customer_id = cc.customer_id
INNER JOIN status cst ON cst.customer_id = cc.customer_id
WHERE cc.churn = 'Yes'
ORDER BY cst.churn_score DESC;