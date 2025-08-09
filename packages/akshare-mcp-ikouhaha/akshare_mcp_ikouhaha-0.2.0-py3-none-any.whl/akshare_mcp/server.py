#!/usr/bin/env python3
"""
Akshare MCP Server - 中国金融数据接口MCP服务器

提供中国股票、期货、基金等金融数据的MCP服务器。
Supports real-time and historical data with 5-minute K-line data.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence

import akshare as ak
import pandas as pd
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("akshare-mcp-server")

# 创建MCP服务器实例
app = Server("akshare-mcp")

def safe_float_convert(value: Any) -> Optional[float]:
    """安全地将值转换为浮点数"""
    if pd.isna(value):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def safe_str_convert(value: Any) -> str:
    """安全地将值转换为字符串"""
    if pd.isna(value):
        return ""
    return str(value)

@app.list_tools()
async def list_tools() -> List[Tool]:
    """列出可用的工具"""
    return [
        Tool(
            name="get_stock_data",
            description="获取股票数据，支持分钟级和日线数据。Get stock data with minute and daily intervals.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "股票代码，如 '000001' (Stock symbol, e.g., '000001')"
                    },
                    "period": {
                        "type": "string",
                        "enum": ["5min", "15min", "30min", "60min", "daily", "weekly", "monthly"],
                        "default": "daily",
                        "description": "数据周期 (Data period)"
                    },
                    "adjust": {
                        "type": "string",
                        "enum": ["qfq", "hfq", ""],
                        "default": "qfq",
                        "description": "复权类型：qfq前复权，hfq后复权，空字符串不复权 (Adjustment type)"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_futures_data",
            description="获取期货数据，支持分钟级和日线数据。Get futures data with minute and daily intervals.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "期货代码，如 'AU0'（黄金主力）、'AG0'（白银主力） (Futures symbol)"
                    },
                    "period": {
                        "type": "string",
                        "enum": ["5min", "15min", "30min", "60min", "daily"],
                        "default": "daily",
                        "description": "数据周期 (Data period)"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_gold_data",
            description="获取黄金数据，支持期货和现货。Get gold data for futures and spot.",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_type": {
                        "type": "string",
                        "enum": ["futures", "spot", "futures_5min"],
                        "default": "futures",
                        "description": "数据类型：futures期货，spot现货，futures_5min期货5分钟数据 (Data type)"
                    },
                    "period": {
                        "type": "string",
                        "enum": ["5min", "15min", "30min", "60min", "daily"],
                        "default": "daily",
                        "description": "数据周期，仅对期货有效 (Data period, for futures only)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_market_overview",
            description="获取市场概览信息，包括A股指数、成交量等。Get market overview including A-share indices and volume.",
            inputSchema={
                "type": "object",
                "properties": {
                    "market": {
                        "type": "string",
                        "enum": ["a_share", "us", "hk"],
                        "default": "a_share",
                        "description": "市场类型：A股、美股、港股 (Market type)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="search_stock",
            description="搜索股票信息，根据股票名称或代码查找。Search stock information by name or symbol.",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索关键词，可以是股票名称或代码 (Search keyword, stock name or symbol)"
                    }
                },
                "required": ["keyword"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """调用工具"""
    try:
        if name == "get_stock_data":
            result = await get_stock_data(
                symbol=arguments["symbol"],
                period=arguments.get("period", "daily"),
                adjust=arguments.get("adjust", "qfq")
            )
        elif name == "get_futures_data":
            result = await get_futures_data(
                symbol=arguments["symbol"],
                period=arguments.get("period", "daily")
            )
        elif name == "get_gold_data":
            result = await get_gold_data(
                data_type=arguments.get("data_type", "futures"),
                period=arguments.get("period", "daily")
            )
        elif name == "get_market_overview":
            result = await get_market_overview(
                market=arguments.get("market", "a_share")
            )
        elif name == "search_stock":
            result = await search_stock(
                keyword=arguments["keyword"]
            )
        else:
            result = {"status": "error", "error": f"Unknown tool: {name}"}
        
        # 格式化输出
        if result["status"] == "success":
            output = format_success_response(result, name)
        else:
            output = f"❌ 错误 (Error): {result.get('error', 'Unknown error')}"
        
        return [TextContent(type="text", text=output)]
        
    except Exception as e:
        logger.error(f"Tool {name} error: {e}")
        return [TextContent(type="text", text=f"❌ 工具执行错误 (Tool execution error): {str(e)}")]

def format_success_response(result: Dict[str, Any], tool_name: str) -> str:
    """格式化成功响应"""
    data = result.get("data", {})
    
    if tool_name == "get_stock_data" or tool_name == "get_futures_data":
        latest = data.get("latest", {})
        output = f"""✅ {data.get('symbol', 'N/A')} - {data.get('period', 'N/A')} 数据

