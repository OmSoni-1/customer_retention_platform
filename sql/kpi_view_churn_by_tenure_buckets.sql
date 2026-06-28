CREATE OR ALTER VIEW vw_churn_by_tenure_band_kpi AS

Select TOP 100 tenure_band,
customer_count, 
churned_count,
ROUND((churned_count / customer_count) * 100, 2) churn_rate_percentage

FROM(
Select
    CASE WHEN tenure >= 0 AND tenure <= 12 THEN 'new customers'
        WHEN tenure >= 13 AND tenure <= 24 THEN 'developing customers'
        WHEN tenure >= 25 AND tenure <= 48 THEN 'established customers'
        WHEN tenure >= 49 AND tenure <= 72 THEN 'long-term customers'
    END tenure_band,

    min(tenure) as tenure_sort,

    Cast(count(distinct customer_id) as float) customer_count,
    Cast(SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) as float) churned_count
from customer_churn
GROUP by 
CASE WHEN tenure >= 0 AND tenure <= 12 THEN 'new customers'
        WHEN tenure >= 13 AND tenure <= 24 THEN 'developing customers'
        WHEN tenure >= 25 AND tenure <= 48 THEN 'established customers'
        WHEN tenure >= 49 AND tenure <= 72 THEN 'long-term customers'
    END
) x

order by tenure_sort;