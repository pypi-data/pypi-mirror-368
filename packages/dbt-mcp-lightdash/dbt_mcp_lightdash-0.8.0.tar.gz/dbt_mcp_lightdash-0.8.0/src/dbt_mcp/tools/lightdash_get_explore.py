"""Tool for getting Lightdash explore details"""

import logging
from typing import Dict, Any, List
import json

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.tools.tool_names import ToolName
from dbt_mcp.prompts.prompts import get_prompt

logger = logging.getLogger(__name__)


def get_lightdash_get_explore_tool() -> Tool:
    """Get the Lightdash get explore tool definition"""
    return Tool(
        name=ToolName.LIGHTDASH_GET_EXPLORE.value,
        description=get_prompt("lightdash/get_explore"),
        inputSchema={
            "type": "object",
            "properties": {
                "explore_id": {
                    "type": "string",
                    "description": "The name/ID of the explore to retrieve"
                }
            },
            "required": ["explore_id"],
        },
    )


async def handle_lightdash_get_explore(
    arguments: Dict[str, Any], config: Config
) -> List[TextContent]:
    """Handle the Lightdash get explore request"""
    
    if not config.lightdash_config:
        return [
            TextContent(
                type="text",
                text="Error: Lightdash configuration is not available"
            )
        ]
    
    explore_id = arguments.get("explore_id")
    if not explore_id:
        return [
            TextContent(
                type="text",
                text="Error: explore_id is required"
            )
        ]
    
    try:
        client = LightdashAPIClient(config.lightdash_config)
        explore = await client.get_explore(explore_id)
        
        # Debug: log the raw response
        logger.info(f"Raw explore response: {json.dumps(explore, indent=2) if explore else 'None'}")
        
        if not explore:
            return [
                TextContent(
                    type="text",
                    text=f"Explore '{explore_id}' not found"
                )
            ]
        
        # Format explore details for display
        result = f"Explore Details: {explore.get('name', 'Unnamed')}\n"
        result += f"{'=' * 50}\n\n"
        
        # Basic information
        result += f"Name: {explore.get('name', 'N/A')}\n"
        label = explore.get('label')
        if label:
            result += f"Label: {label}\n"
        
        # Tags
        tags = explore.get('tags', [])
        if tags:
            result += f"Tags: {', '.join(tags)}\n"
        
        # Tables
        result += f"Base Table: {explore.get('baseTable', 'N/A')}\n"
        joined_tables = explore.get('joinedTables', [])
        if joined_tables:
            result += f"Joined Tables: {', '.join(joined_tables)}\n"
        
        # Get fields from tables structure
        tables = explore.get('tables', {})
        if tables:
            # Separate dimensions and metrics from all tables
            dimensions = []
            metrics = []
            
            # Iterate through each table
            for table_name, table_data in tables.items():
                # Get dimensions from this table
                table_dimensions = table_data.get('dimensions', {})
                for dim_name, dim_data in table_dimensions.items():
                    dim_info = {
                        'name': dim_name,
                        'table': table_name,
                        'label': dim_data.get('label', dim_name),
                        'type': dim_data.get('type', 'unknown'),
                        'description': dim_data.get('description'),
                        'hidden': dim_data.get('hidden', False)
                    }
                    dimensions.append(dim_info)
                
                # Get metrics from this table
                table_metrics = table_data.get('metrics', {})
                for metric_name, metric_data in table_metrics.items():
                    metric_info = {
                        'name': metric_name,
                        'table': table_name,
                        'label': metric_data.get('label', metric_name),
                        'type': metric_data.get('type', 'unknown'),
                        'description': metric_data.get('description'),
                        'hidden': metric_data.get('hidden', False),
                        'sql': metric_data.get('sql')
                    }
                    metrics.append(metric_info)
            
            result += f"\nTotal Fields: {len(dimensions) + len(metrics)}\n"
            
            # Display dimensions
            if dimensions:
                result += f"\nDimensions ({len(dimensions)}):\n"
                for dim in sorted(dimensions, key=lambda x: (x['table'], x['name'])):
                    if not dim['hidden']:
                        result += f"  • {dim['table']}.{dim['name']}"
                        if dim['label'] != dim['name']:
                            result += f" ({dim['label']})"
                        result += f" - {dim['type']}"
                        if dim['description']:
                            result += f"\n    {dim['description']}"
                        result += "\n"
            
            # Display metrics
            if metrics:
                result += f"\nMetrics ({len(metrics)}):\n"
                for metric in sorted(metrics, key=lambda x: (x['table'], x['name'])):
                    if not metric['hidden']:
                        result += f"  • {metric['table']}.{metric['name']}"
                        if metric['label'] != metric['name']:
                            result += f" ({metric['label']})"
                        result += f" - {metric['type']}"
                        if metric['description']:
                            result += f"\n    {metric['description']}"
                        if metric.get('sql'):
                            result += f"\n    SQL: {metric['sql']}"
                        result += "\n"
        
        return [TextContent(type="text", text=result.strip())]
        
    except Exception as e:
        logger.error(f"Error getting Lightdash explore details: {str(e)}", exc_info=True)
        return [
            TextContent(
                type="text",
                text=f"Error getting explore details: {str(e)}"
            )
        ]