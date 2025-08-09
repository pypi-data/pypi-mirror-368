# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/8/9 10:37
# Author     ：Maxwell
# Description：
"""
from typing import Union, List, Dict
from litellm import acompletion


class LLM:

    @staticmethod
    async def ask(model, prompt: str, **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        response = await acompletion(
            model=model,
            messages=messages,
            **kwargs
        )
        return response.choices[0].message.content

    @staticmethod
    async def chat(model, messages: Union[str, List[Dict]], **kwargs):
        """聊天接口，支持多轮对话"""
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        response = await acompletion(model=model, messages=messages, **kwargs)
        return response

    @staticmethod
    async def stream(model, messages: Union[str, List[Dict]], **kwargs):
        """流式响应"""
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        async for chunk in await acompletion(model=model,messages=messages,stream=True, **kwargs):
            yield chunk
