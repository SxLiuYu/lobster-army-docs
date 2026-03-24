# 🦞 Windows 语音助手 - 本地部署方案

让老于在家里的电脑上跑一个可以用语音对话的 AI 助手。

---

## 📋 概述

### 功能
- 🎤 语音输入：读取麦克风
- 🗣️ 语音输出：通过扬声器播放
- 🧠 AI 对话：接入大模型

### 推荐技术栈

| 功能 | 推荐方案 | 价格 |
|------|----------|------|
| **语音识别** | Edge TTS (TTS only) / Whisper (本地) | 免费 |
| **语音合成** | Edge TTS / Azure TTS | 免费/便宜 |
| **大模型** | **DeepSeek** / 阿里千问 | DeepSeek 免费 |

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────┐
│                   Windows 电脑                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  麦克风 ──► 语音识别 ──► 大模型 ──► 语音合成 ──► 扬声器│
│              │              │              │        │
│          speech_recognition   DeepSeek      edge-tts
│              │              API              │        │
│              └──────────────┬───────────────┘        │
│                             ↓                        │
│                      对话管理                         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 💻 一键部署脚本 (Windows)

创建 `deploy-voice.ps1`：

```powershell
# deploy-voice.ps1 - 龙虾军团语音助手部署脚本

Write-Host "🦞 开始部署语音助手..." -ForegroundColor Green

# 检查 Python
Write-Host "`n📌 检查 Python..." -ForegroundColor Yellow
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "❌ Python 未安装" -ForegroundColor Red
    Write-Host "请先下载安装：https://www.python.org/downloads/" -ForegroundColor Cyan
    Write-Host "安装时务必勾选 Add Python to PATH" -ForegroundColor Cyan
    exit 1
}
$pythonVersion = python --version
Write-Host "✅ Python 已安装: $pythonVersion" -ForegroundColor Green

# 创建虚拟环境
Write-Host "`n📌 创建虚拟环境..." -ForegroundColor Yellow
python -m venv venv

# 激活并安装依赖
Write-Host "`n📌 安装依赖..." -ForegroundColor Yellow
.\venv\Scripts\pip install --upgrade pip

# 核心依赖
.\venv\Scripts\pip install speechrecognition edge-tts pyaudio openai requests pydotenv

Write-Host "`n📌 创建配置..." -ForegroundColor Yellow
Copy-Item -Path ".env.example" -Destination ".env" -Force
Write-Host "✅ 已创建 .env 文件" -ForegroundColor Green

# 测试麦克风
Write-Host "`n📌 正在测试音频设备..." -ForegroundColor Yellow
python -c "import pyaudio; p = pyaudio.PyAudio(); print(f'找到 {p.get_device_count()} 个音频设备')"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✅ 部署完成！" -ForegroundColor Green
Write-Host "`n📋 接下来的步骤：" -ForegroundColor Yellow
Write-Host "1. 编辑 .env 文件，填入 API Key" -ForegroundColor White
Write-Host "   - DeepSeek (推荐，免费): https://platform.deepseek.com" -ForegroundColor Cyan
Write-Host "   - 或阿里云千问: https://console.alibabacloud.com/" -ForegroundColor Cyan
Write-Host "2. 运行：.\venv\Scripts\python voice_assistant.py" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Green
```

---

## ⚙️ 环境配置

创建 `.env.example`：

```env
# DeepSeek API（推荐，免费额度够用）
# 注册地址：https://platform.deepseek.com
DEEPSEEK_API_KEY=sk-...

# 阿里云千问（备选）
# 阿里云百炼：https://bailian.aliyun.com/
DASHSCOPE_API_KEY=...

# 语音设置
LANGUAGE=zh-CN
VOICE_NAME=zh-CN-XiaoxiaoNeural  # 中文女声
VOICE_RATE=+0%      # 语速
VOICE_PITCH=+0Hz   # 音调

# 对话设置
WAKE_WORD=小虾     # 唤醒词
LISTEN_TIMEOUT=5   # 监听超时秒数
```

---

## 🎤 主程序

创建 `voice_assistant.py`：

```python
"""
🦞 龙虾军团语音助手
支持语音对话的 AI 助手
"""
import os
import json
import time
import asyncio
import threading
import speech_recognition as sr
import edge_tts
import pyaudio
import openai
from dotenv import load_dotenv

load_dotenv()

# ==================== 配置 ====================

# DeepSeek API
openai.api_key = os.getenv("DEEPSEEK_API_KEY", "")
openai.api_base = "https://api.deepseek.com/v1"

# 阿里云备选（如果没用 DeepSeek）
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")

# 语音设置
LANGUAGE = os.getenv("LANGUAGE", "zh-CN")
VOICE_NAME = os.getenv("VOICE_NAME", "zh-CN-XiaoxiaoNeural")
WAKE_WORD = os.getenv("WAKE_WORD", "小虾")
LISTEN_TIMEOUT = int(os.getenv("LISTEN_TIMEOUT", "5"))

# 对话历史
conversation_history = [
    {"role": "system", "content": "你叫小虾，是老于的AI助手。用中文对话，回复简洁友好。"}
]

# ==================== 语音识别 ====================

