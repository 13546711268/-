import threading  # 导入threading模块
import dashscope  # 导入dashscope库，用于与DashScope服务进行交互
import sounddevice as sd  # 导入sounddevice库，用于录制音频
from dashscope.audio.asr import (Recognition, RecognitionCallback, RecognitionResult)
# 从dashscope.audio.asr模块导入Recognition, RecognitionCallback和RecognitionResult类
from pynput import keyboard  # 导入pynput库，用于监听键盘事件

# 设置DashScope API密钥
dashscope.api_key = 'YOUR_API_KEY'  # 设置API密钥

class RealTimeSpeechRecognizer:
    def __init__(self, sample_rate=16000, channels=1, dtype='int16', block_size=3200,
                 model='paraformer-realtime-v1'):
        self.sample_rate = sample_rate  # 采样率（Hz）
        self.channels = channels  # 单声道
        self.dtype = dtype  # 数据类型
        self.block_size = block_size  # 每个缓冲区的帧数
        self.model = model  # 使用的模型名称
        self.stream = None  # 初始化音频流为None
        self.recognition = None  # 初始化识别服务为None
        self.stop_flag = threading.Event()  # 用于停止识别的标志
        self.final_text = ""  # 存储识别到的最终文本

        # 定义内部回调类
        class MyRecognitionCallback(RecognitionCallback):
            def __init__(self, outer_instance):
                super().__init__()
                self.outer_instance = outer_instance  # 保存外部实例引用
                self.partial_sentence = ""  # 初始化部分句子

            def on_open(self) -> None:
                print('识别已打开')  # 识别打开
                self.outer_instance.start_stream()  # 启动音频流

            def on_complete(self) -> None:
                print('识别已完成')  # 识别完成
                self.outer_instance.stop_flag.set()  # 设置停止标志

            def on_error(self, result: RecognitionResult) -> None:
                print('识别错误，任务ID: ', result.request_id)  # 打印任务ID
                print('错误信息: ', result.message)  # 打印错误信息
                self.outer_instance.stop_flag.set()  # 设置停止标志

            def on_event(self, result: RecognitionResult) -> None:
                sentence = result.get_sentence()
                if 'text' in sentence:
                    self.partial_sentence = sentence['text']  # 更新部分句子
                    if RecognitionResult.is_sentence_end(sentence):
                        print('识别文本: ', self.partial_sentence)  # 打印完整句子
                        self.outer_instance.final_text += self.partial_sentence + " "  # 更新最终识别文本
                        self.partial_sentence = ""  # 清空部分句子
                        print(
                            '句子结束，任务ID:%s，使用情况:%s'
                            % (result.get_request_id(), result.get_usage(sentence)))  # 打印句子结束信息
                        self.outer_instance.stop_flag.set()  # 设置停止标志
                    else:
                        print('部分句子: ', self.partial_sentence)  # 打印部分句子

            def on_close(self) -> None:
                print('识别已关闭')  # 识别关闭

        self.callback = MyRecognitionCallback(self)  # 创建识别回调实例

    def start_stream(self):
        self.stream = sd.InputStream(samplerate=self.sample_rate,
                                     channels=self.channels,
                                     dtype=self.dtype,
                                     blocksize=self.block_size,
                                     callback=self.audio_callback)  # 初始化音频流
        self.stream.start()  # 启动音频流

    def stop_stream(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            print('音频流已停止')  # 打印音频流停止信息

    def audio_callback(self, indata, frames, time, status):
        """发送音频数据到识别服务"""
        if status:
            print(status)  # 打印状态信息
        buffer = indata.tobytes()  # 将录音数据转换为字节
        self.recognition.send_audio_frame(buffer)  # 发送音频帧到识别服务

    def start_recognition(self):
        self.recognition = Recognition(
            model=self.model,  # 指定使用的模型
            format='pcm',  # 指定音频格式
            sample_rate=self.sample_rate,  # 指定采样率
            callback=self.callback)  # 指定回调实例
        self.recognition.start()  # 开始识别
        print("按 'q' 键停止录音和识别。")  # 提示用户按'q'键停止录音和识别

        # 创建键盘监听器以停止录音和识别
        with keyboard.Listener(on_press=self.on_press) as listener:
            # 等待直到监听器检测到'q'键或stop_flag被设置
            while not self.stop_flag.is_set():
                listener.join(0.1)

        self.stop_stream()  # 停止录音
        self.recognition.stop()  # 停止识别
        print('录音和识别已停止。')  # 打印停止信息

    def on_press(self, key):
        try:
            print(f'{key.char} 键被按下.......\n')  # 打印按键信息
            if key.char == 'q':
                self.stop_flag.set()  # 设置停止标志
                return False  # 停止监听
        except AttributeError:
            pass

    def get_final_text(self):
        return self.final_text  # 返回识别到的最终文本


if __name__ == "__main__":
    recognizer = RealTimeSpeechRecognizer()
    recognizer.start_recognition()
