CREATE OR ALTER VIEW vw_overall_churn_kpis AS

Select 
    x.total_customers total_customers ,
    x.churned_customers_count churned_customers,
    x.retained_customers_count retained_customers,
    ROUND((x.churned_customers_count / NULLIF(CAST(x.total_customers AS DECIMAL(10,2)), 0)) * 100, 2) 
    churn_rate_pct,
    ROUND(x.total_revenue_at_risk, 2) total_revenue_at_risk,
    ROUND(x.churned_customers_cltv / NULLIF(x.churned_customers_count, 0), 2) avg_cltv_churned,
    ROUND(x.retained_customers_cltv / NULLIF(x.retained_customers_count, 0), 2) avg_cltv_retained 

FROM

(
    Select 
        count(distinct cc.customer_id) total_customers,
        CAST(SUM(CASE WHEN cc.churn = 'Yes' THEN 1 ELSE 0 END) as decimal(10,2)) churned_customers_count,
        CAST(SUM(CASE WHEN cc.churn = 'Yes' THEN 0 ELSE 1 END) as decimal(10,2)) retained_customers_count,
        SUM(CASE WHEN cc.churn = 'Yes' THEN cc.monthly_charges ELSE 0 END) total_revenue_at_risk,
        SUM(CASE WHEN cs.churn_label = 'Yes' THEN cs.cltv ELSE 0 END) churned_customers_cltv,
        SUM(CASE WHEN cs.churn_label = 'Yes' THEN 0 ELSE cs.cltv END) retained_customers_cltv

    from customer_churn cc
    INNER JOIN customer_status as cs ON cc.customer_id = cs.customer_id

) x;