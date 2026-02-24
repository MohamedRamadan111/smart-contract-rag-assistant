import requests
import json
from app.config import OPENROUTER_API_KEY, OPENROUTER_MODEL

class OpenRouterClient:
    def generate_stream(self, messages):
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "HTTP-Referer": "http://localhost",
                    "Content-Type": "application/json",
                },
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": messages,
                    "temperature": 0.1,
                    "stream": True 
                },
                stream=True
            )
            
            if response.status_code != 200:
                yield f" Provider Error {response.status_code}: {response.text}"
                return

            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8").removeprefix("data: ").strip()
                    if decoded_line and decoded_line != "[DONE]":
                        try:
                            chunk = json.loads(decoded_line)
                            
                            if "error" in chunk:
                                error_msg = chunk["error"].get("message", "Unknown error")
                                yield f"\n⚠️ **OpenRouter API Error:** {error_msg}"
                                return
                                
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                                    
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            
                            yield f"\n⚠️ **Parsing Error:** {str(e)}"
                            
        except Exception as e:
            yield f"⚠️ Connection Error: {str(e)}"