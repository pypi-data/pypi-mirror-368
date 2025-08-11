#!/usr/bin/env python3
"""
XAU Gold MCP Server - 清理版本，只提供準確的數據
提供實時價格、日線歷史和基於真實數據的技術指標
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Sequence
import pandas as pd

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.models import Tool
from mcp.types import TextContent
import akshare as ak

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("xau-server")

# 創建服務器實例
app = Server("xau-gold-server")

# 工具函數
def safe_float_convert(value) -> float:
    """安全轉換為float"""
    try:
        if pd.isna(value) or value is None:
            return 0.0
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def safe_str_convert(value) -> str:
    """安全轉換為字符串"""
    try:
        if pd.isna(value) or value is None:
            return ""
        return str(value)
    except (ValueError, TypeError):
        return ""

@app.list_tools()
async def list_tools() -> List[Tool]:
    """列出可用工具"""
    return [
        Tool(
            name="get_xau_realtime",
            description="獲取XAU黃金實時價格。Get XAU gold realtime price.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_xau_daily_history",
            description="獲取XAU黃金日線歷史數據。Get XAU gold daily historical data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "default": 30,
                        "description": "獲取最近多少天的數據 (Recent days of data)"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "開始日期 YYYY-MM-DD 格式 (Start date in YYYY-MM-DD format)"
                    },
                    "end_date": {
                        "type": "string", 
                        "description": "結束日期 YYYY-MM-DD 格式 (End date in YYYY-MM-DD format)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_xau_technical_indicators",
            description="計算XAU黃金技術指標(SMA, RSI, MACD)，基於真實日線數據。Calculate XAU technical indicators based on real daily data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "indicators": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["sma20", "sma50", "rsi", "macd"]},
                        "default": ["sma20", "rsi"],
                        "description": "要計算的指標 (Indicators to calculate)"
                    }
                },
                "required": []
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """調用工具"""
    try:
        if name == "get_xau_realtime":
            result = await get_xau_realtime()
        elif name == "get_xau_daily_history":
            result = await get_xau_daily_history(
                days=arguments.get("days", 30),
                start_date=arguments.get("start_date"),
                end_date=arguments.get("end_date")
            )
        elif name == "get_xau_technical_indicators":
            result = await get_xau_technical_indicators(
                indicators=arguments.get("indicators", ["sma20", "rsi"])
            )
        else:
            result = {"status": "error", "error": f"Unknown tool: {name}"}
        
        # 格式化輸出
        if result["status"] == "success":
            output = format_success_response(result, name)
        else:
            output = f"❌ 錯誤: {result.get('error', 'Unknown error')}"
        
        return [TextContent(type="text", text=output)]
        
    except Exception as e:
        logger.error(f"Tool {name} error: {e}")
        return [TextContent(type="text", text=f"❌ 工具執行錯誤: {e}")]

def format_success_response(result: Dict[str, Any], tool_name: str) -> str:
    """格式化成功響應"""
    data = result.get("data", {})
    
    if tool_name == "get_xau_realtime":
        latest = data.get("latest", {})
        return f"""✅ XAU 黃金實時價格

💰 當前價格: ${latest.get('close', 'N/A')}
📈 開盤價: ${latest.get('open', 'N/A')}
📊 最高價: ${latest.get('high', 'N/A')}
📉 最低價: ${latest.get('low', 'N/A')}
🔄 漲跌: {latest.get('change', 'N/A')} ({latest.get('change_percent', 'N/A')}%)
🕐 時間: {latest.get('datetime', 'N/A')}
"""
    
    elif tool_name == "get_xau_daily_history":
        history = data.get("history", [])
        return f"""✅ XAU 黃金日線歷史數據

