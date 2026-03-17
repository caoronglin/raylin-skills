# 和风天气 API 参考

## API 端点

### 基础地址
```
https://api.qweather.com/v7/
```

### 认证方式
```
Header: Authorization: Bearer {API_KEY}
```

## 天气 API

### 实时天气
```
GET /weather/now?location={location}
```

**参数：**
- `location` (必填): LocationID 或经纬度
- `lang`: 语言，默认 zh
- `unit`: 单位，m=公制，i=英制

**响应字段：**
| 字段 | 说明 |
|------|------|
| temp | 温度 |
| feelsLike | 体感温度 |
| text | 天气状况 |
| windDir | 风向 |
| windScale | 风力等级 |
| windSpeed | 风速 |
| humidity | 相对湿度 |
| precip | 降水量 |
| pressure | 气压 |
| vis | 能见度 |

### 每日预报
```
GET /weather/{days}?location={location}
```

**days 可选值：** 3d, 7d, 10d, 15d, 30d

**响应字段：**
| 字段 | 说明 |
|------|------|
| fxDate | 预报日期 |
| tempMax | 最高温度 |
| tempMin | 最低温度 |
| textDay | 白天天气 |
| textNight | 夜间天气 |
| sunrise | 日出时间 |
| sunset | 日落时间 |
| uvIndex | 紫外线指数 |

### 逐小时预报
```
GET /weather/{hours}h?location={location}
```

**hours 可选值：** 24, 72, 168

## 空气质量 API

### 实时空气质量
```
GET /air/now?location={location}
```

**响应字段：**
| 字段 | 说明 |
|------|------|
| aqi | 空气质量指数 |
| pm2p5 | PM2.5浓度 |
| pm10 | PM10浓度 |
| o3 | 臭氧浓度 |
| no2 | 二氧化氮浓度 |
| so2 | 二氧化硫浓度 |
| co | 一氧化碳浓度 |
| primary | 主要污染物 |

### AQI 等级
| AQI | 等级 |
|-----|------|
| 0-50 | 优 |
| 51-100 | 良 |
| 101-150 | 轻度污染 |
| 151-200 | 中度污染 |
| 201-300 | 重度污染 |
| >300 | 严重污染 |

## 预警 API

### 实时预警
```
GET /warning/now?location={location}
```

**响应字段：**
| 字段 | 说明 |
|------|------|
| id | 预警ID |
| sender | 发布单位 |
| pubTime | 发布时间 |
| title | 预警标题 |
| status | 预警状态 |
| level | 预警等级 |
| type | 预警类型 |
| typeName | 预警类型名称 |
| text | 预警详情 |

### 预警等级
| 等级 | 颜色 |
|------|------|
| 蓝色 | IV级（一般） |
| 黄色 | III级（较重） |
| 橙色 | II级（严重） |
| 红色 | I级（特别严重） |

## 分钟级降水 API

```
GET /minutely/5m?location={location}
```

**注意：** location 必须是经纬度坐标，仅支持中国地区。

## 生活指数 API

```
GET /indices/1d?location={location}&type={type}
```

**指数类型：**
| 类型 | 名称 |
|------|------|
| 1 | 运动指数 |
| 2 | 洗车指数 |
| 3 | 穿衣指数 |
| 4 | 钓鱼指数 |
| 5 | 紫外线指数 |
| 6 | 旅游指数 |
| 7 | 花粉过敏指数 |
| 8 | 舒适度指数 |
| 9 | 感冒指数 |
| 10 | 空气污染扩散条件指数 |
| 11 | 空调开启指数 |
| 12 | 太阳镜指数 |
| 13 | 化妆指数 |
| 14 | 晾晒指数 |
| 15 | 交通指数 |
| 16 | 防晒指数 |

## GeoAPI

### 城市搜索
```
GET /geo/lookup?location={location}
```

**响应字段：**
| 字段 | 说明 |
|------|------|
| id | Location ID |
| name | 城市名称 |
| adm1 | 一级行政区 |
| adm2 | 二级行政区 |
| country | 国家 |
| lat | 纬度 |
| lon | 经度 |

### 热门城市
```
GET /geo/top?lang={lang}
```

## 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求错误 |
| 401 | 认证失败 |
| 402 | 超过访问配额 |
| 403 | 无访问权限 |
| 404 | 数据不存在 |
| 429 | 过于频繁请求 |
| 500 | 服务器错误 |

## 请求限制

### 免费版
- 1000次/天
- Gzip压缩响应
- 支持实时天气、3天预报、空气质量

### 付费版
- 更高请求配额
- 30天预报
- 分钟级降水
- 历史天气

---
*参考: https://dev.qweather.com/docs/api/*