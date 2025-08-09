Edit an existing Lightdash chart (metadata only).

Currently only supports updating chart name and description. 
Query modifications (metrics, dimensions, filters, sorts) are not supported by the Lightdash API.

To modify chart queries, create a new chart with the desired configuration.

Examples:
- "Change the chart name to 'Monthly Sales Performance'"
- "Update the chart description to explain the metrics"

NOT supported (requires creating a new chart):
- "Update the revenue chart to show only the last 30 days"
- "Add customer_segment dimension to the existing chart"
- "Change the metrics to include order_count"