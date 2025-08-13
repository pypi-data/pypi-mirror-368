import json
import httpx
import argparse
from typing import Any, Dict, List, Union
import re
import asyncio
import time
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# 初始化
mcp = FastMCP("QueryWeatherMcp")

# api配置
OPENWEATHER_API_BASE = "https://weather.cma.cn/api/map/weather/1"
USER_AGENT = "weather-app/1.0.0"
# 超时与缓存设置
HTTP_TIMEOUT_SECONDS = 5.0
TOOL_TIMEOUT_SECONDS = 8.0
CACHE_TTL_SECONDS = 300.0

# 简单的内存缓存
_weather_cache_data: Dict[str, Any] | None = None
_weather_cache_ts: float | None = None

async def get_weather_data() -> Dict[str, Any] | Dict[str, str]:
    """
    获取天气数据
    """
    async with httpx.AsyncClient(
        headers={"User-Agent": USER_AGENT},
        timeout=httpx.Timeout(HTTP_TIMEOUT_SECONDS)
    ) as client:
        try:
            # 保留可能需要的时间戳作为参数避免缓存（非必须）
            response = await client.get(OPENWEATHER_API_BASE, params={"t": str(int(time.time()))})
            response.raise_for_status()
            data = response.json()
            return data
        except httpx.HTTPStatusError as e:
            print(f"请求失败: {e}")
            return {"error":f"请求失败: {e.request.status_code}"}
        except Exception as e:
            print(f"发生错误: {e}")
            return {"error":f"发生错误: {str(e)}"}

def _load_local_fallback() -> Dict[str, Any] | Dict[str, str]:
    """从本地 `weather.json` 读取回退数据。"""
    try:
        path = Path(__file__).parent / "weather.json"
        if not path.exists() or path.stat().st_size == 0:
            return {"error": "本地回退数据不存在或为空"}
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"error": f"读取本地回退数据失败: {e}"}

async def get_weather_data_cached() -> Dict[str, Any] | Dict[str, str]:
    """带缓存与本地回退的获取逻辑，尽量避免超时。"""
    global _weather_cache_data, _weather_cache_ts

    now = time.time()
    # 命中有效缓存
    if _weather_cache_data is not None and _weather_cache_ts is not None:
        if (now - _weather_cache_ts) < CACHE_TTL_SECONDS:
            return _weather_cache_data

    # 尝试网络请求
    try:
        data = await get_weather_data()
        # 如果不是错误则写入缓存
        if not (isinstance(data, dict) and "error" in data):
            _weather_cache_data = data
            _weather_cache_ts = now
            return data
        # 网络返回错误时，尝试使用旧缓存
        if _weather_cache_data is not None:
            return _weather_cache_data
        # 再降级到本地
        return _load_local_fallback()
    except Exception:
        # 任何异常降级
        if _weather_cache_data is not None:
            return _weather_cache_data
        return _load_local_fallback()

def _parse_city_query(city_query: str) -> List[str]:
    """解析城市查询字符串，支持用逗号/空格分隔。"""
    if not city_query:
        return []
    # 将中文逗号替换为英文逗号，统一切分
    normalized = city_query.replace("，", ",")
    # 先按逗号，再降级按空白
    parts = [p.strip() for p in normalized.split(",") if p.strip()]
    if not parts:
        parts = [p.strip() for p in normalized.split() if p.strip()]
    return parts

def format_weather(data: Union[Dict[str, Any], str], city_query: str) -> str:
    """
    格式化天气数据
    """
    # 1) 错误透传
    if isinstance(data, dict) and "error" in data:
        return f"⚠ {data['error']}"

    # 2) 抽取城市数组
    cities_data: List[list] = []
    try:
        if isinstance(data, str):
            json_match = re.search(r'\{.*\}', data, re.DOTALL)
            if not json_match:
                return "⚠ 未找到有效的JSON数据"
            parsed = json.loads(json_match.group())
        else:
            parsed = data
        cities_data = parsed["data"]["city"]
        if not isinstance(cities_data, list):
            return "⚠ 返回数据格式不正确: data.city 不是列表"
    except Exception as e:
        return f"⚠ 解析JSON失败: {e}"

    # 3) 解析查询关键词
    query_names = _parse_city_query(city_query)
    if not query_names:
        return "⚠ 请输入要查询的城市名称（可使用逗号或空格分隔）"

    # 4) 查找匹配
    result: Dict[str, List[Dict[str, Any]]] = {}
    for query_name in query_names:
        found: List[Dict[str, Any]] = []
        for city_row in cities_data:
            try:
                # city_row 索引: [?, 城市名, ?, ?, 纬度, 经度, 温度, 天气, ?, 风向, 风力, 最低温, 夜间天气, ?, 夜间风向, 夜间风力, ...]
                if query_name in city_row[1]:
                    found.append({
                        "城市名称": city_row[1],
                        "温度": f"{city_row[6]}°C",
                        "天气": city_row[7],
                        "风向": city_row[9],
                        "风力": city_row[10],
                        "最低温度": f"{city_row[11]}°C",
                        "夜间天气": city_row[12],
                        "夜间风向": city_row[14],
                        "夜间风力": city_row[15],
                        "位置": f"纬度:{city_row[4]}, 经度:{city_row[5]}",
                    })
            except Exception:
                # 单行异常不影响整体
                continue
        result[query_name] = found

    # 5) 返回字符串（MCP tool 要求返回 str）
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
async def query_weather(city: str) -> str:
    """
    查询天气MCP工具
    """
    data = await get_weather_data()
    return format_weather(data, city)
def main():
    parser = argparse.ArgumentParser(description="天气查询工具")
    args = parser.parse_args()
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
