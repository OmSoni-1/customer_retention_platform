CREATE OR ALTER VIEW vw_churn_by_payment_method_kpi

AS

Select payment_method,
customer_count,
churned_count,
ROUND((churned_count / customer_count) * 100,  2) churn_rate_percentage
from 
(
Select
    payment_method payment_method,
    Cast(count(distinct customer_id) as float) customer_count,
    Cast(SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) as float) churned_count

from customer_churn
GROUP BY payment_method
) x;