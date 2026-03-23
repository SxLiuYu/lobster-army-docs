# 🦞 天猫精灵 Agent 集成研究

从网络搜索中获取的天猫精灵纳入 Agent 控制的技术方案。

---

## 📋 目录

1. [现有集成方案](#-现有集成方案)
2. [AliGenie 开放平台](#-aligenie-开放平台)
3. [HomeAssistant 集成](#-homeassistant-集成)
4. [MQTT 桥接方案](#-mqtt-桥接方案)
5. [Webhook 方案](#-webhook-方案)
6. [代码实现](#-代码实现)

---

## 🔍 现有集成方案

### GitHub 上找到的相关项目

| 项目 | Stars | 技术方案 |
|------|-------|----------|
| **feversky/aligenie** | 47 ⭐ | HomeAssistant 自定义组件 |
| **aligenieHomeAssistant** | 12 ⭐ | 天猫精灵 OAuth2 授权连接 HA |
| **sososoyoung/aligenie** | 1 ⭐ | 自定义组件 |

### 方案对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| **AliGenie SDK** | 官方支持，功能最全 | 需要申请开发者账号 |
| **HomeAssistant** | 成熟稳定，设备多 | 配置复杂 |
| **MQTT 桥接** | 实时性好，开源 | 需要中转服务 |
| **Webhook** | 简单直接 | 依赖公网地址 |

---

## 🛠️ AliGenie 开放平台

### 接入流程

```
1. 访问 https://open.aligen.net (需验证)
2. 注册开发者账号
3. 创建技能 → 自定义技能
4. 配置意图（Intent）和槽位（Slot）
5. 配置后端服务（HTTP/WebSocket）
6. 测试并发布
```

### 技能配置示例

```json
{
  "intentName": "controlDevice",
  "slots": [
    {
      "name": "device",
      "type": "DEVICE_TYPE_ENUM",
      "required": true
    },
    {
      "name": "action",
      "type": "ACTION_ENUM", 
      "required": true
    }
  ],
  "responses": [
    {
      "type": "TTS",
      "content": "好的，{{action}} {{device}}"
    }
  ]
}
```

### 回调接口

```python
from flask import Flask, request, jsonify
import aiohttp

app = Flask(__name__)

@app.route('/aligenie/callback', methods=['POST'])
def aligenie_callback():
    """AliGenie 技能回调接口"""
    
    data = request.json
    
    # 解析意图
    intent = data.get('intent', {})
    slots = intent.get('slots', {})
    
    # 提取设备类型和动作
    device = slots.get('device', {}).get('value')
    action = slots.get('action', {}).get('value')
    
    # 调用 HomeAssistant
    result = asyncio.run(control_device(device, action))
    
    # 返回响应
    return jsonify({
        "returnCode": "0",
        "returnMessage": "success",
        "result": {
            "type": "TTS",
            "text": f"好的，已{action}{device}"
        }
    })

async def control_device(device: str, action: str):
    """控制设备"""
    
    entity_id = f"switch.{device}" if device else "switch.default"
    service = "turn_on" if action == "打开" else "turn_off"
    
    async with aiohttp.ClientSession() as session:
        url = "http://homeassistant:8123/api/services/switch/" + service
        await session.post(
            url,
            json={"entity_id": entity_id},
            headers={"Authorization": "Bearer YOUR_TOKEN"}
        )
```

---

## 🏠 HomeAssistant 集成

### 方案一：OAuth2 授权（推荐）

项目：**292427558/aligenieHomeAssistant** (12 ⭐)

```javascript
// 核心逻辑
const AligenieHA = {
  // 1. OAuth2 授权
  async authorize() {
    const authUrl = 'https://open.aligen.net/oauth2/authorize' +
      '?client_id=YOUR_CLIENT_ID' +
      '&redirect_uri=YOUR_REDIRECT_URI' +
      '&response_type=code';
    
    return window.location.href = authUrl;
  },
  
  // 2. 获取 Access Token
  async getToken(code) {
    const response = await fetch('https://open.aligen.net/oauth2/token', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        grant_type: 'authorization_code',
        code: code,
        client_id: 'YOUR_CLIENT_ID',
        client_secret: 'YOUR_CLIENT_SECRET'
      })
    });
    
    return response.json();
  },
  
  // 3. 调用 HA API
  async callHA(token, entityId, service) {
    const response = await fetch(
      `https://YOUR_HA_URL/api/services/${entityId}/${service}`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      }
    );
    
    return response.json();
  }
};
```

### 方案二：自定义组件

项目：**feversky/aligenie** (47 ⭐)

```python
# custom_components/aligenie/__init__.py

import asyncio
import aiohttp
import async_timeout
from homeassistant.core import HomeAssistant

DOMAIN = "aligenie"

async def async_setup(hass: HomeAssistant, config: dict):
    """设置 AliGenie 集成"""
    
    # 配置
    aligenie_config = config.get(DOMAIN, {})
    client_id = aligenie_config.get('client_id')
    client_secret = aligenie_config.get('client_secret')
    
    # 注册服务
    hass.services.async_register(
        DOMAIN, 
        'call',
        lambda hass, service, data: aligenie_call(hass, data)
    )
    
    return True

async def aligenie_call(hass, data):
    """调用天猫精灵技能"""
    
    device = data.get('device')
    action = data.get('action')
    
    # 调用 AliGenie API
    url = "https://api.aligen.net/v1/device/control"
    
    async with aiohttp.ClientSession() as session:
        await session.post(
            url,
            json={
                "client_id": "YOUR_CLIENT_ID",
                "device_id": device,
                "action": action
            }
        )
```

---

## 📡 MQTT 桥接方案

### 架构

```
天猫精灵 → MQTT Broker → 龙虾军团 Agent → HomeAssistant
              ↓
        设备状态同步
```

### 天猫精灵 MQTT 集成

```python
# tmall_mqtt_bridge.py
import paho.mqtt.client as mqtt
import json
import requests

# 配置
Tmall_MQTT_BROKER = "localhost"
Tmall_MQTT_PORT = 1883
HA_URL = "http://localhost:8123"
HA_TOKEN = "YOUR_HA_TOKEN"

# 设备映射表
DEVICE_MAP = {
    "客厅灯": "light.living_room",
    "卧室灯": "light.bedroom", 
    "空调": "climate.ac",
    "插座": "switch.power_plug"
}

def on_connect(client, userdata, flags, rc):
    """连接回调"""
    print(f"Connected with result code {rc}")
    # 订阅天猫精灵设备主题
    client.subscribe("aligenie/device/#")

def on_message(client, userdata, msg):
    """消息回调"""
    try:
        topic = msg.topic
        payload = json.loads(msg.payload)
        
        # 解析设备控制命令
        if "control" in topic:
            device_name = payload.get("deviceName")
            action = payload.get("action")
            
            # 转换为 HA entity
            entity_id = DEVICE_MAP.get(device_name)
            if entity_id:
                # 调用 HA API
                call_ha(entity_id, action)
                
    except Exception as e:
        print(f"Error: {e}")

def call_ha(entity_id: str, action: str):
    """调用 HomeAssistant"""
    
    domain = entity_id.split('.')[0]
    service = "turn_on" if action in ["打开", "开启"] else "turn_off"
    
    url = f"{HA_URL}/api/services/{domain}/{service}"
    
    requests.post(
        url,
        json={"entity_id": entity_id},
        headers={"Authorization": f"Bearer {HA_TOKEN}"}
    )

# 启动 MQTT 客户端
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(Tmall_MQTT_BROKER, Tmall_MQTT_PORT, 60)
client.loop_forever()
```

---

## 🪝 Webhook 方案

### 简单直接的方式

```
天猫精灵技能 → Webhook → 龙虾军团 Agent
```

```python
# webhook_server.py
from flask import Flask, request, jsonify
from crewai import Agent

app = Flask(__name__)

# 定义智能家居 Agent
smart_home_agent = Agent(
    role="智能家居控制",
    goal="理解并执行用户的家居控制命令",
    backstory="你是智能家居助手，可以控制灯、空调、窗帘等设备"
)

@app.route('/webhook/tmall', methods=['POST'])
def tmall_webhook():
    """天猫精灵 Webhook"""
    
    data = request.json
    
    # 提取用户语音
    utterance = data.get('utterance', '')
    
    # 交给 Agent 处理
    result = smart_home_agent.chat(utterance)
    
    # 返回响应
    return jsonify({
        "returnCode": "0",
        "returnMessage": "success",
        "result": {
            "type": "TTS",
            "text": result
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### 天猫精灵配置

在阿里云智能服务平台配置：

```
Webhook 地址：https://your-domain.com/webhook/tmall
```

---

## 💻 完整代码示例

### 智能家居技能类

```python
# smart_home_skill.py
from crewai import Tool
import aiohttp

class TmallGenieSmartHome:
    """天猫精灵智能家居技能"""
    
    def __init__(self, ha_url: str, ha_token: str):
        self.ha_url = ha_url
        self.ha_token = ha_token
        self.name = "tmall_smart_home"
        self.description = "控制智能家居设备"
        
    async def control(self, device: str, action: str) -> str:
        """控制设备"""
        
        # 设备映射
        device_map = {
            "灯": {"domain": "light", "entity": "light.default"},
            "空调": {"domain": "climate", "entity": "climate.ac"},
            "窗帘": {"domain": "cover", "entity": "cover.curtain"},
            "插座": {"domain": "switch", "entity": "switch.plug"}
        }
        
        cfg = device_map.get(device)
        if not cfg:
            return f"不支持的设备：{device}"
        
        # 执行动作
        service = "turn_on" if action in ["打开", "开启", "开"] else "turn_off"
        
        url = f"{self.ha_url}/api/services/{cfg['domain']}/{service}"
        
        async with aiohttp.ClientSession() as session:
            await session.post(
                url,
                json={"entity_id": cfg["entity"]},
                headers={"Authorization": f"Bearer {self.ha_token}"}
            )
        
        return f"好的，已{action}{device}"
    
    async def query(self, device: str) -> str:
        """查询设备状态"""
        
        url = f"{self.ha_url}/api/states"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers={"Authorization": f"Bearer {self.ha_token}"}
            ) as response:
                states = await response.json()
        
        # 查找对应设备
        for state in states:
            if "light" in state.get("entity_id", ""):
                if device in ["灯", "灯光"]:
                    return f"灯的状态是：{state.get('state')}"
            if "climate" in state.get("entity_id", ""):
                if device in ["空调", "温度"]:
                    temp = state.get("attributes", {}).get("temperature")
                    return f"当前温度 {temp} 度"
        
        return "未找到该设备状态"

def get_tmall_smart_home_tool(ha_url: str, ha_token: str):
    """获取工具"""
    
    skill = TmallGenieSmartHome(ha_url, ha_token)
    
    return Tool(
        name="tmall_smart_home",
        description="控制天猫精灵连接的智能家居设备：灯、空调、窗帘、插座等",
        func=lambda params: skill.control(
            params.get("device"),
            params.get("action")
        )
    )
```

---

## 📋 部署步骤

### 1. HomeAssistant 部署

```bash
docker run -d \
  --name homeassistant \
  --network=host \
  -v ./config:/config \
  homeassistant/home-assistant:stable
```

### 2. 配置设备

在 HA 中添加天猫精灵支持的设备

### 3. 获取 Long-Lived Access Token

HA → 用户头像 → 创建令牌

### 4. 部署 Agent 服务

```bash
pip install crewai aiohttp flask
python webhook_server.py
```

### 5. 测试

```
对天猫精灵说："打开客厅灯"
→ 发送到 Webhook
→ Agent 处理
→ 调用 HA API
→ 灯打开
→ 返回响应
→ 天猫精灵："好的，灯已打开"
```

---

## 📎 参考资源

| 资源 | 链接 |
|------|------|
| aligenieHomeAssistant | https://github.com/292427558/aligenieHomeAssistant |
| feversky/aligenie | https://github.com/feversky/aligenie |
| HomeAssistant 文档 | https://www.home-assistant.io/docs/ |
| AliGenie 开发者平台 | https://open.aligen.net/ (需申请) |

---

## 🎯 推荐方案

对于你的情况（2 台天猫.runner ），推荐：

1. **首选**：AliGenie Webhook + Agent
   - 简单易实现
   - 不需要复杂配置

2. **进阶**：HomeAssistant + OAuth2
   - 功能最全
   - 可以控制更多设备

3. **长期**：MQTT 桥接
   - 实时性好
   - 可扩展性强

---

*Generated on 2026-03-23 | 天猫精灵 Agent 集成研究*