def listen_for_speech():
    """监听麦克风，返回识别到的文字"""
    
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("🎤 监听中...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        try:
            audio = recognizer.listen(source, timeout=LISTEN_TIMEOUT)
            print("🔄 识别中...")
            
            # 使用 Edge 的在线识别（免费）
            text = recognizer.recognize_google(audio, language=LANGUAGE)
            print(f"👤 你说: {text}")
            return text
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except Exception as e:
            print(f"❌ 识别错误: {e}")
            return None

# ==================== 语音合成 ====================

async def speak_async(text: str):
    """将文字转为语音并播放"""
    
    print(f"🗣️ 小虾说: {text}")
    
    # 生成语音文件
    communicate = edge_tts.Communicate(text, VOICE_NAME)
    audio_file = "temp_speech.mp3"
    await communicate.save(audio_file)
    
    # 播放（使用 Windows 自带播放器）
    os.system(f'start /B "" "{audio_file}"')
    
    # 等待播放完成
    time.sleep(0.5)

def speak(text: str):
    """同步播放语音"""
    asyncio.run(speak_async(text))

# ==================== AI 对话 ====================

def chat_with_ai(user_message: str) -> str:
    """调用 AI 获取回复"""
    
    # 添加用户消息
    conversation_history.append({"role": "user", "content": user_message})
    
    try:
        # 调用 DeepSeek API
        response = openai.ChatCompletion.create(
            model="deepseek-chat",
            messages=conversation_history,
            temperature=0.7,
        )
        
        assistant_message = response['choices'][0]['message']['content']
        
        # 添加助手回复
        conversation_history.append({"role": "assistant", "content": assistant_message})
        
        return assistant_message
        
    except Exception as e:
        print(f"❌ AI 调用失败: {e}")
        
        # 尝试备用方案
        return call_dashscope(user_message)

def call_dashscope(user_message: str) -> str:
    """调用阿里云千问（备用方案）"""
    
    if not DASHSCOPE_API_KEY:
        return "抱歉，API 配置有问题。"
    
    try:
        import requests
        
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
        headers = {
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "qwen-turbo",
            "input": {
                "messages": conversation_history
            },
            "parameters": {
                "result_format": "message"
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        return result['output']['choices']['message']['content']
        
    except Exception as e:
        return f"抱歉，服务暂时不可用: {e}"

# ==================== 主循环 ====================

def main():
    """主程序"""
    
    print("=" * 50)
    print("🦞 龙虾军团语音助手")
    print("=" * 50)
    print(f"唤醒词: {WAKE_WORD}")
    print(f"说 '{WAKE_WORD}' 开始对话")
    print("=" * 50)
    
    # 检查 API
    if not openai.api_key and not DASHSCOPE_API_KEY:
        print("❌ 请先配置 API Key！")
        print("编辑 .env 文件")
        return
    
    print()
    speak("你好，我是小虾。试着用唤醒词叫我吧。")
    
    while True:
        try:
            # 监听语音
            text = listen_for_speech()
            
            if text and WAKE_WORD in text:
                # 检测到唤醒词
                print("✨ 唤醒成功！")
                speak("我在")
                
                # 继续监听用户说话
                user_input = listen_for_speech()
                
                if user_input:
                    # 获取 AI 回复
                    reply = chat_with_ai(user_input)
                    
                    # 语音回复
                    speak(reply)
                else:
                    speak("我没听清，请再说一次。")
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
```

---

## 🔧 备选方案：使用更便宜的 API

### DeepSeek（推荐 - 免费额度）

1. 访问 https://platform.deepseek.com
2. 注册账号
3. 获取 API Key（免费）
4. 填入 `.env`

### 阿里云千问（备选）

1. 访问 https://bailian.aliyun.com/
2. 开通千问 API
3. 获取 API Key
4. 填入 `.env`

### 费用对比

| 服务 | 价格 | 免费额度 |
|------|------|----------|
| **DeepSeek** | 很便宜 | 100万 tokens |
| **阿里千问** | 便宜 | 100万 tokens |
| **OpenAI** | 较贵 | $5 |

---

## ⚠️ 常见问题

### 1. 麦克风无法识别

```powershell
# 检查设备
python -c "import pyaudio; p = pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)}') for i in range(p.get_device_count())]"
```

### 2. pyaudio 安装失败

```powershell
# 安装 Visual C++ Build Tools
# 然后使用
pip install pyaudio --only-binary :all:
```

### 3. 语音识别失败

- 检查网络
- 确认麦克风权限

### 4. API 调用失败

- 检查 API Key 是否正确
- 确认余额是否充足

---

## 🚀 进阶：离线语音识别

如果想完全离线，需要安装 Whisper：

```bash
pip install faster-whisper

# 修改代码使用本地模型
import faster_whisper

model = faster_whisper.load_model("base")
segments, info = model.transcribe("audio.wav")
```

---

## 📋 运行步骤

```powershell
# 1. 克隆项目
git clone https://github.com/SxLiuYu/lobster-army-docs.git lobster-voice
cd lobster-voice

# 2. 一键部署
.\deploy-voice.ps1

# 3. 配置 API
notepad .env

# 4. 运行
.\venv\Scripts\python voice_assistant.py
```

---

## 🎯 使用方法

1. 运行程序后，会听到"你好，我是小虾"
2. 对着麦克风说"小虾"（唤醒词）
3. 小虾回答"我在"
4. 说你的问题
5. 小虾会思考并回答
6. 回答通过扬声器播放

---

*Generated on 2026-03-23 | 语音助手方案*
