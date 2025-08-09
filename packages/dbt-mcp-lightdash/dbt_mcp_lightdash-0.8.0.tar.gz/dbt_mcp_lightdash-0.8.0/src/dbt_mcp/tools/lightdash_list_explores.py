"""Tool for listing Lightdash explores"""

import logging
from typing import Dict, Any, List

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.tools.tool_names import ToolName
from dbt_mcp.prompts.prompts import get_prompt

logger = logging.getLogger(__name__)


def get_lightdash_list_explores_tool() -> Tool:
    """Get the Lightdash list explores tool definition"""
    return Tool(
        name=ToolName.LIGHTDASH_LIST_EXPLORES.value,
        description=get_prompt("lightdash/list_explores"),
        inputSchema={
            "type": "object",
            "properties": {},
            "required": [],
        },
    )


async def handle_lightdash_list_explores(
    arguments: Dict[str, Any], config: Config
) -> List[TextContent]:
    """Handle the Lightdash list explores request"""
    
    if not config.lightdash_config:
        return [
            TextContent(
                type="text",
                text="Error: Lightdash configuration is not available"
            )
        ]
    
    try:
        client = LightdashAPIClient(config.lightdash_config)
        explores = await client.list_explores()
        
        if not explores:
            return [
                TextContent(
                    type="text",
                    text="No explores found in the Lightdash project"
                )
            ]
        
        # Format explores for display
        result = f"Found {len(explores)} explore(s) in Lightdash:\n\n"
        
        for explore in explores:
            result += f"• {explore.get('name', 'Unnamed')}"
            
            # Add label if different from name
            label = explore.get('label')
            if label and label != explore.get('name'):
                result += f" ({label})"
            result += "\n"
            
            # Add tags if available
            tags = explore.get('tags', [])
            if tags:
                result += f"  Tags: {', '.join(tags)}\n"
            
            # Add base table
            base_table = explore.get('baseTable')
            if base_table:
                result += f"  Base Table: {base_table}\n"
            
            # Add joined tables if any
            joined_tables = explore.get('joinedTables', [])
            if joined_tables:
                result += f"  Joined Tables: {', '.join(joined_tables)}\n"
            
            # Count fields
            fields = explore.get('fields', {})
            if fields:
                dimension_count = sum(1 for f in fields.values() if f.get('fieldType') == 'dimension')
                metric_count = sum(1 for f in fields.values() if f.get('fieldType') == 'metric')
                result += f"  Fields: {dimension_count} dimensions, {metric_count} metrics\n"
            
            result += "\n"
        
        return [TextContent(type="text", text=result.strip())]
        
    except Exception as e:
        logger.error(f"Error listing Lightdash explores: {str(e)}", exc_info=True)
        return [
            TextContent(
                type="text",
                text=f"Error listing Lightdash explores: {str(e)}"
            )
        ]