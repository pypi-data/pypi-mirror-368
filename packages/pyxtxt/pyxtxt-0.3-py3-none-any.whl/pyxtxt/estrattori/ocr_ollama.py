# pyxtxt/extractors/image_ocr_ollama.py
from . import register_extractor
from io import BytesIO
import base64

try:
    import ollama
    from PIL import Image
except ImportError:
    ollama = None
    Image = None

# Global configuration for Ollama model
OLLAMA_MODEL = "gemma3:4b"  # Default multimodal model

def set_ollama_model(model_name: str):
    """
    Set the Ollama model to use for OCR.
    
    Recommended multimodal models:
    - gemma3:4b (default, balanced speed/quality)
    - gemma3:12b (higher quality, slower)
    - gemma3:27b (best quality, very slow)
    - llava:7b (alternative vision model)
    - llava:13b (higher quality LLAVA)
    """
    global OLLAMA_MODEL
    OLLAMA_MODEL = model_name
    print(f"✅ Ollama OCR model set to: {model_name}")

def get_ollama_model():
    """Get current Ollama model name"""
    return OLLAMA_MODEL

if ollama and Image:
    def xtxt_image_ocr_ollama(file_buffer, mode="ocr", model=None):
        """
        Extract text from images using Ollama with multimodal models.
        
        Args:
            file_buffer: Image file buffer
            mode: "ocr" (text only) or "describe" (text + description)  
            model: Override default model (optional)
        """
        try:
            # Use specified model or global default
            current_model = model or OLLAMA_MODEL
            
            # Convert buffer to PIL Image
            image = Image.open(BytesIO(file_buffer.read()))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert image to base64
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            # Different prompts based on mode
            if mode == "ocr":
                prompt = """Extract ALL visible text from this image exactly as it appears. 
Rules:
- Only return text that is actually written/printed in the image
- Preserve reading order (left to right, top to bottom)  
- Maintain line breaks and formatting
- Include numbers, symbols, special characters
- Do NOT add descriptions, interpretations, or context
- If no text is visible, return 'NO_TEXT_FOUND'

Extracted text:"""
            
            else:  # mode == "describe"
                prompt = """Analyze this image and provide:
1. All visible text exactly as written
2. Brief description of the image content and context

Format:
TEXT: [all visible text here, or NO_TEXT_FOUND if none]
DESCRIPTION: [brief image description and context]"""
            
            # Send request to Ollama
            response = ollama.generate(
                model=current_model,
                prompt=prompt,
                images=[img_base64],
                options={
                    'temperature': 0.1,  # Low temperature for accuracy
                    'top_p': 0.9,
                    'num_predict': 1500
                }
            )
            
            # Extract and clean response
            extracted_content = response.get('response', '').strip()
            
            # Handle no-text case for OCR mode
            if mode == "ocr" and ('NO_TEXT_FOUND' in extracted_content or len(extracted_content) < 3):
                return ""
            
            return extracted_content
            
        except Exception as e:
            print(f"⚠️ Error extracting from image with Ollama {current_model}: {e}")
            return ""
    
    # Wrapper functions for each mode
    def xtxt_image_ocr_only(file_buffer):
        """Traditional OCR: extract only visible text using Ollama"""
        return xtxt_image_ocr_ollama(file_buffer, mode="ocr")
    
    def xtxt_image_describe(file_buffer):
        """OCR + Description: text + image context using Ollama"""
        return xtxt_image_ocr_ollama(file_buffer, mode="describe")
    
    # Register OCR-only version as default
    # Note: Will override traditional EasyOCR if both modules are loaded
    image_formats = [
        "image/jpeg", "image/jpg", "image/png", 
        "image/bmp", "image/tiff", "image/webp"
    ]
    
    for format_type in image_formats:
        register_extractor(format_type, xtxt_image_ocr_only, name="OCR-Ollama")