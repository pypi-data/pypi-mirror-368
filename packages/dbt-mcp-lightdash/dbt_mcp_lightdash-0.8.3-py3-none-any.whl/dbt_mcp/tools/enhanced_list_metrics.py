"""Enhanced tool for listing metrics with Lightdash metadata"""

import logging
from typing import Dict, Any, List

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.lightdash.mapping import get_model_explore_mapper
from dbt_mcp.tools.tool_names import ToolName
from dbt_mcp.prompts.prompts import get_prompt

logger = logging.getLogger(__name__)


def get_enhanced_list_metrics_tool() -> Tool:
    """Get the enhanced list metrics tool definition"""
    return Tool(
        name="list_metrics_enhanced",
        description=get_prompt("lightdash/list_metrics_enhanced"),
        inputSchema={
            "type": "object",
            "properties": {
                "explore_filter": {
                    "type": "string",
                    "description": "Optional: Filter metrics by explore/model name"
                },
                "include_lightdash_only": {
                    "type": "boolean",
                    "description": "Include metrics that only exist in Lightdash (not in semantic layer)"
                }
            },
            "required": [],
        },
    )


async def handle_enhanced_list_metrics(
    arguments: Dict[str, Any], config: Config
) -> List[TextContent]:
    """Handle the enhanced list metrics request"""
    
    explore_filter = arguments.get("explore_filter")
    include_lightdash_only = arguments.get("include_lightdash_only", False)
    
    # Collect metrics from both sources
    semantic_metrics = {}
    lightdash_metrics = {}
    
    # Get semantic layer metrics if available
    if config.semantic_layer_config:
        try:
            from dbt_mcp.semantic_layer.sl_service import SLService
            from dbt_mcp.semantic_layer.client import SemanticLayerFetcher
            sl_service = SLService(config.semantic_layer_config)
            sl_client = sl_service.get_sl_client()
            fetcher = SemanticLayerFetcher(sl_client, config.semantic_layer_config)
            
            sl_metrics = fetcher.list_metrics()
            for metric in sl_metrics:
                semantic_metrics[metric.name] = {
                    "name": metric.name,
                    "type": str(metric.type),
                    "label": metric.label,
                    "description": metric.description,
                    "source": "semantic_layer"
                }
        except Exception as e:
            logger.warning(f"Could not fetch semantic layer metrics: {e}")
    
    # Get Lightdash metrics if available
    if config.lightdash_config:
        try:
            client = LightdashAPIClient(config.lightdash_config)
            mapper = await get_model_explore_mapper(config.lightdash_config)
            
            explores = await client.list_explores()
            
            for explore in explores:
                explore_name = explore.get('name', '')
                
                # Apply explore filter if specified
                if explore_filter and explore_filter.lower() not in explore_name.lower():
                    continue
                
                fields = explore.get('fields', {})
                
                for field_name, field_data in fields.items():
                    if field_data.get('fieldType') == 'metric':
                        # Build metric info
                        metric_info = {
                            "name": field_name,
                            "type": field_data.get('type', 'unknown'),
                            "label": field_data.get('label', field_name),
                            "description": field_data.get('description'),
                            "explore": explore_name,
                            "table": explore.get('baseTable'),
                            "hidden": field_data.get('hidden', False),
                            "source": "lightdash"
                        }
                        
                        lightdash_metrics[field_name] = metric_info
        except Exception as e:
            logger.warning(f"Could not fetch Lightdash metrics: {e}")
    
    # Merge metrics from both sources
    all_metrics = {}
    
    # Start with semantic layer metrics
    all_metrics.update(semantic_metrics)
    
    # Enhance with Lightdash metadata
    for metric_name, ld_info in lightdash_metrics.items():
        if metric_name in all_metrics:
            # Enhance existing metric
            all_metrics[metric_name]["explore"] = ld_info.get("explore")
            all_metrics[metric_name]["table"] = ld_info.get("table")
            all_metrics[metric_name]["hidden"] = ld_info.get("hidden")
            all_metrics[metric_name]["source"] = "both"
            # Use Lightdash description if semantic layer doesn't have one
            if not all_metrics[metric_name].get("description") and ld_info.get("description"):
                all_metrics[metric_name]["description"] = ld_info["description"]
        elif include_lightdash_only:
            # Add Lightdash-only metric
            all_metrics[metric_name] = ld_info
    
    # Group metrics by explore
    metrics_by_explore = {}
    ungrouped_metrics = []
    
    for metric_name, metric_info in all_metrics.items():
        if metric_info.get("hidden"):
            continue  # Skip hidden metrics
            
        explore = metric_info.get("explore")
        if explore:
            if explore not in metrics_by_explore:
                metrics_by_explore[explore] = []
            metrics_by_explore[explore].append(metric_info)
        else:
            ungrouped_metrics.append(metric_info)
    
    # Format output
    if not all_metrics:
        return [
            TextContent(
                type="text",
                text="No metrics found"
            )
        ]
    
    result = f"Found {len(all_metrics)} metric(s)"
    if explore_filter:
        result += f" (filtered by '{explore_filter}')"
    result += ":\n\n"
    
    # Display grouped metrics
    for explore, metrics in sorted(metrics_by_explore.items()):
        result += f"📊 **{explore}**\n"
        for metric in sorted(metrics, key=lambda x: x['name']):
            result += f"  • {metric['name']}"
            if metric.get('label') and metric['label'] != metric['name']:
                result += f" ({metric['label']})"
            result += f" - {metric.get('type', 'unknown')}"
            
            # Add source indicator
            source = metric.get('source', 'unknown')
            if source == 'both':
                result += " [SL+LD]"
            elif source == 'semantic_layer':
                result += " [SL]"
            elif source == 'lightdash':
                result += " [LD]"
            
            if metric.get('description'):
                result += f"\n    {metric['description']}"
            result += "\n"
        result += "\n"
    
    # Display ungrouped metrics
    if ungrouped_metrics:
        result += "📊 **Other Metrics**\n"
        for metric in sorted(ungrouped_metrics, key=lambda x: x['name']):
            result += f"  • {metric['name']}"
            if metric.get('label') and metric['label'] != metric['name']:
                result += f" ({metric['label']})"
            result += f" - {metric.get('type', 'unknown')}"
            
            source = metric.get('source', 'unknown')
            if source == 'semantic_layer':
                result += " [SL]"
            
            if metric.get('description'):
                result += f"\n    {metric['description']}"
            result += "\n"
    
    # Add legend
    result += "\n---\n"
    result += "Legend: [SL] = Semantic Layer only, [LD] = Lightdash only, [SL+LD] = Both sources"
    
    return [TextContent(type="text", text=result.strip())]