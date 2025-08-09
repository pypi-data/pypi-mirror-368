import time
from dataclasses import dataclass
from typing import Dict, List, AsyncGenerator, Union
from litellm import acompletion


@dataclass
class ChatResponse:
    content: str
    input_token_count: int
    output_token_count: int
    elapsed_time_ms: int = 0
    error: str = None
    model: str = None
    finish_reason: str = None

    @property
    def total_tokens(self) -> int:
        return self.input_token_count + self.output_token_count

    @property
    def success(self) -> bool:
        return self.error is None


class ChatStreamResponse:
    def __init__(self, content_generator: AsyncGenerator[str, None]):
        self.content_generator = content_generator
        self.input_token_count = 0
        self.output_token_count = 0
        self.full_content = ""
        self.model = None
        self.finish_reason = None

    async def __aiter__(self):
        async for chunk in self.content_generator:
            if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                self.full_content += content
                yield content

    async def collect(self) -> str:
        async for _ in self:
            pass
        return self.full_content


class LLM:

    @staticmethod
    def _extract_token_usage(response) -> tuple:
        """提取token使用情况"""
        if hasattr(response, 'usage') and response.usage:
            input_tokens = getattr(response.usage, 'prompt_tokens', 0)
            output_tokens = getattr(response.usage, 'completion_tokens', 0)
        else:
            input_tokens = output_tokens = 0
        return input_tokens, output_tokens

    @staticmethod
    async def ask(model: str, prompt: str, **kwargs) -> ChatResponse:
        """
        简单问答接口

        Args:
            model: 模型名称
            prompt: 用户输入
            **kwargs: 其他参数

        Returns:
            ChatResponse: 包含完整响应信息的对象
        """
        start_time = time.time()

        try:
            messages = [{"role": "user", "content": prompt}]

            response = await acompletion(
                model=model,
                messages=messages,
                **kwargs
            )

            elapsed_ms = int((time.time() - start_time) * 1000)
            input_tokens, output_tokens = LLM._extract_token_usage(response)

            return ChatResponse(
                content=response.choices[0].message.content,
                input_token_count=input_tokens,
                output_token_count=output_tokens,
                elapsed_time_ms=elapsed_ms,
                model=model,
                finish_reason=getattr(response.choices[0], 'finish_reason', None)
            )

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return ChatResponse(
                content="",
                input_token_count=0,
                output_token_count=0,
                elapsed_time_ms=elapsed_ms,
                error=str(e),
                model=model
            )

    @staticmethod
    async def chat(model: str, messages: Union[str, List[Dict]], **kwargs) -> ChatResponse:
        """
        多轮对话接口

        Args:
            model: 模型名称
            messages: 消息列表或单个字符串
            **kwargs: 其他参数

        Returns:
            ChatResponse: 包含完整响应信息的对象
        """
        start_time = time.time()

        try:
            if isinstance(messages, str):
                messages = [{"role": "user", "content": messages}]

            response = await acompletion(
                model=model,
                messages=messages,
                **kwargs
            )

            elapsed_ms = int((time.time() - start_time) * 1000)
            input_tokens, output_tokens = LLM._extract_token_usage(response)

            return ChatResponse(
                content=response.choices[0].message.content,
                input_token_count=input_tokens,
                output_token_count=output_tokens,
                elapsed_time_ms=elapsed_ms,
                model=model,
                finish_reason=getattr(response.choices[0], 'finish_reason', None)
            )

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return ChatResponse(
                content="",
                input_token_count=0,
                output_token_count=0,
                elapsed_time_ms=elapsed_ms,
                error=str(e),
                model=model
            )

    @staticmethod
    async def stream(model: str, messages: Union[str, List[Dict]], **kwargs) -> ChatStreamResponse:
        """
        流式响应接口

        Args:
            model: 模型名称
            messages: 消息列表或单个字符串
            **kwargs: 其他参数

        Returns:
            ChatStreamResponse: 流式响应对象
        """
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        async def content_generator():
            try:
                async for chunk in await acompletion(
                        model=model,
                        messages=messages,
                        stream=True,
                        **kwargs
                ):
                    yield chunk
            except Exception as e:
                print(f"Stream error: {e}")

        stream_response = ChatStreamResponse(content_generator())
        stream_response.model = model
        return stream_response

    # 便捷方法 - 直接返回字符串内容
    @staticmethod
    async def quick_ask(model: str, prompt: str, **kwargs) -> str:
        """快速问答，直接返回字符串内容"""
        response = await LLM.ask(model, prompt, **kwargs)
        return response.content if response.success else ""

    @staticmethod
    async def quick_chat(model: str, messages: Union[str, List[Dict]], **kwargs) -> str:
        """快速聊天，直接返回字符串内容"""
        response = await LLM.chat(model, messages, **kwargs)
        return response.content if response.success else ""

    @staticmethod
    async def quick_stream(model: str, messages: Union[str, List[Dict]], **kwargs) -> AsyncGenerator[str, None]:
        """快速流式响应，直接yield字符串内容"""
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        try:
            async for chunk in await acompletion(
                    model=model,
                    messages=messages,
                    stream=True,
                    **kwargs
            ):
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            print(f"Stream error: {e}")