📊 數據期間: {data.get('period', 'N/A')}
💰 最新收盤: ${history[-1].get('close', 'N/A') if history else 'N/A'}
📅 最新日期: {history[-1].get('date', 'N/A') if history else 'N/A'}
📈 期間最高: ${data.get('period_high', 'N/A')}
📉 期間最低: ${data.get('period_low', 'N/A')}
📊 總記錄數: {data.get('total_records', 0)} 天

最近5天收盤價:
{chr(10).join([f"  {h.get('date', 'N/A')}: ${h.get('close', 'N/A')}" for h in history[-5:]])}
"""
    
    elif tool_name == "get_xau_technical_indicators":
        indicators = data.get("indicators", {})
        return f"""✅ XAU 黃金技術指標（基於真實日線數據）

時間週期: {data.get('period', 'daily')}
數據來源: {data.get('based_on', 'Real OHLC data')}
計算指標:
{chr(10).join([f"  {name}: {value}" for name, value in indicators.items()])}

數據時間: {data.get('timestamp', 'N/A')}
"""
    
    return "✅ 操作完成"

# 核心數據獲取函數
async def get_xau_realtime() -> Dict[str, Any]:
    """獲取XAU實時價格"""
    result = {"status": "success", "data": {}}
    
    try:
        # 使用akshare获取黄金实时数据
        df = ak.futures_foreign_commodity_realtime(symbol='XAU')
        
        if df.empty:
            result["status"] = "error"
            result["error"] = "XAU實時數據為空"
        else:
            # 提取數據
            row = df.iloc[0]
            
            # 獲取價格信息
            current_price = safe_float_convert(row['最新价'])
            open_price = safe_float_convert(row['开盘价'])
            high_price = safe_float_convert(row['最高价'])
            low_price = safe_float_convert(row['最低价'])
            price_change = safe_float_convert(row['涨跌额'])
            change_percent = safe_float_convert(row['涨跌幅'])
            
            # 獲取時間信息
            trade_time = safe_str_convert(row.get('行情时间', ''))
            trade_date = safe_str_convert(row.get('日期', ''))
            
            result["data"] = {
                "symbol": "XAUUSD",
                "source": "AkShare Foreign Commodity Realtime",
                "latest": {
                    "date": trade_date,
                    "time": trade_time,
                    "datetime": f"{trade_date} {trade_time}" if trade_date and trade_time else datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "open": open_price,
                    "high": high_price,
                    "low": low_price,
                    "close": current_price,
                    "change": price_change,
                    "change_percent": round(change_percent, 3) if change_percent != 0 else 0.0
                },
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        logger.error(f"獲取XAU實時數據失敗: {e}")
    
    return result

async def get_xau_daily_history(days: int = 30, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
    """獲取XAU日線歷史數據 - 支持日期範圍"""
    result = {"status": "success", "data": {}}
    
    try:
        # 使用akshare获取黄金历史数据
        df = ak.futures_foreign_hist(symbol='XAU')
        
        if df.empty:
            result["status"] = "error"
            result["error"] = "XAU歷史數據為空"
        else:
            # 確保日期列是datetime類型
            df['date'] = pd.to_datetime(df['date'])
            
            # 根據參數篩選數據
            if start_date and end_date:
                # 使用指定日期範圍
                start_dt = pd.to_datetime(start_date)
                end_dt = pd.to_datetime(end_date)
                filtered_df = df[(df['date'] >= start_dt) & (df['date'] <= end_dt)]
                period_desc = f"從 {start_date} 到 {end_date}"
            elif start_date:
                # 只有開始日期
                start_dt = pd.to_datetime(start_date)
                filtered_df = df[df['date'] >= start_dt]
                period_desc = f"從 {start_date} 開始"
            elif end_date:
                # 只有結束日期
                end_dt = pd.to_datetime(end_date)
                filtered_df = df[df['date'] <= end_dt]
                period_desc = f"到 {end_date} 為止"
            else:
                # 使用days參數
                filtered_df = df.tail(days)
                period_desc = f"最近 {days} 天"
            
            if filtered_df.empty:
                result["status"] = "error"
                result["error"] = f"指定日期範圍內無數據: {period_desc}"
            else:
                # 重新轉換date為字符串格式
                filtered_df = filtered_df.copy()
                filtered_df['date'] = filtered_df['date'].dt.strftime('%Y-%m-%d')
                
                # 處理歷史數據
                history = []
                for _, row in filtered_df.iterrows():
                    history.append({
                        "date": str(row['date']),
                        "open": safe_float_convert(row['open']),
                        "high": safe_float_convert(row['high']),
                        "low": safe_float_convert(row['low']),
                        "close": safe_float_convert(row['close']),
                        "volume": safe_float_convert(row['volume'])
                    })
                
                # 計算期間最高最低
                period_high = filtered_df['high'].max()
                period_low = filtered_df['low'].min()
                
                result["data"] = {
                    "symbol": "XAUUSD", 
                    "period": period_desc,
                    "history": history,
                    "period_high": safe_float_convert(period_high),
                    "period_low": safe_float_convert(period_low),
                    "total_records": len(history),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        logger.error(f"獲取XAU歷史數據失敗: {e}")
    
    return result

async def get_xau_technical_indicators(indicators: List[str] = ["sma20", "rsi"]) -> Dict[str, Any]:
    """計算XAU技術指標 - 基於真實日線數據"""
    result = {"status": "success", "data": {}}
    
    try:
        # 使用真實的日線數據
        df = ak.futures_foreign_hist(symbol='XAU')
        
        if df.empty:
            result["status"] = "error"
            result["error"] = "無法獲取日線數據計算指標"
        else:
            calculated_indicators = {}
            
            # 獲取收盤價序列
            if 'close' in df.columns:
                closes = df['close'].astype(float)
                
                # 計算各種指標
                for indicator in indicators:
                    if indicator == "sma20":
                        sma20 = closes.rolling(window=20).mean()
                        calculated_indicators["SMA20"] = f"${safe_float_convert(sma20.iloc[-1]):.2f}" if pd.notnull(sma20.iloc[-1]) else "N/A"
                    
                    elif indicator == "sma50":
                        sma50 = closes.rolling(window=50).mean()
                        calculated_indicators["SMA50"] = f"${safe_float_convert(sma50.iloc[-1]):.2f}" if pd.notnull(sma50.iloc[-1]) else "N/A"
                    
                    elif indicator == "rsi":
                        # 計算RSI
                        delta = closes.diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rs = gain / loss
                        rsi = 100 - (100 / (1 + rs))
                        calculated_indicators["RSI"] = f"{safe_float_convert(rsi.iloc[-1]):.2f}" if pd.notnull(rsi.iloc[-1]) else "N/A"
                    
                    elif indicator == "macd":
                        # 計算MACD
                        ema12 = closes.ewm(span=12).mean()
                        ema26 = closes.ewm(span=26).mean()
                        macd = ema12 - ema26
                        calculated_indicators["MACD"] = f"{safe_float_convert(macd.iloc[-1]):.2f}" if pd.notnull(macd.iloc[-1]) else "N/A"
            
            result["data"] = {
                "symbol": "XAUUSD",
                "period": "daily",
                "indicators": calculated_indicators,
                "based_on": "Real daily OHLC data from akshare",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        logger.error(f"計算XAU技術指標失敗: {e}")
    
    return result

async def main():
    """啟動服務器"""
    # 初始化選項
    init_options = InitializationOptions(
        server_name="xau-gold-server",
        server_version="2.0.0",
        capabilities=app.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={}
        )
    )
    
    async with app.run_server() as server:
        logger.info("XAU Gold MCP Server is running...")
        logger.info("Available tools: get_xau_realtime, get_xau_daily_history, get_xau_technical_indicators")
        await server.wait_for_shutdown()

if __name__ == "__main__":
    asyncio.run(main())