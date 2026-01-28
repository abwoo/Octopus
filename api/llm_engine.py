import os
import json
import logging
import google.generativeai as genai
from openai import OpenAI
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
- Be precise with coordinates and paths.

Example Response:
{
  "intent": "Create a new text file on desktop",
  "actions": [
    {"type": "file.write", "params": {"path": "C:/Users/User/Desktop/hello.txt", "content": "Hello from Octopus!"}}
  ]
}
"""

class LLMEngine:
    def __init__(self):
        self._provider = "mock"
        self._api_key = ""
        self._model_name = ""
        self._base_url = None

    def configure(self, provider: str, api_key: str, model_name: str, base_url: Optional[str] = None):
        self._provider = provider
        self._api_key = api_key
        self._model_name = model_name
        self._base_url = base_url
        
        if provider == "gemini":
            genai.configure(api_key=api_key)
        else:
            # All others (openai, local, custom) use the OpenAI client pattern
            self._client = OpenAI(
                api_key=api_key or "no-key-required",
                base_url=base_url
            )

    async def generate_actions(self, prompt: str) -> Dict[str, Any]:
        if self._provider == "gemini":
            return await self._call_gemini(prompt)
        elif self._provider in ["openai", "local", "custom"]:
            return await self._call_openai(prompt)
        else:
            return {"intent": "Mock execution", "actions": [{"type": "system.info", "params": {}}]}

    async def _call_gemini(self, prompt: str) -> Dict[str, Any]:
        try:
            model = genai.GenerativeModel(
                model_name=self._model_name or "gemini-1.5-flash",
                system_instruction=SYSTEM_PROMPT
            )
            response = model.generate_content(prompt)
            # Find and parse JSON in response
            text = response.text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end != 0:
                return json.loads(text[start:end])
            return {"intent": "Error", "actions": [], "error": "No JSON found in response"}
        except Exception as e:
            log.error(f"Gemini error: {e}")
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
            log.error(f"OpenAI error: {e}")
            return {"intent": "Error", "actions": [], "error": str(e)}