📊 最新数据 (Latest Data):
时间: {latest.get('datetime', latest.get('date', 'N/A'))}
开盘: {latest.get('open', 'N/A')}
最高: {latest.get('high', 'N/A')}
最低: {latest.get('low', 'N/A')}
收盘: {latest.get('close', 'N/A')}
成交量: {latest.get('volume', 'N/A')}"""
        
        if 'change_rate' in latest:
            output += f"\n涨跌幅: {latest.get('change_rate', 'N/A')}%"
        
        if 'recent_10' in data and len(data['recent_10']) > 0:
            output += f"\n\n📈 最近10条记录 (Recent 10 records): {len(data['recent_10'])}条"
        
        output += f"\n\n📈 总记录数: {data.get('total_records', 0)}条"
        
    elif tool_name == "get_gold_data":
        if "latest" in data:
            latest = data.get("latest", {})
            output = f"""✅ 黄金数据 (Gold Data)

📊 最新数据 (Latest):
时间: {latest.get('datetime', latest.get('date', 'N/A'))}
收盘: {latest.get('close', 'N/A')}
成交量: {latest.get('volume', 'N/A')}

说明: {data.get('description', 'N/A')}"""
        else:
            output = f"""ℹ️ 黄金数据信息

说明: {data.get('description', 'N/A')}
备注: {data.get('note', 'N/A')}"""
    
    elif tool_name == "get_market_overview":
        output = f"""✅ 市场概览 (Market Overview)

{data.get('description', '市场数据')}
数据时间: {data.get('timestamp', 'N/A')}"""
        
        if 'indices' in data:
            output += "\n\n📊 主要指数:"
            for index in data.get('indices', []):
                output += f"\n{index.get('name', 'N/A')}: {index.get('value', 'N/A')}"
    
    elif tool_name == "search_stock":
        results = data.get('results', [])
        output = f"""✅ 股票搜索结果 (Search Results)