# 工具函数 - 用于构建消息
class MessageBuilder:
    """消息构建器 - 纯函数式，无状态"""

    @staticmethod
    def create_message(role: str, content: str) -> Dict:
        """创建单条消息"""
        return {"role": role, "content": content}

    @staticmethod
    def user(content: str) -> Dict:
        """创建用户消息"""
        return MessageBuilder.create_message("user", content)

    @staticmethod
    def assistant(content: str) -> Dict:
        """创建助手消息"""
        return MessageBuilder.create_message("assistant", content)

    @staticmethod
    def system(content: str) -> Dict:
        """创建系统消息"""
        return MessageBuilder.create_message("system", content)

    @staticmethod
    def build_conversation(system_prompt: str = None, *exchanges) -> List[Dict]:
        """
        构建对话消息列表

        Args:
            system_prompt: 系统提示词
            *exchanges: (user_msg, assistant_msg) 元组序列

        Returns:
            List[Dict]: 消息列表
        """
        messages = []

        if system_prompt:
            messages.append(MessageBuilder.system(system_prompt))

        for exchange in exchanges:
            if len(exchange) >= 1:
                messages.append(MessageBuilder.user(exchange[0]))
            if len(exchange) >= 2:
                messages.append(MessageBuilder.assistant(exchange[1]))

        return messages

    @staticmethod
    def add_message(messages: List[Dict], role: str, content: str) -> List[Dict]:
        """向消息列表添加新消息（返回新列表，不修改原列表）"""
        return messages + [MessageBuilder.create_message(role, content)]


# 使用示例
async def example_usage():
    model = "litellm_proxy/g4o_m"

    import os
    os.environ["LITELLM_PROXY_API_KEY"] = "sk-"
    os.environ["LITELLM_PROXY_API_BASE"] = "https://"

    # 1. 简单问答
    response = await LLM.ask(model, "你好，请介绍一下自己", temperature=0.7)
    print(f"回答: {response.content}")
    print(f"用时: {response.elapsed_time_ms}ms")
    print(f"Token: {response.total_tokens}")

    # 2. 多轮对话
    messages = MessageBuilder.build_conversation(
        "你是一个helpful的助手",
        ("什么是Python?", "Python是一种编程语言..."),
        ("它有什么特点?", None)  # 最后一个对话还没有回复
    )

    chat_response = await LLM.chat(model, messages, temperature=0.5)
    print(f"对话回答: {chat_response.content}")

    # 3. 流式响应
    print("流式输出:")
    async for content in LLM.quick_stream(model, "请写一首关于春天的诗"):
        print(content, end="", flush=True)
    print()

    # 4. 便捷方法
    quick_answer = await LLM.quick_ask(model, "1+1等于几?")
    print(f"快速回答: {quick_answer}")

    # 5. 动态构建对话
    conversation = [MessageBuilder.system("你是翻译助手")]
    conversation = MessageBuilder.add_message(conversation, "user", "Hello World")

    result = await LLM.chat(model, conversation)
    print(f"翻译结果: {result.content}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
