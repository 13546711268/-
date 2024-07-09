import subprocess  # 导入subprocess模块，用于调用外部进程
import threading  # 导入threading模块，用于多线程处理
import pyaudio  # 导入pyaudio模块，用于音频播放
import dashscope  # 导入dashscope库，用于与DashScope服务进行交互
from dashscope.audio.tts_v2 import *  # 从dashscope.audio.tts_v2模块导入所有类

# 设置DashScope API密钥
dashscope.api_key = 'YOUR_API_KEY'  # 设置API密钥

# 定义实时MP3播放器类
class RealtimeMp3Player:
    def __init__(self):  # 初始化方法
        self.ffmpeg_process = None  # 初始化ffmpeg进程为None
        self._stream = None  # 初始化音频流为None
        self._player = None  # 初始化音频播放器为None
        self.play_thread = None  # 初始化播放线程为None
        self.stop_event = threading.Event()  # 初始化停止事件

    def start(self):  # 启动播放器方法
        self._player = pyaudio.PyAudio()  # 初始化pyaudio实例
        self._stream = self._player.open(
            format=pyaudio.paInt16, channels=1, rate=22050,
            output=True)  # 打开pyaudio音频流
        self.ffmpeg_process = subprocess.Popen(
            [
                'ffmpeg', '-i', 'pipe:0', '-f', 's16le', '-ar', '22050', '-ac',
                '1', 'pipe:1'
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )  # 初始化ffmpeg进程，解码MP3
        print('audio player is started')  # 打印播放器启动信息

    def stop(self):  # 停止播放器方法
        self.ffmpeg_process.stdin.close()  # 关闭ffmpeg标准输入
        self.ffmpeg_process.wait()  # 等待ffmpeg进程结束
        self.play_thread.join()  # 等待播放线程结束
        self._stream.stop_stream()  # 停止音频流
        self._stream.close()  # 关闭音频流
        self._player.terminate()  # 终止pyaudio实例
        if self.ffmpeg_process:
            self.ffmpeg_process.terminate()  # 终止ffmpeg进程
        print('audio player is stopped')  # 打印播放器停止信息

    def play_audio(self):  # 播放音频方法
        # 使用ffmpeg解码的PCM数据播放音频
        while not self.stop_event.is_set():  # 当停止事件未被设置时
            pcm_data = self.ffmpeg_process.stdout.read(1024)  # 从ffmpeg读取PCM数据
            if pcm_data:
                self._stream.write(pcm_data)  # 写入音频流
            else:
                break  # 如果没有数据，退出循环

    def write(self, data: bytes) -> None:  # 写入音频数据方法
        self.ffmpeg_process.stdin.write(data)  # 将数据写入ffmpeg标准输入
        if self.play_thread is None:  # 如果播放线程未启动
            print('start play thread')  # 打印启动播放线程信息
            self._stream.start_stream()  # 启动音频流
            self.play_thread = threading.Thread(target=self.play_audio)  # 创建播放线程
            self.play_thread.start()  # 启动播放线程

# 定义语音合成包装类
class SpeechSynthesizerWrapper:
    def __init__(self, model='cosyvoice-v1', voice='longxiaochun'):  # 初始化方法，设置模型和声音
        self.model = model  # 保存模型名称
        self.voice = voice  # 保存声音名称
        self.player = RealtimeMp3Player()  # 创建RealtimeMp3Player实例
        self.player.start()  # 启动播放器

    def synthesize(self, text):  # 合成方法
        # 定义一个回调来处理结果
        class Callback(ResultCallback):
            def on_open(self):
                print('websocket is open.')  # 打开WebSocket连接
                self.outer_instance.on_start()  # 播放开始

            def on_complete(self):
                print('speech synthesis task complete successfully.')  # 语音合成任务成功完成
                self.outer_instance.on_complete()  # 播放完成

            def on_error(self, message: str):
                print(f'speech synthesis task failed, {message}')  # 语音合成任务失败
                self.outer_instance.on_error(message)  # 播放错误

            def on_close(self):
                print('websocket is closed.')  # 关闭WebSocket连接

            def on_event(self, message):
                print(f'recv speech synthesis message {message}')  # 接收语音合成消息

            def on_data(self, data: bytes) -> None:
                # 将音频保存到文件
                self.player.write(data)  # 播放音频数据

        # 调用语音合成回调
        synthesizer_callback = Callback()  # 创建Callback实例
        synthesizer_callback.outer_instance = self  # 将自身传递给回调实例
        synthesizer_callback.player = self.player  # 将player传递给回调实例

        synthesizer = SpeechSynthesizer(
            model=self.model,  # 使用cosyvoice-v1模型
            voice=self.voice,  # 使用longxiaochun声音
            callback=synthesizer_callback,  # 设置回调函数
        )
        synthesizer.streaming_call(text)  # 调用流式语音合成
        synthesizer.streaming_complete()  # 完成流式语音合成
        print('requestId: ', synthesizer.get_last_request_id())  # 打印最后一个请求ID

    def on_start(self):
        print("语音播放开始")  # 语音播放开始

    def on_complete(self):
        print("语音播放完成")  # 语音播放完成

    def on_error(self, message):
        print("语音播放错误: ", message)  # 语音播放错误

    def stop(self):  # 停止方法
        self.player.stop()  # 停止播放器

# 示例代码
if __name__ == '__main__':
    synthesizer = SpeechSynthesizerWrapper()  # 创建SpeechSynthesizerWrapper实例
    text = "你好，这是一个语音合成的测试。"  # 测试文本
    synthesizer.synthesize(text)  # 调用合成方法
    synthesizer.stop()  # 停止播放
