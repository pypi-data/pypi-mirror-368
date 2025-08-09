from typing import Dict, List, Optional
from ..models import ChatCompletion, Message, Choice, Usage

class PromptOptimizersChatCompletion:
    def __init__(self, client):
        self.client = client
    
    def create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
        **kwargs
    ) -> ChatCompletion:
        endpoint = "/chat/completions"
        
        data = {
            "model": model,
            "messages": messages,
            **kwargs
        }
        
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
        if temperature is not None:
            data["temperature"] = temperature
        if stream:
            data["stream"] = stream
        
        if stream:
            return self.client._stream_request(endpoint, data)
        else:
            response = self.client._make_request(endpoint, data)
            return self._parse_response(response)
    
    def _parse_response(self, response_data: Dict) -> ChatCompletion:
        """Parse API response into ChatCompletion object"""
        choices = []
        for choice_data in response_data.get("choices", []):
            message = Message(
                role=choice_data["message"]["role"],
                content=choice_data["message"]["content"]
            )
            choice = Choice(
                index=choice_data["index"],
                message=message,
                finish_reason=choice_data.get("finish_reason")
            )
            choices.append(choice)
        
        usage_data = response_data.get("usage", {})
        usage = Usage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0)
        )
        
        return ChatCompletion(
            id=response_data.get("id"),
            object=response_data.get("object"),
            created=response_data.get("created"),
            model=response_data.get("model"),
            choices=choices,
            usage=usage
        )

        
    # def optimize(self, prompt: str) -> Dict[str]:


    #     pass
    
    # def send_request_with_headers(self, prompt: str) -> Dict[str]:
        
    #     url = "https://api.dd.com"
    #     headers = {
    #         "Authorization": f"Bearer {self.api_key}",
    #         "Content-Type": "application/json"
    #     }
        
    #     data = {
    #         "prompt": prompt
    #     }
        
    #     try:
    #         response = requests.post(url, headers=headers, json=data)
            
    #         if response.status_code == 200:
    #             print("Success:", response.json())
    #         else:
    #             print(f"Error {response.status_code}:", response.text)
                
    #     except requests.exceptions.RequestException as e:
    #         print(f"Request failed: {e}")
    #         return False