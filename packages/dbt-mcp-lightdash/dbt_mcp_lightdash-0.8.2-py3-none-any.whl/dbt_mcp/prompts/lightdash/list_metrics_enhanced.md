<instructions>
List all available metrics with enriched metadata from both dbt semantic layer and Lightdash explores.

This tool provides a comprehensive view of metrics available for analysis, showing:
- Which metrics come from dbt semantic layer [SL]
- Which metrics are available in Lightdash explores [LD]
- Which metrics are available in both systems [SL+LD]

The tool groups metrics by their associated explore/model, making it easy to understand
what data can be queried together. Use this tool when:
- Starting a new analysis and need to understand available metrics
- Planning which tool to use (semantic layer vs Lightdash) for queries
- Building charts and need to know metric context

The enriched metadata includes:
- Metric descriptions to understand business meaning
- Data types (number, currency, percentage, etc.)
- Associated dimensions that can be used with each metric
- Labels and tags for categorization

When no metrics match your criteria, the tool will suggest similar metrics
or guide you to explore other data models that might contain what you need.
</instructions>

<examples>
<example>
Question: "What metrics do we have for analyzing customer behavior?"
    Thinking step-by-step:
    - User wants customer-related metrics
    - Should filter or search for customer-related explores
    - Include both SL and LD metrics for comprehensive view
    Parameters:
    explore_filter="customer"
    include_lightdash_only=true
    
    Response interpretation:
    - Found metrics in 'customers' explore
    - Shows customer_lifetime_value [SL+LD], customer_count [LD], retention_rate [SL]
    - Can suggest using these metrics with customer dimensions
</example>

<example>
Question: "List all revenue metrics we track"
    Thinking step-by-step:
    - User wants revenue-related metrics across all explores
    - Should search across all explores, not filter by specific one
    - Look for metrics with 'revenue' in name or description
    Parameters:
    include_lightdash_only=true
    
    Response interpretation:
    - Found total_revenue in 'orders' explore [SL+LD]
    - Found product_revenue in 'products' explore [LD]
    - Found monthly_recurring_revenue in 'subscriptions' explore [SL]
    - User can now choose appropriate explore based on analysis needs
</example>

<example>
Question: "What metrics can I use with the orders data?"
    Thinking step-by-step:
    - User specifically asking about 'orders' explore
    - Should filter to just that explore
    - Show all available metrics regardless of source
    Parameters:
    explore_filter="orders"
    include_lightdash_only=true
    
    Response shows:
    - total_revenue [SL+LD] - Sum of all order amounts
    - order_count [LD] - Number of orders
    - average_order_value [SL+LD] - Revenue divided by order count
    - Shows these can be grouped by: created_date, status, customer_name
</example>

<example>
Question: "I need to build a dashboard about product performance"
    Thinking step-by-step:
    - User planning dashboard, needs comprehensive metric list
    - Should look for product-related explores
    - Include context about how metrics relate
    Parameters:
    explore_filter="product"
    include_lightdash_only=true
    
    Response interpretation:
    - Found 'products' explore with: units_sold, revenue, return_rate
    - Found 'orders' explore with product dimensions and sales metrics
    - Can suggest combining metrics from both explores for complete dashboard
</example>

<example>
Question: "Show me only the metrics that are in both dbt and Lightdash"
    Thinking step-by-step:
    - User wants to see overlap between systems
    - Should exclude Lightdash-only metrics
    - Useful for understanding migration status
    Parameters:
    include_lightdash_only=false
    
    Response shows only [SL+LD] metrics:
    - More reliable for cross-system workflows
    - Can be queried through either tool
</example>
</examples>

<parameters>
explore_filter: Optional filter to show metrics from specific explore/model only
include_lightdash_only: Whether to include metrics that only exist in Lightdash (default: true)
</parameters>