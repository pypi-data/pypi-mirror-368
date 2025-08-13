#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阿里云百炼-通义万相视频编辑统一模型MCP服务器

本MCP服务器实现了通义万相-通用视频编辑API的所有功能，包括：
- 多图参考视频生成
- 视频重绘
- 局部编辑
- 视频延展
- 视频画面扩展

官方文档：https://help.aliyun.com/zh/model-studio/wanx-vace-api-reference

Author: John Chen
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional

import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    TextContent,
    Tool,
)

# 阿里云百炼API配置
BASE_URL = "https://dashscope.aliyuncs.com"
VIDEO_SYNTHESIS_ENDPOINT = "/api/v1/services/aigc/video-generation/video-synthesis"
TASK_QUERY_ENDPOINT = "/api/v1/tasks"
MODEL_NAME = "wanx2.1-vace-plus"


class BailianVideoSynthesisServer:
    """
    阿里云百炼-通义万相视频编辑统一模型MCP服务器
    """

    def __init__(self, api_key: str):
        """
        初始化服务器

        Args:
            api_key: 阿里云百炼API密钥
        """
        self.api_key = api_key
        self.server = Server("bailian-video-synthesis")
        self.client = httpx.AsyncClient(timeout=60.0)

        # 注册工具
        self._register_tools()

    def _register_tools(self):
        """
        注册所有MCP工具
        """

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """
            列出所有可用的工具
            """
            return [
                Tool(
                    name="create_task_image_reference",
                    description="创建多图参考视频生成任务。基于参考图像和提示词生成视频，支持主体和背景分离控制。",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "视频生成的文本描述，详细描述期望的视频内容",
                            },
                            "ref_images_url": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "参考图像URL列表，最多支持2张图片",
                            },
                            "obj_or_bg": {
                                "type": "array",
                                "items": {"type": "string", "enum": ["obj", "bg"]},
                                "description": "指定每张参考图的用途：obj表示主体，bg表示背景",
                                "default": ["obj", "bg"],
                            },
                            "size": {
                                "type": "string",
                                "enum": ["1280*720", "720*1280", "1024*1024"],
                                "description": "输出视频尺寸",
                                "default": "1280*720",
                            },
                        },
                        "required": ["prompt", "ref_images_url"],
                    },
                ),
                Tool(
                    name="create_task_video_repainting",
                    description="创建视频重绘任务。基于输入视频和提示词，重新绘制视频内容，保持原有结构。",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "视频重绘的文本描述，描述期望的重绘效果",
                            },
                            "video_url": {
                                "type": "string",
                                "description": "输入视频的URL地址",
                            },
                            "control_condition": {
                                "type": "string",
                                "enum": ["depth", "canny", "pose"],
                                "description": "控制条件：depth(深度)、canny(边缘)、pose(姿态)",
                                "default": "depth",
                            },
                        },
                        "required": ["prompt", "video_url"],
                    },
                ),
                Tool(
                    name="create_task_video_edit",
                    description="创建视频局部编辑任务。基于掩码图像对视频的特定区域进行编辑。",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "编辑区域的文本描述，描述期望的编辑效果",
                            },
                            "video_url": {
                                "type": "string",
                                "description": "输入视频的URL地址",
                            },
                            "mask_url": {
                                "type": "string",
                                "description": "掩码图像URL，白色区域表示需要编辑的区域",
                            },
                        },
                        "required": ["prompt", "video_url", "mask_url"],
                    },
                ),
                Tool(
                    name="create_task_video_extension",
                    description="创建视频延展任务。基于输入的短视频片段，延长视频时长。",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "视频延展的文本描述，描述期望的延展内容",
                            },
                            "video_url": {
                                "type": "string",
                                "description": "输入视频的URL地址（通常为1秒的短片段）",
                            },
                            "target_duration": {
                                "type": "integer",
                                "description": "目标视频时长（秒），最大支持5秒",
                                "minimum": 2,
                                "maximum": 5,
                                "default": 5,
                            },
                        },
                        "required": ["prompt", "video_url"],
                    },
                ),
                Tool(
                    name="create_task_video_expansion",
                    description="创建视频画面扩展任务。扩展视频的画面范围，增加更多的视觉内容。",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "画面扩展的文本描述，描述期望扩展的内容",
                            },
                            "video_url": {
                                "type": "string",
                                "description": "输入视频的URL地址",
                            },
                            "expansion_ratio": {
                                "type": "number",
                                "description": "扩展比例，1.0表示不扩展，2.0表示扩展一倍",
                                "minimum": 1.0,
                                "maximum": 2.0,
                                "default": 1.5,
                            },
                        },
                        "required": ["prompt", "video_url"],
                    },
                ),
                Tool(
                    name="get_task_result",
                    description="查询任务执行结果。根据任务ID获取任务状态和结果。",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "任务ID，由创建任务接口返回",
                            }
                        },
                        "required": ["task_id"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """
            调用指定的工具
            """
            try:
                if name == "create_task_image_reference":
                    result = await self._create_task_image_reference(**arguments)
                elif name == "create_task_video_repainting":
                    result = await self._create_task_video_repainting(**arguments)
                elif name == "create_task_video_edit":
                    result = await self._create_task_video_edit(**arguments)
                elif name == "create_task_video_extension":
                    result = await self._create_task_video_extension(**arguments)
                elif name == "create_task_video_expansion":
                    result = await self._create_task_video_expansion(**arguments)
                elif name == "get_task_result":
                    result = await self._get_task_result(**arguments)
                else:
                    raise ValueError(f"未知的工具名称: {name}")

                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps(result, ensure_ascii=False, indent=2),
                        )
                    ]
                )
            except Exception as e:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"工具调用失败: {str(e)}")],
                    isError=True,
                )

    async def _create_task_image_reference(
        self,
        prompt: str,
        ref_images_url: List[str],
        obj_or_bg: Optional[List[str]] = None,
        size: str = "1280*720",
    ) -> Dict[str, Any]:
        """
        创建多图参考视频生成任务

        Args:
            prompt: 视频生成的文本描述
            ref_images_url: 参考图像URL列表
            obj_or_bg: 指定每张参考图的用途
            size: 输出视频尺寸

        Returns:
            任务创建结果，包含task_id
        """
        if obj_or_bg is None:
            obj_or_bg = ["obj", "bg"][: len(ref_images_url)]

        payload = {
            "model": MODEL_NAME,
            "input": {
                "function": "image_reference",
                "prompt": prompt,
                "ref_images_url": ref_images_url,
            },
            "parameters": {"obj_or_bg": obj_or_bg, "size": size},
        }

        return await self._make_request(VIDEO_SYNTHESIS_ENDPOINT, payload)

    async def _create_task_video_repainting(
        self, prompt: str, video_url: str, control_condition: str = "depth"
    ) -> Dict[str, Any]:
        """
        创建视频重绘任务

        Args:
            prompt: 视频重绘的文本描述
            video_url: 输入视频的URL地址
            control_condition: 控制条件

        Returns:
            任务创建结果，包含task_id
        """
        payload = {
            "model": MODEL_NAME,
            "input": {
                "function": "video_repainting",
                "prompt": prompt,
                "video_url": video_url,
            },
            "parameters": {"control_condition": control_condition},
        }

        return await self._make_request(VIDEO_SYNTHESIS_ENDPOINT, payload)

    async def _create_task_video_edit(
        self, prompt: str, video_url: str, mask_url: str
    ) -> Dict[str, Any]:
        """
        创建视频局部编辑任务

        Args:
            prompt: 编辑区域的文本描述
            video_url: 输入视频的URL地址
            mask_url: 掩码图像URL

        Returns:
            任务创建结果，包含task_id
        """
        payload = {
            "model": MODEL_NAME,
            "input": {
                "function": "video_edit",
                "prompt": prompt,
                "video_url": video_url,
                "mask_url": mask_url,
            },
        }

        return await self._make_request(VIDEO_SYNTHESIS_ENDPOINT, payload)

    async def _create_task_video_extension(
        self, prompt: str, video_url: str, target_duration: int = 5
    ) -> Dict[str, Any]:
        """
        创建视频延展任务

        Args:
            prompt: 视频延展的文本描述
            video_url: 输入视频的URL地址
            target_duration: 目标视频时长

        Returns:
            任务创建结果，包含task_id
        """
        payload = {
            "model": MODEL_NAME,
            "input": {
                "function": "video_extension",
                "prompt": prompt,
                "video_url": video_url,
            },
            "parameters": {"target_duration": target_duration},
        }

        return await self._make_request(VIDEO_SYNTHESIS_ENDPOINT, payload)

    async def _create_task_video_expansion(
        self, prompt: str, video_url: str, expansion_ratio: float = 1.5
    ) -> Dict[str, Any]:
        """
        创建视频画面扩展任务

        Args:
            prompt: 画面扩展的文本描述
            video_url: 输入视频的URL地址
            expansion_ratio: 扩展比例

        Returns:
            任务创建结果，包含task_id
        """
        payload = {
            "model": MODEL_NAME,
            "input": {
                "function": "video_expansion",
                "prompt": prompt,
                "video_url": video_url,
            },
            "parameters": {"expansion_ratio": expansion_ratio},
        }

        return await self._make_request(VIDEO_SYNTHESIS_ENDPOINT, payload)

    async def _get_task_result(self, task_id: str) -> Dict[str, Any]:
        """
        查询任务执行结果

        Args:
            task_id: 任务ID

        Returns:
            任务状态和结果
        """
        endpoint = f"{TASK_QUERY_ENDPOINT}/{task_id}"
        return await self._make_request(endpoint, method="GET")

    async def _make_request(
        self,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None,
        method: str = "POST",
    ) -> Dict[str, Any]:
        """
        发送HTTP请求到阿里云百炼API

        Args:
            endpoint: API端点
            payload: 请求载荷
            method: HTTP方法

        Returns:
            API响应结果
        """
        url = f"{BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",
        }

        try:
            if method == "POST":
                response = await self.client.post(url, json=payload, headers=headers)
            else:
                response = await self.client.get(url, headers=headers)

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_detail = e.response.json()
            except:
                error_detail = e.response.text

            raise Exception(
                f"API请求失败 (状态码: {e.response.status_code}): {error_detail}"
            )
        except Exception as e:
            raise Exception(f"请求发送失败: {str(e)}")

    async def run(self):
        """
        运行MCP服务器
        """
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="bailian-video-synthesis",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None, experimental_capabilities={}
                    ),
                ),
            )


