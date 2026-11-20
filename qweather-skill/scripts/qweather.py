#!/usr/bin/env python3
"""
和风天气 API 客户端
提供实时天气、天气预报、空气质量、预警等功能

文档: https://dev.qweather.com/docs/api/
"""

import os
import json
import time
import httpx
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


# 中国主要城市 Location ID 映射
CITY_ID_MAP = {
    "北京": "101010100",
    "上海": "101020100",
    "广州": "101280101",
    "深圳": "101280601",
    "杭州": "101210101",
    "南京": "101190101",
    "成都": "101270101",
    "重庆": "101040100",
    "武汉": "101200101",
    "西安": "101110101",
    "天津": "101030100",
    "苏州": "101190401",
    "郑州": "101180101",
    "长沙": "101250101",
    "青岛": "101120201",
    "大连": "101070201",
    "宁波": "101210401",
    "厦门": "101230201",
    "福州": "101230101",
    "合肥": "101220101",
    "哈尔滨": "101050101",
    "沈阳": "101070101",
    "长春": "101060101",
    "石家庄": "101090101",
    "济南": "101120101",
    "太原": "101100101",
    "昆明": "101290101",
    "贵阳": "101260101",
    "南宁": "101300101",
    "海口": "101310101",
    "拉萨": "101140101",
    "乌鲁木齐": "101130101",
    "兰州": "101160101",
    "银川": "101170101",
    "西宁": "101150101",
    "呼和浩特": "101080101",
    "南昌": "101240101",
}


@dataclass
class QWeatherConfig:
    """和风天气配置"""
    api_key: str
    api_host: str = "api.qweather.com"
    timeout: int = 10
    
    @classmethod
    def from_env(cls) -> "QWeatherConfig":
        """从环境变量加载配置"""
        api_key = os.getenv("QWEATHER_API_KEY", "")
        api_host = os.getenv("QWEATHER_API_HOST", "api.qweather.com")
        
        if not api_key:
            raise ValueError("QWEATHER_API_KEY 未配置，请在 keys.env 中设置")
        
        return cls(api_key=api_key, api_host=api_host)


