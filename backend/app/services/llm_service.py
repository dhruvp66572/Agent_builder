import os
import google.generativeai as genai
import logging
import asyncio
from typing import Dict, Any, List
from serpapi import GoogleSearch  # <-- from google-search-results pkg

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        # --- Google Gemini setup ---
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        genai.configure(api_key=google_api_key)

        # --- SerpAPI key ---
        self.serpapi_key = os.getenv("SERPAPI_KEY")

        # --- Model config ---
        self.available_models = {
            "gemini-pro": "gemini-pro",
            "gemini-1.5-pro": "gemini-1.5-pro",
            "gemini-1.5-flash": "gemini-1.5-flash",
        }
        self.default_model = "gemini-1.5-flash"
    
    
    async def generate_response_gemini(
        self, 
        prompt: str, 
        context: str = "",
        model: str = "gemini-1.5-flash",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """Generate response using Google Gemini"""
        try:
            model_name = self.available_models.get(model, self.default_model)
            model_instance = genai.GenerativeModel(model_name)
            
            # Construct the full prompt
            full_prompt = self._construct_prompt(prompt, context)
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=min(max_tokens, 8192),  # Gemini's max tokens
                candidate_count=1,
                stop_sequences=None
            )
            
            # Generate response
            response = model_instance.generate_content(
                full_prompt,
                generation_config=generation_config,
                safety_settings=self._get_safety_settings()
            )
            
            # Handle potential content filtering
            if not response.text:
                if response.candidates and response.candidates[0].finish_reason:
                    reason = response.candidates[0].finish_reason
                    raise Exception(f"Content generation blocked: {reason}")
                else:
                    raise Exception("No content generated")
            
            return {
                "response": response.text,
                "model": model_name,
                "usage": {
                    "prompt_tokens": self._estimate_tokens(full_prompt),
                    "completion_tokens": self._estimate_tokens(response.text),
                    "total_tokens": self._estimate_tokens(full_prompt + response.text)
                },
                "finish_reason": response.candidates[0].finish_reason if response.candidates else "stop"
            }
            
        except Exception as e:
            logger.error(f"Error generating Gemini response: {str(e)}")
            raise Exception(f"Error generating Gemini response: {str(e)}")
    
    def _construct_prompt(self, prompt: str, context: str = "") -> str:
        if context:
            return (
                "You are a helpful AI assistant. Use the following context to answer.\n\n"
                f"Context:\n{context}\n\nQuestion: {prompt}\n"
            )
        return f"You are a helpful AI assistant.\n\nQuestion: {prompt}"
    
    def _get_safety_settings(self) -> List[Any]:
        """Get safety settings for content generation"""
        return [
            {
                "category": genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
            },
            {
                "category": genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
            },
            {
                "category": genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
            },
            {
                "category": genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                "threshold": genai.types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
            }
        ]
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        return len(text.split()) * 1.3  # Approximate tokens per word
    
    async def generate_response(
        self, 
        prompt: str, 
        context: str = "",
        model: str = "gemini-1.5-flash",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        custom_prompt: str = ""
    ) -> Dict[str, Any]:
        """Generate response using Gemini (primary method)"""
        # Apply custom prompt if provided
        if custom_prompt:
            prompt = f"{custom_prompt}\n\nUser Question: {prompt}"
        
        # Use Gemini as default, but support model specification
        if model in self.available_models or model.startswith("gemini"):
            return await self.generate_response_gemini(
                prompt, context, model, temperature, max_tokens
            )
        else:
            # Fallback to Gemini Pro for unsupported models
            logger.warning(f"Unsupported model '{model}', falling back to {self.default_model}")
            return await self.generate_response_gemini(
                prompt, context, self.default_model, temperature, max_tokens
            )
    
    async def search_web(self, query: str, num_results: int = 3) -> List[Dict[str, Any]]:
        """
        Perform a Google search using SerpAPI asynchronously.
        """
        if not self.serpapi_key:
            logger.warning("SerpAPI key not configured; web search unavailable")
            return []

        params = {
            "q": query,
            "api_key": self.serpapi_key,
            "num": num_results,
            "engine": "google",
            "hl": "en",
            "gl": "us",
        }

        def _sync_search():
            search = GoogleSearch(params)
            return search.get_dict()

        try:
            results = await asyncio.to_thread(_sync_search)
        except Exception as e:
            logger.error(f"Error searching web: {e}")
            return []

        web_results: List[Dict[str, Any]] = []
        for result in results.get("organic_results", [])[:num_results]:
            web_results.append(
                {
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "displayed_link": result.get("displayed_link", ""),
                }
            )
        return web_results
    
    async def generate_response_with_web_search(
        self,
        prompt: str,
        context: str = "",
        model: str = "gemini-1.5-flash",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        custom_prompt: str = "",
        num_web_results: int = 3,
    ) -> Dict[str, Any]:
        try:
            web_results = await self.search_web(prompt, num_web_results)

            web_context = ""
            if web_results:
                web_context = "Current web information:\n"
                for i, r in enumerate(web_results, 1):
                    web_context += (
                        f"\n{i}. {r['title']}\n"
                        f"   Source: {r.get('displayed_link', r.get('link', ''))}\n"
                        f"   Content: {r['snippet']}\n"
                    )

            full_context = "\n\n".join(
                filter(None, [f"Document context:\n{context}" if context else "", web_context])
            )

            result = await self.generate_response(
                prompt, full_context, model, temperature, max_tokens, custom_prompt
            )
            result["web_results"] = web_results
            result["web_search_performed"] = bool(web_results)
            result["num_web_results"] = len(web_results)
            return result

        except Exception as e:
            logger.error(f"Error in web search augmented generation: {e}")
            result = await self.generate_response(
                prompt, context, model, temperature, max_tokens, custom_prompt
            )
            result.update(
                {"web_search_performed": False, "web_search_error": str(e), "web_results": []}
            )
            return result
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available models"""
        return {
            "gemini-pro": {
                "name": "Gemini Pro",
                "provider": "google",
                "description": "Advanced reasoning and general-purpose tasks",
                "max_tokens": 8192,
                "supports_functions": False
            },
            "gemini-1.5-pro": {
                "name": "Gemini 1.5 Pro",
                "provider": "google", 
                "description": "Latest model with improved performance",
                "max_tokens": 8192,
                "supports_functions": True
            },
            "gemini-1.5-flash": {
                "name": "Gemini 1.5 Flash",
                "provider": "google",
                "description": "Fast responses for simple tasks",
                "max_tokens": 8192,
                "supports_functions": False
            }
        }
    
    async def validate_model_access(self, model: str = None) -> Dict[str, Any]:
        """Validate access to specified model or default model"""
        test_model = model or self.default_model
        
        try:
            model_instance = genai.GenerativeModel(test_model)
            
            # Test with a simple prompt
            response = model_instance.generate_content(
                "Say 'Hello' to test the connection.",
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=10
                )
            )
            
            return {
                "success": True,
                "model": test_model,
                "response": response.text if response.text else "Connection successful",
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "model": test_model,
                "response": None,
                "error": str(e)
            }