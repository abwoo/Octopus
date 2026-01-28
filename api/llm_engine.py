import os
import json
import logging
import httpx
import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic
from typing import Dict, Any, List, Optional

log = logging.getLogger("octopus.llm")

SYSTEM_PROMPT = """
You are Octopus, an AI action engine for Windows. 
Your goal is to translate user natural language instructions into a sequence of technical actions.

Available Action Types:
1. mouse.move(x, y)
2. mouse.click(button='left')
3. mouse.double_click()
4. keyboard.type(text)
5. keyboard.press(key)
6. keyboard.hotkey(*keys)
7. file.write(path, content)
8. file.read(path)
9. system.sleep(seconds)
10. system.screen_size()

Rules:
- You MUST respond ONLY with a JSON object.
- The JSON must have an 'intent' (brief description) and 'actions' (list of action objects).
- Each action object must have 'type' (e.g., 'mouse.move') and 'params' (dictionary of arguments).

Example Response:
{
  "intent": "Create a new text file",
  "actions": [
    {"type": "file.write", "params": {"path": "workspace/hello.txt", "content": "Hello!"}}
  ]
}
"""

class LLMEngine:
    def __init__(self):
        self._provider = "mock"
        self._api_key = ""
        self._model_name = ""
        self._base_url = None
        self._client = None
        self._anthropic_client = None

    def configure(self, provider: str, api_key: str, model_name: str, base_url: Optional[str] = None):
        self._provider = provider
        self._api_key = api_key
        self._model_name = model_name
        self._base_url = base_url
        
        if provider == "gemini":
            genai.configure(api_key=api_key)
        elif provider == "anthropic":
            self._anthropic_client = Anthropic(api_key=api_key, base_url=base_url)
        elif provider == "deepseek":
            # DeepSeek uses OpenAI protocol but with a specific endpoint if not provided
            ds_url = base_url or "https://api.deepseek.com/v1"
            self._client = OpenAI(api_key=api_key, base_url=ds_url)
        elif provider in ["openai", "local", "custom"]:
            self._client = OpenAI(api_key=api_key or "no-key", base_url=base_url)

    async def generate_actions(self, prompt: str) -> Dict[str, Any]:
        if self._provider == "gemini":
            return await self._call_gemini(prompt)
        elif self._provider == "anthropic":
            return await self._call_anthropic(prompt)
        elif self._provider in ["openai", "local", "custom", "deepseek"]:
            return await self._call_openai(prompt)
        elif self._provider == "http":
            return await self._call_universal_http(prompt)
        else:
            return {"intent": "Mock execution", "actions": [{"type": "system.info", "params": {}}]}

    async def _call_gemini(self, prompt: str) -> Dict[str, Any]:
        try:
            model = genai.GenerativeModel(
                model_name=self._model_name or "gemini-1.5-flash",
                system_instruction=SYSTEM_PROMPT
            )
            response = model.generate_content(prompt)
            return self._parse_json(response.text)
        except Exception as e:
            return {"intent": "Error", "actions": [], "error": str(e)}

    async def _call_anthropic(self, prompt: str) -> Dict[str, Any]:
        try:
            message = self._anthropic_client.messages.create(
                model=self._model_name or "claude-3-5-sonnet-20240620",
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            return self._parse_json(message.content[0].text)
        except Exception as e:
            return {"intent": "Error", "actions": [], "error": str(e)}

    async def _call_openai(self, prompt: str) -> Dict[str, Any]:
        try:
            response = self._client.chat.completions.create(
                model=self._model_name or "gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"intent": "Error", "actions": [], "error": str(e)}

    async def _call_universal_http(self, prompt: str) -> Dict[str, Any]:
        """Universal HTTP mode for arbitrary non-standard APIs"""
        if not self._base_url:
            return {"intent": "Error", "actions": [], "error": "No Base URL provided for HTTP mode"}
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": self._model_name,
                    "prompt": f"{SYSTEM_PROMPT}\n\nUser: {prompt}",
                    "stream": False
                }
                headers = {"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}
                res = await client.post(self._base_url, json=payload, headers=headers)
                res.raise_for_status()
                return self._parse_json(res.text)
        except Exception as e:
            return {"intent": "Error", "actions": [], "error": str(e)}

    def _parse_json(self, text: str) -> Dict[str, Any]:
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end != 0:
                return json.loads(text[start:end])
            return json.loads(text)
        except:
            return {"intent": "Error", "actions": [], "error": "Failed to parse AI response as JSON"}
