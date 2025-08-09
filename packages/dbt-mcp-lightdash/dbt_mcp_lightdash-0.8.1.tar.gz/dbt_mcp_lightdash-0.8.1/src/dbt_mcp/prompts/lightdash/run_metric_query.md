<instructions>
Execute queries against Lightdash explores to answer business questions and optionally save results as charts.

This tool queries data through Lightdash's API using explores (dbt models) and their associated fields.
Before using this tool, you should first understand what explores and fields are available by using:
- list_explores to see available data models
- get_explore to see fields within a specific explore
- list_metrics_enhanced to understand available metrics

When constructing queries:
- Use the explore_id (like 'orders', 'customers') to specify the data model
- Metrics and dimensions should use field names without table prefixes
- The tool automatically handles field name mapping between dbt models and Lightdash
- Group by dimensions when you want to break down metrics
- Use filters to narrow results to specific conditions
- Sort results to highlight important patterns

For chart creation:
- Set save_as_chart=true to persist the query as a Lightdash chart
- Provide a descriptive chart_name that explains what the chart shows
- Charts default to table visualization (can be changed in Lightdash UI)
- Choose appropriate space_id or let it use the default space

Best practices:
1. Start with a small limit to verify results before running larger queries
2. When exploring data, first query without saving, then save once you've refined the query
3. Use clear, business-friendly names for saved charts
</instructions>

<examples>
<example>
Question: "Show me total revenue by month for this year"
    Thinking step-by-step:
    - I need the orders explore which contains revenue data
    - I'll use total_revenue metric and group by created_date with MONTH grain
    - I should filter for current year data
    - Order by date to show chronological progression
    Parameters:
    explore_id="orders"
    metrics=["total_revenue"]
    dimensions=["created_date"]
    group_by=[{"field": "created_date", "grain": "month"}]
    filters=[{"field": "created_date", "operator": "inThePast", "value": 1, "unit": "years"}]
    sort=[{"field": "created_date", "order": "asc"}]
    limit=12
</example>

<example>
Question: "What are our top 10 customers by lifetime value? Save this as a chart"
    Thinking step-by-step:
    - First, I'll check what customer metrics are available
    - Using list_metrics_enhanced, I find customer_lifetime_value in the customers explore
    - I need to group by customer_name to see individual customers
    - Sort by lifetime value descending to get top customers
    - Save as a chart since user requested it
    Parameters:
    explore_id="customers"
    metrics=["customer_lifetime_value"]
    dimensions=["customer_name"]
    group_by=[{"field": "customer_name"}]
    sort=[{"field": "customer_lifetime_value", "order": "desc"}]
    limit=10
    save_as_chart=true
    chart_name="Top 10 Customers by Lifetime Value"
    chart_description="Shows our highest value customers based on total lifetime purchases"
</example>

<example>
Question: "Compare sales performance across regions"
    Thinking step-by-step:
    - I need to find sales metrics and region dimension
    - Check explores: orders explore has total_sales and region
    - Group by region to compare performance
    - Also include order_count to show volume
    - Sort by sales to rank regions
    Initial query (verify data):
    explore_id="orders"
    metrics=["total_sales", "order_count"]
    dimensions=["region"]
    group_by=[{"field": "region"}]
    sort=[{"field": "total_sales", "order": "desc"}]
    limit=5
    
    Follow-up (if results look good):
    save_as_chart=true
    chart_name="Sales Performance by Region"
    limit=None
</example>

<example>
Question: "Show me product sales but I'm not sure what fields are available"
    Thinking step-by-step:
    - User is unsure about available data
    - First, I should use list_explores to find product-related explores
    - Then use get_explore to see available fields
    - Guide user on what's possible
    Response to user:
    "Let me check what product data is available for you..."
    [Uses list_explores and finds 'orders' explore with product fields]
    [Uses get_explore('orders') to see product_name, product_category, etc.]
    "I found that in the orders explore, you have access to:
    - Metrics: total_sales, order_count, average_order_value
    - Product dimensions: product_name, product_category, product_brand
    Would you like to see sales broken down by product category or specific products?"
</example>

<example>
Question: "Daily orders trend for the last 30 days, and save it for our morning dashboard"
    Thinking step-by-step:
    - Need orders explore with order_count metric
    - Group by created_date with DAY grain
    - Filter for last 30 days
    - Sort chronologically
    - Save with descriptive name for dashboard use
    Parameters:
    explore_id="orders"
    metrics=["order_count"]
    dimensions=["created_date"]
    group_by=[{"field": "created_date", "grain": "day"}]
    filters=[{"field": "created_date", "operator": "inThePast", "value": 30, "unit": "days"}]
    sort=[{"field": "created_date", "order": "asc"}]
    save_as_chart=true
    chart_name="Daily Orders - Last 30 Days"
    chart_description="Daily order volume trend for morning dashboard review"
</example>
</examples>

<parameters>
explore_id: The explore (dbt model) to query
metrics: List of metric field names to include
dimensions: List of dimension field names available for grouping/filtering
group_by: Optional list of dimensions to group results by, with optional time grain
filters: Optional list of filter conditions
sort: Optional list of fields to sort by
limit: Optional number of results to return
save_as_chart: Whether to save the query results as a Lightdash chart
chart_name: Name for the saved chart (required if save_as_chart=true)
chart_description: Optional description for the saved chart
space_id: Optional space to save the chart in (uses default if not specified)
</parameters>