class QWeatherClient:
    """和风天气 API 客户端"""
    
    def __init__(self, config: Optional[QWeatherConfig] = None):
        self.config = config or QWeatherConfig.from_env()
        self.base_url = f"https://{self.config.api_host}/v7"
        self.headers = {
            "X-QW-Api-Key": self.config.api_key,
            "Accept-Encoding": "gzip"
        }
    
    def _resolve_location(self, location: str) -> str:
        """解析城市名称为 Location ID"""
        # 如果是纯数字，直接返回
        if location.isdigit():
            return location
        
        # 如果是经纬度格式，直接返回
        if "," in location and location.replace(",", "").replace(".", "").replace("-", "").isdigit():
            return location
        
        # 查找城市映射
        city_name = location.replace("市", "").strip()
        if city_name in CITY_ID_MAP:
            return CITY_ID_MAP[city_name]
        
        # 尝试模糊匹配
        for name, loc_id in CITY_ID_MAP.items():
            if city_name in name or name in city_name:
                return loc_id
        
        # 无法解析，返回原值（可能失败）
        return location
    
    def _request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送 API 请求"""
        url = f"{self.base_url}/{endpoint}"
        
        # 解析城市名称
        if "location" in params:
            params["location"] = self._resolve_location(params["location"])
        
        with httpx.Client(timeout=self.config.timeout) as client:
            response = client.get(url, params=params, headers=self.headers)
            
            if response.status_code != 200:
                return {"code": str(response.status_code), "error": response.text}
            
            return response.json()
    
    def get_weather_now(self, location: str, lang: str = "zh") -> Dict[str, Any]:
        """获取实时天气"""
        params = {"location": location, "lang": lang}
        return self._request("weather/now", params)
    
    def get_weather_daily(self, location: str, days: str = "7d", lang: str = "zh") -> Dict[str, Any]:
        """获取每日天气预报 (3d/7d/10d/15d/30d)"""
        params = {"location": location, "lang": lang}
        return self._request(f"weather/{days}", params)
    
    def get_weather_hourly(self, location: str, hours: int = 24, lang: str = "zh") -> Dict[str, Any]:
        """获取逐小时天气预报 (24/72/168)"""
        endpoint = f"weather/{hours}h"
        params = {"location": location, "lang": lang}
        return self._request(endpoint, params)
    
    def get_air_quality(self, location: str, lang: str = "zh") -> Dict[str, Any]:
        """获取实时空气质量"""
        params = {"location": location, "lang": lang}
        return self._request("air/now", params)
    
    def get_weather_warning(self, location: str, lang: str = "zh") -> Dict[str, Any]:
        """获取天气预警"""
        params = {"location": location, "lang": lang}
        return self._request("warning/now", params)
    
    def get_minutely_rain(self, location: str, lang: str = "zh") -> Dict[str, Any]:
        """获取分钟级降水预报（需要经纬度）"""
        params = {"location": location, "lang": lang}
        return self._request("minutely/5m", params)
    
    def get_weather_indices(self, location: str, indices_type: str = "0", lang: str = "zh") -> Dict[str, Any]:
        """获取生活指数"""
        params = {"location": location, "type": indices_type, "lang": lang}
        return self._request("indices/1d", params)
    
    def city_lookup(self, location: str, lang: str = "zh") -> Dict[str, Any]:
        """城市搜索"""
        params = {"location": location, "lang": lang}
        return self._request("geo/lookup", params)


def format_weather_now(data: Dict[str, Any]) -> str:
    """格式化实时天气输出"""
    if data.get("code") != "200":
        return f"❌ 获取天气失败: {data.get('code', '未知错误')}"
    
    now = data.get("now", {})
    update_time = data.get("updateTime", "")
    
    lines = [
        f"📅 更新时间: {update_time}",
        f"🌡️ 温度: {now.get('temp')}°C（体感 {now.get('feelsLike')}°C）",
        f"🌤️ 天气: {now.get('text')}",
        f"💨 风向风力: {now.get('windDir')} {now.get('windScale')}级（{now.get('windSpeed')}km/h）",
        f"💧 湿度: {now.get('humidity')}%",
        f"🌧️ 降水量: {now.get('precip')}mm",
        f"🌡️ 气压: {now.get('pressure')}hPa",
        f"👁️ 能见度: {now.get('vis')}km"
    ]
    
    return "\n".join(lines)


def format_weather_daily(data: Dict[str, Any]) -> str:
    """格式化每日天气预报输出"""
    if data.get("code") != "200":
        return f"❌ 获取天气预报失败: {data.get('code', '未知错误')}"
    
    daily_list = data.get("daily", [])
    lines = ["📅 天气预报:\n"]
    
    for day in daily_list:
        date = day.get("fxDate", "")
        lines.append(f"📆 {date}")
        lines.append(f"   🌡️ {day.get('tempMin')}°C ~ {day.get('tempMax')}°C")
        lines.append(f"   ☀️ 白天: {day.get('textDay')} | 夜间: {day.get('textNight')}")
        lines.append(f"   💨 {day.get('windDirDay')} {day.get('windScaleDay')}级")
        lines.append(f"   💧 湿度: {day.get('humidity')}% | 降水: {day.get('precip')}mm")
        if day.get("sunrise"):
            lines.append(f"   🌅 日出: {day.get('sunrise')} | 日落: {day.get('sunset')}")
        lines.append("")
    
    return "\n".join(lines)


def format_air_quality(data: Dict[str, Any]) -> str:
    """格式化空气质量输出"""
    if data.get("code") != "200":
        return f"❌ 获取空气质量失败: {data.get('code', '未知错误')}"
    
    now = data.get("now", {})
    
    aqi = int(now.get("aqi", 0))
    if aqi <= 50:
        level = "优 🟢"
    elif aqi <= 100:
        level = "良 🟡"
    elif aqi <= 150:
        level = "轻度污染 🟠"
    elif aqi <= 200:
        level = "中度污染 🔴"
    else:
        level = "重度污染 🟣"
    
    lines = [
        f"🌬️ 空气质量: {level}",
        f"📊 AQI: {now.get('aqi')}",
        f"🔸 PM2.5: {now.get('pm2p5')} μg/m³",
        f"🔸 PM10: {now.get('pm10')} μg/m³",
        f"🔸 O₃: {now.get('o3')} μg/m³",
        f"🔸 NO₂: {now.get('no2')} μg/m³",
        f"📝 主要污染物: {now.get('primary', '无')}"
    ]
    
    return "\n".join(lines)


def format_warning(data: Dict[str, Any]) -> str:
    """格式化天气预警输出"""
    if data.get("code") != "200":
        return f"❌ 获取预警失败: {data.get('code', '未知错误')}"
    
    warnings = data.get("warning", [])
    
    if not warnings:
        return "✅ 当前无天气预警"
    
    lines = ["⚠️ 天气预警:\n"]
    
    for w in warnings:
        lines.append(f"🔴 {w.get('typeName')} - {w.get('status')}")
        lines.append(f"   📅 发布时间: {w.get('pubTime')}")
        lines.append(f"   📝 内容: {w.get('text')}")
        lines.append("")
    
    return "\n".join(lines)


def format_indices(data: Dict[str, Any]) -> str:
    """格式化生活指数输出"""
    if data.get("code") != "200":
        return f"❌ 获取生活指数失败: {data.get('code', '未知错误')}"
    
    indices = data.get("daily", [])
    
    lines = ["📊 生活指数:\n"]
    
    for idx in indices:
        lines.append(f"📌 {idx.get('name')}: {idx.get('category')}")
        lines.append(f"   {idx.get('text')}")
    
    return "\n".join(lines)


# 便捷函数
def get_weather(location: str) -> str:
    """获取实时天气"""
    client = QWeatherClient()
    data = client.get_weather_now(location)
    return format_weather_now(data)


def get_forecast(location: str, days: int = 7) -> str:
    """获取天气预报"""
    client = QWeatherClient()
    days_str = f"{days}d" if days in [3, 7, 10, 15, 30] else "7d"
    data = client.get_weather_daily(location, days_str)
    return format_weather_daily(data)


def get_aqi(location: str) -> str:
    """获取空气质量"""
    client = QWeatherClient()
    data = client.get_air_quality(location)
    return format_air_quality(data)


def get_warnings(location: str) -> str:
    """获取天气预警"""
    client = QWeatherClient()
    data = client.get_weather_warning(location)
    return format_warning(data)


def get_indices(location: str) -> str:
    """获取生活指数"""
    client = QWeatherClient()
    data = client.get_weather_indices(location)
    return format_indices(data)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("用法: python qweather.py <命令> <位置>")
        print("命令: now, forecast, aqi, warning, indices")
        print("示例: python qweather.py now 北京")
        print("      python qweather.py forecast 上海 7")
        sys.exit(1)
    
    cmd = sys.argv[1]
    location = sys.argv[2]
    
    try:
        if cmd == "now":
            print(get_weather(location))
        elif cmd == "forecast":
            days = int(sys.argv[3]) if len(sys.argv) > 3 else 7
            print(get_forecast(location, days))
        elif cmd == "aqi":
            print(get_aqi(location))
        elif cmd == "warning":
            print(get_warnings(location))
        elif cmd == "indices":
            print(get_indices(location))
        else:
            print(f"❌ 未知命令: {cmd}")
    except Exception as e:
        print(f"❌ 错误: {e}")