async def async_main():
    """
    异步主函数，启动MCP服务器
    """
    # 从环境变量或命令行参数获取API密钥
    api_key = os.getenv("DASHSCOPE_API_KEY")

    if not api_key and len(sys.argv) > 1:
        # 检查是否是帮助参数
        if sys.argv[1] in ["--help", "-h"]:
            print("阿里云百炼-通义万相视频编辑统一模型MCP服务器")
            print("")
            print("使用方法:")
            print(
                "  方式1: export DASHSCOPE_API_KEY=your_api_key && mcp-server-bailian-video-synthesis"
            )
            print("  方式2: mcp-server-bailian-video-synthesis your_api_key")
            print("")
            print("支持的功能:")
            print("  - 多图参考视频生成")
            print("  - 视频重绘")
            print("  - 视频局部编辑")
            print("  - 视频延展")
            print("  - 视频画面扩展")
            print("")
            print(
                "官方文档: https://help.aliyun.com/zh/model-studio/wanx-vace-api-reference"
            )
            return
        else:
            api_key = sys.argv[1]

    if not api_key:
        print("错误: 请提供DASHSCOPE_API_KEY")
        print("使用方法:")
        print(
            "  方式1: export DASHSCOPE_API_KEY=your_api_key && mcp-server-bailian-video-synthesis"
        )
        print("  方式2: mcp-server-bailian-video-synthesis your_api_key")
        print("  方式3: mcp-server-bailian-video-synthesis --help (查看帮助)")
        sys.exit(1)

    # 创建并运行服务器
    server = BailianVideoSynthesisServer(api_key)
    await server.run()


def main():
    """
    同步主函数，用于console_scripts入口点
    """
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
