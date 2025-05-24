import requests

class ModelConnector:
    def __init__(self):
        self.available_models = []
        self.ollama_endpoint = "http://localhost:11434"
        
    def refresh_models(self):
        """Get list of all available models from Ollama"""
        try:
            # Try to get models from Ollama
            response = requests.get(f"{self.ollama_endpoint}/api/tags")
            if response.status_code == 200:
                ollama_models = response.json().get("models", [])
                
                # Get all models
                self.available_models = []
                for model in ollama_models:
                    model_name = model.get("name")
                    if model_name:
                        self.available_models.append(model_name)
                
                # If no models found, add default suggestions
                if not self.available_models:
                    self.available_models = ["llava:latest", "gemma3:27b"]
                    
                return self.available_models
            else:
                print(f"Error from Ollama API: {response.status_code}")
                return ["llava:latest", "gemma3:27b"]  # Default fallback
        except Exception as e:
            print(f"Error fetching Ollama models: {str(e)}")
            return ["llava:latest", "gemma3:27b"]  # Default fallback
    
    def get_models(self):
        """Return available models"""
        return self.available_models
    
    def enhance_prompt(self, model_name, prompt_text, prompt_type="general"):
        """Send prompt to selected model and get response
        
        Args:
            model_name (str): Name of the model to use
            prompt_text (str): The prompt text to enhance
            prompt_type (str, optional): Type of prompt ('image' or 'general'). Defaults to "general".
        """
        try:
            # Choose appropriate system prompt based on prompt type
            if prompt_type == "image":
                system_prompt = "You are a helpful assistant specializing in image analysis."
            else:
                system_prompt = "You are a helpful assistant. Your task is to respond to the user's prompt clearly and concisely."
            
            # Try the chat endpoint first
            try:
                response = requests.post(
                    f"{self.ollama_endpoint}/api/chat",
                    json={
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt_text}
                        ],
                        "stream": False
                    },
                    timeout=180  # Add timeout
                )
                
                if response.status_code == 200:
                    return response.json().get("message", {}).get("content", "No response from model")
            except Exception as e:
                print(f"Error with chat endpoint: {str(e)}")
                # Fall through to generate endpoint
            
            # Try the generate endpoint if chat didn't work
            try:
                full_prompt = f"{system_prompt}\n\n{prompt_text}"
                response = requests.post(
                    f"{self.ollama_endpoint}/api/generate",
                    json={
                        "model": model_name,
                        "prompt": full_prompt,
                        "stream": False
                    },
                    timeout=180  # Add timeout
                )
                
                if response.status_code == 200:
                    return response.json().get("response", "No response from model")
                else:
                    return f"Error: {response.status_code} - {response.text}"
            except Exception as e:
                return f"Error calling model with generate endpoint: {str(e)}"
                
        except Exception as e:
            return f"General error calling model: {str(e)}"
            
    def analyze_image(self, model_name, prompt, image_data):
        """Send an image to the model for analysis using Ollama
        
        Args:
            model_name: Name of the model to use (llava is recommended)
            prompt: The analysis prompt text
            image_data: Raw binary image data
            
        Returns:
            The model's analysis text response
        """
        try:
            # Convert image to base64 encoding
            import base64
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            
            # Try to determine mime type (for debugging only)
            import io
            from PIL import Image
            try:
                img = Image.open(io.BytesIO(image_data))
                format_lower = img.format.lower() if img.format else "jpeg"
                print(f"Image format detected: {format_lower}")
            except Exception as e:
                print(f"Warning: Could not determine image type: {e}")
            
            # Create the correct format for Ollama vision models
            system_prompt = "You are a helpful assistant specializing in image analysis."
            
            # Format payload according to Ollama's vision model API
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user", 
                        "content": prompt,
                        "images": [encoded_image]
                    }
                ],
                "stream": False
            }
            
            # Make the API call
            print(f"Sending image to model {model_name} for analysis...")
            response = requests.post(
                f"{self.ollama_endpoint}/api/chat",
                json=payload,
                timeout=180
            )
            
            if response.status_code == 200:
                print("Received successful response from Ollama")
                result = response.json()
                return result.get("message", {}).get("content", "")
            else:
                error_msg = f"Ollama Error ({response.status_code}): {response.text}"
                print(error_msg)
                
                # Try alternative format as fallback
                print("Trying alternative format as fallback...")
                alt_payload = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image", "image_url": f"data:image/jpeg;base64,{encoded_image}"}
                        ]}
                    ],
                    "stream": False
                }
                
                try:
                    response = requests.post(
                        f"{self.ollama_endpoint}/api/chat",
                        json=alt_payload,
                        timeout=180
                    )
                    
                    if response.status_code == 200:
                        print("Alternative format succeeded")
                        result = response.json()
                        return result.get("message", {}).get("content", "")
                    else:
                        return f"Image analysis failed with both formats. Error: {response.status_code} - {response.text}"
                except Exception as e:
                    print(f"Error with alternative format: {e}")
                    return self._mock_analyze_image(model_name, prompt, image_data)
                
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return self._mock_analyze_image(model_name, prompt, image_data)
    
    def _mock_analyze_image(self, model_name, prompt, image_data):
        """Mock implementation when Ollama is unavailable
        
        Args:
            model_name: Name of the model
            prompt: The analysis prompt
            image_data: Raw image data
            
        Returns:
            A mock analysis result
        """
        print(f"Using mock analyze_image with model: {model_name}")
        
        try:
            import io
            from PIL import Image
            
            # Try to extract basic image metadata for more realistic mock response
            img = Image.open(io.BytesIO(image_data))
            width, height = img.size
            format_name = img.format
            mode = img.mode
            
            # Mock analysis response
            return (f"Description: This is a {width}x{height} {format_name} image.\n\n"
                   "Objects: The image likely contains multiple visual elements. (Mock analysis)\n\n"
                   "People: There may be people in this image. (Mock analysis)\n\n"
                   "Scene/Setting: Unable to determine in mock analysis.\n\n"
                   "Activities: Unable to determine in mock analysis.\n\n"
                   "Text: No text detection performed. (Mock analysis)\n\n"
                   "Note: This is a placeholder analysis - Ollama couldn't process the image with the selected model. "
                   "This could be because the selected model doesn't support vision capabilities, "
                   "or because Ollama is not configured correctly. Try using a model like 'llava:latest'.")
            
        except Exception as e:
            print(f"Error in mock image analysis: {e}")
            return ("Description: Unable to analyze this image.\n\n"
                   "Note: This is a placeholder analysis - Ollama couldn't be reached or process the image. "
                   "Try using a model like 'llava:latest' which has vision capabilities.")
