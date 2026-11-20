# 和风天气技能

基于和风天气 API 的天气查询技能，支持实时天气、天气预报、空气质量、预警等功能。

## 功能

- 🌤️ 实时天气查询
- 📅 3-30天天气预报
- ⏰ 逐小时预报
- 🌬️ 空气质量（AQI）
- ⚠️ 天气预警
- 🌧️ 分钟级降水预报
- 📊 生活指数

## 安装

```bash
# 将技能目录复制到 active_skills/ 目录
cp -r qweather /path/to/copaw/active_skills/
```

## 配置

在 `.secrets/working.secret/keys.env` 中添加：

```bash
QWEATHER_API_KEY=your_api_key_here
QWEATHER_API_HOST=your_api_host_here  # 可选
```

### 获取 API Key

1. 访问 [和风天气开发平台](https://dev.qweather.com/)
2. 注册并创建应用
3. 获取 API Key

## 使用方法

### Python API

```python
from scripts.qweather import QWeatherClient, get_weather, get_forecast

# 方式1: 使用便捷函数
print(get_weather("北京"))
print(get_forecast("上海", days=7))

# 方式2: 使用客户端
client = QWeatherClient()
data = client.get_weather_now("116.41,39.92")
print(data)
```

### 命令行

```bash
# 实时天气
python scripts/qweather.py now 北京

# 天气预报
python scripts/qweather.py forecast 上海

# 空气质量
python scripts/qweather.py aqi 广州

# 天气预警
python scripts/qweather.py warning 深圳
```

## 文件结构

```
qweather/
├── SKILL.md              # 技能文档
├── README.md             # 说明文档
├── scripts/
│   └── qweather.py       # Python 实现
└── references/
    └── api-reference.md  # API 参考
```

## API 支持

| 功能 | API 端点 | 说明 |
|------|----------|------|
| 实时天气 | /weather/now | 温度、湿度、风力等 |
| 天气预报 | /weather/3d~30d | 3-30天预报 |
| 逐小时 | /weather/24h~168h | 24-168小时预报 |
| 空气质量 | /air/now | AQI、PM2.5等 |
| 天气预警 | /warning/now | 极端天气预警 |
| 分钟降水 | /minutely/5m | 仅中国地区 |
| 生活指数 | /indices/1d | 穿衣、运动等建议 |
| 城市搜索 | /geo/lookup | 获取城市ID |

## 依赖

- Python 3.8+
- httpx

## 许可证

MIT License

## 相关链接

- [和风天气官网](https://www.qweather.com/)
- [开发文档](https://dev.qweather.com/docs/)
- [控制台](https://console.qweather.com/)