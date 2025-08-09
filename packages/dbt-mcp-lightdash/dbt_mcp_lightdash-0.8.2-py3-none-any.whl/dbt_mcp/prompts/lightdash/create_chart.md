<instructions>
Create a new chart in Lightdash from query results, typically after exploring data with other tools.

This tool is used when you have query results (from lightdash_run_metric_query or manual exploration)
and want to save them as a permanent chart in Lightdash. Charts created through this tool:
- Default to table visualization (users can change visualization type in Lightdash UI)
- Are saved to a specified space for organization
- Include proper field mappings for Lightdash compatibility
- Can be shared with team members through Lightdash

Before using this tool:
1. You should have already queried the data to verify it's what you want
2. Consider if the chart name clearly describes what it shows
3. Think about which space is most appropriate for the chart

Common workflows:
- After exploring data with lightdash_run_metric_query, save interesting findings
- Create charts requested by users for their dashboards
- Build a collection of charts for a specific analysis project

The tool handles:
- Automatic field name mapping (e.g., 'total_revenue' → 'orders_total_revenue')
- Organization context for row-level security
- Proper chart configuration for Lightdash compatibility
</instructions>

<examples>
<example>
Scenario: User has been exploring revenue data and wants to save a specific view
Previous query results: Monthly revenue for last 12 months from orders explore
User says: "This looks good, save it as 'Monthly Revenue Trend'"
    
    Thinking step-by-step:
    - User has already seen and approved the data
    - Need to structure it for chart creation
    - Use descriptive name provided by user
    - Add helpful description for future reference
    
    Parameters:
    name="Monthly Revenue Trend"
    description="Monthly revenue totals for the last 12 months, showing growth trend"
    explore_id="orders"
    metrics=["total_revenue"]
    dimensions=["created_date"]
    group_by=[{"field": "created_date", "grain": "month"}]
    filters=[{"field": "created_date", "operator": "inThePast", "value": 12, "unit": "months"}]
    sort=[{"field": "created_date", "order": "asc"}]
</example>

<example>
Scenario: Creating a chart from existing analysis for executive dashboard
User says: "Create a chart showing our top spending customers this quarter for the exec dashboard"
    
    Thinking step-by-step:
    - This is for executives, so should be clear and focused
    - Need customer names and their spending
    - Filter to current quarter
    - Sort by spending to show top customers
    - Save to appropriate space (exec or leadership)
    
    Parameters:
    name="Top Customers - Current Quarter"
    description="Highest spending customers in the current quarter, for executive review"
    explore_id="customers"
    metrics=["total_spend"]
    dimensions=["customer_name", "customer_segment"]
    group_by=[{"field": "customer_name"}, {"field": "customer_segment"}]
    filters=[{"field": "order_date", "operator": "inCurrentQuarter"}]
    sort=[{"field": "total_spend", "order": "desc"}]
    limit=20
    space_id="exec-dashboard-space-id"
</example>

<example>
Scenario: Saving a complex analysis with multiple metrics
User says: "Save this conversion funnel analysis we just did"
    
    Thinking step-by-step:
    - Conversion funnel implies multiple stage metrics
    - Should preserve the funnel structure in the chart
    - Name should indicate it's a funnel analysis
    
    Parameters:
    name="Conversion Funnel Analysis"
    description="User journey from visit to purchase with conversion rates at each stage"
    explore_id="events"
    metrics=["visits", "signups", "trial_starts", "purchases"]
    dimensions=["week"]
    group_by=[{"field": "week", "grain": "week"}]
    filters=[{"field": "week", "operator": "inThePast", "value": 8, "unit": "weeks"}]
    sort=[{"field": "week", "order": "asc"}]
</example>

<example>
Scenario: User wants to save a chart but hasn't specified details
User says: "Can you save this as a chart?"
    
    Thinking step-by-step:
    - Need to ask for clarification on name and purpose
    - Should understand the business context
    - Guide user to provide meaningful name
    
    Response to user:
    "I'll help you save this as a chart. To make it useful for you and your team, could you tell me:
    1. What should we name this chart? (e.g., 'Weekly Sales Performance')
    2. What's the main insight or purpose? (This will be the description)
    3. Which space should it go in? (or I can use the default Shared space)"
</example>

<example>
Scenario: Creating a chart that will be used in multiple dashboards
User says: "Create a reusable revenue by product category chart"
    
    Thinking step-by-step:
    - "Reusable" suggests it should be general purpose
    - Should not have too restrictive filters
    - Clear naming for easy discovery
    
    Parameters:
    name="Revenue by Product Category"
    description="Product category revenue breakdown - reusable across different dashboards and time periods"
    explore_id="orders"
    metrics=["total_revenue", "order_count"]
    dimensions=["product_category"]
    group_by=[{"field": "product_category"}]
    sort=[{"field": "total_revenue", "order": "desc"}]
    # Note: No time filters so users can apply their own when using the chart
</example>
</examples>

<parameters>
name: Clear, descriptive name for the chart
description: Optional explanation of what the chart shows and why it's useful
explore_id: The explore (dbt model) containing the data
metrics: List of metrics to include (without table prefix)
dimensions: List of dimensions available for grouping
group_by: List of dimensions to group by with optional grain
filters: Optional filter conditions to apply
sort: Optional sorting configuration
limit: Optional result limit
space_id: Space to save the chart in (uses default if not specified)
</parameters>