SELECT
    s.sale_id,
    s.sale_date,
    s.quantity,
    s.unit_price,
    s.discount_pct,
    s.total_amount,
    s.payment_method,
    s.customer_type,

    p.product_id,
    p.product_name,
    p.category,
    p.sub_category,
    p.brand,
    p.sku,
    p.unit_cost,
    p.margin_pct,

    st.store_id,
    st.store_name,
    st.city,
    st.region,
    st.store_type,
    st.sqft,
    st.opened_date,
    st.manager,

    r.return_id,
    r.return_date,
    r.reason AS return_reason,
    r.refund_amount,
    r.status AS return_status

FROM retail.sales s

JOIN retail.products p
    ON s.product_id = p.product_id

JOIN retail.stores st
    ON s.store_id = st.store_id

LEFT JOIN retail.returns r
    ON s.sale_id = r.sale_id

LIMIT 50;