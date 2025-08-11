#!/usr/bin/env python3
"""
Akshare MCP Server - XAUUSD Gold Data
簡化版本，專注於XAUUSD黃金數據獲取
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List
import akshare as ak
import pandas as pd

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("xau-mcp-server")

# 创建MCP服务器
app = Server("xau-gold-mcp")

@app.list_tools()
async def list_tools() -> List[Tool]:
    """列出可用工具"""
    return [
        Tool(
            name="get_xau_realtime",
            description="获取XAUUSD黄金实时价格数据",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_xau_daily",
            description="获取XAUUSD黄金日线历史数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "获取最近N天的数据，默认30天",
                        "default": 30
                    }
                },
                "required": []
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """调用工具"""
    try:
        if name == "get_xau_realtime":
            return await get_xau_realtime()
        elif name == "get_xau_daily":
            days = arguments.get("days", 30)
            return await get_xau_daily(days)
        else:
            return [TextContent(type="text", text=f"未知工具: {name}")]
    except Exception as e:
        logger.error(f"工具调用失败 {name}: {e}")
        return [TextContent(type="text", text=f"错误: {str(e)}")]

async def get_xau_realtime() -> List[TextContent]:
    """获取XAUUSD实时价格"""
    try:
        # 使用akshare获取黄金实时数据
        df = ak.futures_foreign_commodity_realtime(symbol='XAU')
        
        if df.empty:
            return [TextContent(type="text", text="❌ 无法获取XAUUSD实时数据")]
        
        # 提取数据
        row = df.iloc[0]
        price = float(row['最新价'])
        change = float(row['涨跌'])
        change_pct = float(row['涨跌幅'])
        
        result = f"""✅ XAUUSD 黄金实时价格

💰 当前价格: ${price:.2f}
📈 涨跌幅: ${change:.2f} ({change_pct:.2f}%)
🕒 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📊 数据来源: AkShare"""
        
        return [TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"获取实时数据失败: {e}")
        return [TextContent(type="text", text=f"❌ 获取实时数据失败: {str(e)}")]

async def get_xau_daily(days: int = 30) -> List[TextContent]:
    """获取XAUUSD日线数据"""
    try:
        # 使用akshare获取黄金历史数据
        df = ak.futures_foreign_hist(symbol='XAU')
        
        if df.empty:
            return [TextContent(type="text", text="❌ 无法获取XAUUSD历史数据")]
        
        # 获取最近N天的数据
        recent_df = df.tail(days)
        
        # 计算统计信息
        latest = recent_df.iloc[-1]
        highest = recent_df['high'].max()
        lowest = recent_df['low'].min()
        
        result = f"""✅ XAUUSD 黄金日线数据 (最近{days}天)

📅 数据期间: {recent_df.iloc[0]['date']} 至 {latest['date']}
💰 最新收盘: ${latest['close']:.2f}
📈 期间最高: ${highest:.2f}
📉 期间最低: ${lowest:.2f}
📊 数据记录: {len(recent_df)} 天

最近5天收盘价:"""
        
        # 添加最近5天数据
        recent_5 = recent_df.tail(5)
        for _, row in recent_5.iterrows():
            result += f"\n  {row['date']}: ${row['close']:.2f}"
        
        result += f"\n\n📊 数据来源: AkShare"
        
        return [TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"获取历史数据失败: {e}")
        return [TextContent(type="text", text=f"❌ 获取历史数据失败: {str(e)}")]

async def main():
    """运行服务器"""
    logger.info("启动XAUUSD Gold MCP服务器...")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

def cli_main():
    """CLI入口点"""
    asyncio.run(main())

if __name__ == "__main__":
    cli_main()