关键词: {data.get('keyword', 'N/A')}
找到 {len(results)} 个结果:
"""
        for i, stock in enumerate(results[:10], 1):  # 只显示前10个结果
            output += f"{i}. {stock.get('name', 'N/A')} ({stock.get('symbol', 'N/A')})\n"
    
    else:
        output = f"✅ 操作完成\n\n{str(data)}"
    
    return output

async def get_stock_data(symbol: str, period: str = "daily", adjust: str = "qfq") -> Dict[str, Any]:
    """获取股票数据"""
    result = {"status": "success", "data": {}, "period": period}
    
    try:
        if period in ["5min", "15min", "30min", "60min"]:
            # 分钟数据
            period_map = {"5min": "5", "15min": "15", "30min": "30", "60min": "60"}
            minute_period = period_map[period]
            
            try:
                # 方法1：使用 stock_zh_a_minute
                stock_data = ak.stock_zh_a_minute(symbol=f"sz{symbol}", period=minute_period, adjust=adjust)
            except:
                try:
                    # 方法2：备用方法
                    stock_data = ak.stock_zh_a_hist_min_em(symbol=symbol, period=minute_period, adjust=adjust)
                except:
                    # 方法3：最后备用
                    stock_data = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust=adjust).tail(1)
            
            if not stock_data.empty:
                latest = stock_data.iloc[-1]
                recent_data = stock_data.tail(10)
                
                result["data"] = {
                    "symbol": symbol,
                    "period": period,
                    "total_records": len(stock_data),
                    "latest": {
                        "datetime": str(latest.get('day', latest.get('time', latest.name if hasattr(latest, 'name') else 'N/A'))),
                        "open": safe_float_convert(latest.get('open', latest.get('开盘', 0))),
                        "high": safe_float_convert(latest.get('high', latest.get('最高', 0))),
                        "low": safe_float_convert(latest.get('low', latest.get('最低', 0))),
                        "close": safe_float_convert(latest.get('close', latest.get('收盘', 0))),
                        "volume": safe_float_convert(latest.get('volume', latest.get('成交量', 0)))
                    },
                    "recent_10": []
                }
                
                # 添加最近10条记录
                for _, row in recent_data.iterrows():
                    result["data"]["recent_10"].append({
                        "datetime": str(row.get('day', row.get('time', row.name if hasattr(row, 'name') else 'N/A'))),
                        "close": safe_float_convert(row.get('close', row.get('收盘', 0)))
                    })
        
        else:
            # 日线/周线/月线数据
            stock_data = ak.stock_zh_a_hist(symbol=symbol, period=period, adjust=adjust)
            
            if not stock_data.empty:
                latest = stock_data.iloc[-1]
                recent_data = stock_data.tail(10)
                
                result["data"] = {
                    "symbol": symbol,
                    "period": period,
                    "total_records": len(stock_data),
                    "latest": {
                        "date": str(latest.get('日期', 'N/A')),
                        "open": safe_float_convert(latest.get('开盘', 0)),
                        "high": safe_float_convert(latest.get('最高', 0)),
                        "low": safe_float_convert(latest.get('最低', 0)),
                        "close": safe_float_convert(latest.get('收盘', 0)),
                        "volume": safe_float_convert(latest.get('成交量', 0)),
                        "change_rate": safe_float_convert(latest.get('涨跌幅', 0))
                    },
                    "recent_10": []
                }
                
                # 添加最近10条记录
                for _, row in recent_data.iterrows():
                    result["data"]["recent_10"].append({
                        "date": str(row.get('日期', 'N/A')),
                        "close": safe_float_convert(row.get('收盘', 0)),
                        "change_rate": safe_float_convert(row.get('涨跌幅', 0))
                    })
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        logger.error(f"获取股票数据失败: {e}")
    
    return result

async def get_futures_data(symbol: str, period: str = "daily") -> Dict[str, Any]:
    """获取期货数据"""
    result = {"status": "success", "data": {}, "period": period}
    
    try:
        if period in ["5min", "15min", "30min", "60min"]:
            # 期货分钟数据
            period_map = {"5min": "5", "15min": "15", "30min": "30", "60min": "60"}
            minute_period = period_map[period]
            
            # 构建期货合约代码
            if symbol == "AU0":  # 黄金主力
                contract_symbol = "AU2502"  # 示例：2025年2月合约
            elif symbol == "AG0":  # 白银主力
                contract_symbol = "AG2502"
            else:
                contract_symbol = symbol
            
            try:
                futures_data = ak.futures_zh_minute_sina(symbol=contract_symbol, period=minute_period)
            except:
                # 备用方法：使用日线数据
                end_date = datetime.now().strftime("%Y%m%d")
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
                futures_data = ak.futures_main_sina(symbol=symbol, start_date=start_date, end_date=end_date)
            
            if not futures_data.empty:
                latest = futures_data.iloc[-1]
                recent_data = futures_data.tail(10)
                
                result["data"] = {
                    "symbol": symbol,
                    "contract": contract_symbol,
                    "period": period,
                    "total_records": len(futures_data),
                    "latest": {
                        "datetime": str(latest.get('datetime', latest.get('date', latest.name if hasattr(latest, 'name') else 'N/A'))),
                        "open": safe_float_convert(latest.get('open', 0)),
                        "high": safe_float_convert(latest.get('high', 0)),
                        "low": safe_float_convert(latest.get('low', 0)),
                        "close": safe_float_convert(latest.get('close', 0)),
                        "volume": safe_float_convert(latest.get('volume', 0)),
                        "hold": safe_float_convert(latest.get('hold', 0))
                    },
                    "recent_10": []
                }
                
                # 添加最近10条记录
                for _, row in recent_data.iterrows():
                    result["data"]["recent_10"].append({
                        "datetime": str(row.get('datetime', row.get('date', row.name if hasattr(row, 'name') else 'N/A'))),
                        "close": safe_float_convert(row.get('close', 0))
                    })
        
        else:
            # 日线数据
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
            
            futures_data = ak.futures_main_sina(symbol=symbol, start_date=start_date, end_date=end_date)
            
            if not futures_data.empty:
                latest = futures_data.iloc[-1]
                
                result["data"] = {
                    "symbol": symbol,
                    "period": "daily",
                    "total_records": len(futures_data),
                    "latest": {
                        "date": str(latest.get('date', 'N/A')),
                        "open": safe_float_convert(latest.get('open', 0)),
                        "high": safe_float_convert(latest.get('high', 0)),
                        "low": safe_float_convert(latest.get('low', 0)),
                        "close": safe_float_convert(latest.get('close', 0)),
                        "volume": safe_float_convert(latest.get('volume', 0))
                    }
                }
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        logger.error(f"获取期货数据失败: {e}")
    
    return result

async def get_gold_data(data_type: str = "futures", period: str = "daily") -> Dict[str, Any]:
    """获取黄金数据"""
    result = {"status": "success", "data": {}}
    
    try:
        if data_type == "futures" or data_type == "futures_5min":
            # 黄金期货数据
            if data_type == "futures_5min":
                period = "5min"
            
            gold_data = await get_futures_data("AU0", period)
            result = gold_data
            result["data"]["description"] = f"黄金期货{period}数据"
            
        elif data_type == "spot":
            # 现货黄金数据（通常是日线）
            result["data"] = {
                "description": "现货黄金数据（目前仅支持日线级别）",
                "note": "如需5分钟数据，请使用 data_type='futures_5min'"
            }
    
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result

async def get_market_overview(market: str = "a_share") -> Dict[str, Any]:
    """获取市场概览"""
    result = {"status": "success", "data": {}}
    
    try:
        if market == "a_share":
            # A股市场概览
            try:
                # 获取主要指数
                sh_index = ak.stock_zh_index_daily(symbol="sh000001")  # 上证指数
                if not sh_index.empty:
                    latest_sh = sh_index.iloc[-1]
                    
                result["data"] = {
                    "market": "A股",
                    "description": "A股市场概览",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "indices": [
                        {
                            "name": "上证指数",
                            "value": safe_float_convert(latest_sh.get('close', 0)),
                            "change": safe_float_convert(latest_sh.get('change', 0))
                        }
                    ]
                }
            except:
                result["data"] = {
                    "market": "A股",
                    "description": "A股市场概览（简化版）",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "note": "详细数据暂时无法获取"
                }
        
        else:
            result["data"] = {
                "market": market,
                "description": f"{market}市场概览",
                "note": "暂不支持该市场数据"
            }
    
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result

async def search_stock(keyword: str) -> Dict[str, Any]:
    """搜索股票"""
    result = {"status": "success", "data": {}}
    
    try:
        # 获取股票基本信息
        try:
            stock_info = ak.stock_info_a_code_name()
            
            # 搜索匹配的股票
            matches = stock_info[
                stock_info['code'].str.contains(keyword, na=False) | 
                stock_info['name'].str.contains(keyword, na=False)
            ]
            
            results = []
            for _, stock in matches.head(20).iterrows():  # 最多返回20个结果
                results.append({
                    "symbol": str(stock.get('code', 'N/A')),
                    "name": str(stock.get('name', 'N/A'))
                })
            
            result["data"] = {
                "keyword": keyword,
                "results": results
            }
            
        except:
            # 备用搜索方法
            result["data"] = {
                "keyword": keyword,
                "results": [],
                "note": "股票搜索功能暂时不可用，请直接使用股票代码查询数据"
            }
    
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result

def main():
    """主函数"""
    async def run_server():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    
    asyncio.run(run_server())

if __name__ == "__main__":
    main()