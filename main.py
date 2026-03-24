"""
🦞 龙虾军团 - 本地运行版本
"""
import os
import asyncio
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from dotenv import load_dotenv
import json
import datetime

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局状态
nodes = {}  # 手机节点状态
agents = {}  # Agent 状态

# ==================== API 接口 ====================

@app.route('/api/health')
def health():
    return {"status": "ok", "nodes": len(nodes), "time": datetime.datetime.now().isoformat()}

@app.route('/api/nodes')
def get_nodes():
    return jsonify(nodes)

@app.route('/api/nodes/<node_id>')
def get_node(node_id):
    return jsonify(nodes.get(node_id, {}))

@app.route('/api/sensor', methods=['POST'])
def receive_sensor():
    """接收手机节点数据"""
    data = request.json
    node_id = data.get("node_id")
    nodes[node_id] = data
    print(f"📱 收到节点 {node_id} 数据")
    return {"success": True}

@app.route('/api/presence')
def presence():
    """检测是否在家"""
    wifi_networks = []
    for node_id, data in nodes.items():
        ssid = data.get("sensors", {}).get("wifi_ssid")
        if ssid:
            wifi_networks.append({"node": node_id, "ssid": ssid})
    
    # 检查是否有设备连接到家WiFi
    home_wifi = os.getenv("HOME_WIFI", "YourHomeWiFi")
    is_home = any(n.get("ssid") == home_wifi for n in wifi_networks)
    
    return jsonify({
        "is_home": is_home,
        "networks": wifi_networks
    })

# ==================== 主程序 ====================

def main():
    """启动本地服务"""
    port = int(os.getenv("PORT", 8000))
    
    print("=" * 50)
    print("🦞 龙虾军团本地节点启动")
    print("=" * 50)
    print(f"📡 服务地址: http://localhost:{port}")
    print(f"📱 API 文档: http://localhost:{port}/api")
    print(f"🔌 MQTT: localhost:1883")
    print("=" * 50)
    print()
    print("可用接口：")
    print("  GET  /api/health          - 健康检查")
    print("  GET  /api/nodes            - 所有节点状态")
    print("  GET  /api/nodes/<node_id>  - 指定节点状态")
    print("  GET  /api/presence        - 是否在家检测")
    print("  POST /api/sensor           - 接收传感器数据")
    print()
    
    socketio.run(app, host='0.0.0.0', port=port, debug=True)

if __name__ == "__main__":
    main()
