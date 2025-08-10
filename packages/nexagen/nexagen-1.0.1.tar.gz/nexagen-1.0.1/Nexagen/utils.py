import re
import subprocess
import asyncio
import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pathlib import Path
from typing import List, Dict, Any
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")


def call_llm(task_description: str) -> dict:
    """使用LLM"""
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL")

    prompt = task_description

    headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    payload = {
            "model": os.getenv("model_name"),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 8000
        }

    response = requests.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=300
            )
    #print(response.text)
    result = response.json()
    #print(result['choices'][0]['message']['content'])
    return result['choices'][0]['message']['content']
def generate_agent_card(
        name: str,
        description: str,
        tools: List[Dict],
        url: str,
        capabilities: List[Dict],
        default_input_modes: list,
        default_output_modes: list
) -> Dict:
    """生成Nexagen智能体卡片"""
    return {
            "name": name,
            "description": description,
            "url": url,
            "version": "1.0.0",
            "capabilities": capabilities,
            "defaultInputModes": default_input_modes,
            "defaultOutputModes": default_output_modes,
            "skills": tools

        }

