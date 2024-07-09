
# 智能语音连续问答项目

- **本项目基于通义大模型API，分为三个模块：语音识别、大模型分析、语音合成。该项目粗略复刻了通义app的智能语音功能，三个模块均可独立对接其他任务，组成新的项目。**
- **语音模型可连续问答，能够记忆前文问题内容**

## 环境配置

请按照以下步骤配置环境：

```bash
conda create -n audio python=3.12.4
conda activate audio
pip install pyaudio dashscope sounddevice pynput numpy
```

## 设置API密钥

每个代码文件（除 `main.py` 外）开头都需要将密钥改为自己的。密钥为通义大模型API密钥，可在阿里云百炼平台申请。第一个月有免费额度，之后的价格也较为合理。

```python
# 设置DashScope API密钥
dashscope.api_key = 'YOUR_API_KEY'  # 替换为你的API密钥
```

## 声明

此代码继承自百炼大模型官网教程以及GitHub开源教程，并稍作改动和拼凑。如果有涉及侵权，请联系我进行修改。

**注意：** 此代码并不算美观，并且还有很多设想尚未完成，此次仅先保留项目在GitHub上。

