from SpeechSynthesizerWrapper import SpeechSynthesizerWrapper  # 导入SpeechSynthesizerWrapper类
from multi_round_assistant import MultiRoundAssistant  # 导入MultiRoundAssistant类
from speech_recognizer import RealTimeSpeechRecognizer  # 导入定义的类




assistant = MultiRoundAssistant()  # 创建MultiRoundAssistant实例


print("输入你的问题，或输入 'exit', 'quit' 或 'q' 退出。")
while True:
    recognizer = RealTimeSpeechRecognizer()  # 创建识别实例
    recognizer.start_recognition()  # 开始识别

    user_input = recognizer.get_final_text()  # 获取最终识别文本
    if user_input.lower() in ['exit', 'quit', 'q']:  # 用户输入 'exit', 'quit' 或 'q' 退出
        break
    reply = assistant.ask(user_input)  # 调用ask方法
    print("助手: " + reply)  # 打印助手回复
    synthesizer = SpeechSynthesizerWrapper()  # 创建SpeechSynthesizerWrapper实例
    text = reply  # 测试文本
    synthesizer.synthesize(text)  # 调用合成方法
    synthesizer.stop()  # 停止播放


