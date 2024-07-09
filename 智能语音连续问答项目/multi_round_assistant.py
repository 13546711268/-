from http import HTTPStatus  # 导入HTTPStatus类，用于处理HTTP状态码
import dashscope  # 导入dashscope库

# 设置DashScope API密钥
dashscope.api_key = 'YOUR_API_KEY'  # 设置API密钥

class MultiRoundAssistant:
    def __init__(self):
        self.messages = [{'role': 'system', 'content': 'You are a helpful assistant.'}]  # 初始消息列表

    def ask(self, user_input):
        self.messages.append({'role': 'user', 'content': user_input})  # 将用户输入添加到消息列表

        response = dashscope.Generation.call(model="qwen-turbo",
                                             messages=self.messages,
                                             result_format='message')  # 调用生成模型
        if response.status_code == HTTPStatus.OK:  # 如果响应成功
            assistant_reply = response.output.choices[0]['message']['content']
            self.messages.append({'role': response.output.choices[0]['message']['role'],
                                  'content': assistant_reply})  # 将助手的回复添加到消息列表中
            return assistant_reply  # 返回助手回复
        else:  # 如果响应失败
            print('请求ID: %s, 状态码: %s, 错误码: %s, 错误信息: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))  # 打印错误信息
            return "对不起，我无法回答你的问题。"  # 返回错误消息

    def get_messages(self):
        return self.messages  # 返回消息列表

# 示例代码
if __name__ == '__main__':
    print("输入你的问题，或输入 'exit', 'quit' 或 'q' 退出。")
    assistant = MultiRoundAssistant()  # 创建MultiRoundAssistant实例
    while True:
        user_input = input("你: ")  # 获取用户输入
        if user_input.lower() in ['exit', 'quit', 'q']:  # 用户输入 'exit', 'quit' 或 'q' 退出
            break
        reply = assistant.ask(user_input)  # 调用ask方法
        print("助手: " + reply)  # 打印助手回复
