-- SQLite and BigQuery GoogleSQL. Set the default dataset before running in BigQuery.
-- One input row per unique assigned session, including sessions with no events.
SELECT
    case_id,
    retailer,
    locale,
    day,
    device,
    variant,
    COUNT(*) AS n,
    SUM(engaged) AS engaged,
    SUM(carts) AS carts,
    SUM(purchases) AS purchases
FROM trial_sessions
GROUP BY case_id, retailer, locale, day, device, variant
ORDER BY case_id, day, device, variant;
