"""
Local AI Engine for White Beat
Uses Hugging Face Transformers for local inference
No OpenAI API required!
"""

import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import logging

logger = logging.getLogger(__name__)

class LocalAIEngine:
    """
    Local AI Engine using Hugging Face models
    Supports multiple models for different use cases
    """
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self.model_name = None
        self.initialized = False
        
    def initialize(self, model_name="microsoft/DialoGPT-medium"):
        """
        Initialize the AI model
        
        Available models:
        - microsoft/DialoGPT-medium (Conversational, 355M params)
        - microsoft/DialoGPT-large (Conversational, 762M params)
        - facebook/blenderbot-400M-distill (Conversational)
        - google/flan-t5-base (Instruction following)
        - distilgpt2 (Lightweight, 82M params)
        """
        try:
            logger.info(f"🔄 Initializing AI model: {model_name}")
            
            # Check if CUDA is available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"📱 Using device: {device}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Move model to device
            self.model.to(device)
            self.model.eval()  # Set to evaluation mode
            
            # Create pipeline for easier inference
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if device == "cuda" else -1
            )
            
            self.model_name = model_name
            self.initialized = True
            
            logger.info(f"✅ AI model initialized successfully: {model_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI model: {e}")
            self.initialized = False
            return False
    
    def generate_response(self, prompt, max_length=150, temperature=0.7):
        """
        Generate AI response for given prompt
        
        Args:
            prompt: User input text
            max_length: Maximum response length
            temperature: Creativity (0.0-1.0, higher = more creative)
        
        Returns:
            Generated response text
        """
        if not self.initialized:
            return "AI model not initialized. Please check server logs."
        
        try:
            # Generate response
            response = self.pipeline(
                prompt,
                max_length=max_length,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                top_k=50,
                num_return_sequences=1,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract generated text
            generated_text = response[0]['generated_text']
            
            # Remove the prompt from response (model includes it)
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            return f"Error generating response: {str(e)}"
    
    def chat(self, message, conversation_history=None):
        """
        Chat interface with conversation history support
        
        Args:
            message: Current user message
            conversation_history: List of previous messages
        
        Returns:
            AI response
        """
        if not self.initialized:
            return "AI model not initialized. Please check server logs."
        
        try:
            # Build conversation context
            if conversation_history:
                context = "\n".join([
                    f"User: {msg['user']}\nAI: {msg['ai']}" 
                    for msg in conversation_history[-3:]  # Last 3 exchanges
                ])
                prompt = f"{context}\nUser: {message}\nAI:"
            else:
                prompt = f"User: {message}\nAI:"
            
            # Generate response
            response = self.generate_response(
                prompt,
                max_length=200,
                temperature=0.8
            )
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error in chat: {e}")
            return f"Error: {str(e)}"


class BlenderBotEngine:
    """
    Alternative engine using Facebook's BlenderBot
    Better for conversational AI
    """
    
    def __init__(self):
        self.pipeline = None
        self.initialized = False
    
    def initialize(self):
        """Initialize BlenderBot model"""
        try:
            logger.info("🔄 Initializing BlenderBot...")
            
            self.pipeline = pipeline(
                "conversational",
                model="facebook/blenderbot-400M-distill"
            )
            
            self.initialized = True
            logger.info("✅ BlenderBot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize BlenderBot: {e}")
            return False
    
    def chat(self, message, conversation_history=None):
        """Chat with BlenderBot"""
        if not self.initialized:
            return "BlenderBot not initialized."
        
        try:
            from transformers import Conversation
            
            # Create conversation
            conversation = Conversation(message)
            
            # Add history if available
            if conversation_history:
                for msg in conversation_history[-3:]:
                    conversation.add_user_input(msg['user'])
                    conversation.mark_processed()
            
            # Generate response
            result = self.pipeline(conversation)
            
            return result.generated_responses[-1]
            
        except Exception as e:
            logger.error(f"❌ Error in BlenderBot chat: {e}")
            return f"Error: {str(e)}"


class FLANT5Engine:
    """
    Google's FLAN-T5 for instruction following
    Better for task-oriented conversations
    """
    
    def __init__(self):
        self.pipeline = None
        self.initialized = False
    
    def initialize(self):
        """Initialize FLAN-T5 model"""
        try:
            logger.info("🔄 Initializing FLAN-T5...")
            
            self.pipeline = pipeline(
                "text2text-generation",
                model="google/flan-t5-base"
            )
            
            self.initialized = True
            logger.info("✅ FLAN-T5 initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize FLAN-T5: {e}")
            return False
    
    def generate(self, prompt):
        """Generate response"""
        if not self.initialized:
            return "FLAN-T5 not initialized."
        
        try:
            result = self.pipeline(
                prompt,
                max_length=200,
                do_sample=True,
                temperature=0.7
            )
            
            return result[0]['generated_text']
            
        except Exception as e:
            logger.error(f"❌ Error in FLAN-T5: {e}")
            return f"Error: {str(e)}"


# Global AI engine instance
ai_engine = None
ai_engine_type = "dialogpt"  # Options: dialogpt, blenderbot, flan-t5

def get_ai_engine():
    """Get or create AI engine instance"""
    global ai_engine
    
    if ai_engine is None:
        if ai_engine_type == "blenderbot":
            ai_engine = BlenderBotEngine()
            ai_engine.initialize()
        elif ai_engine_type == "flan-t5":
            ai_engine = FLANT5Engine()
            ai_engine.initialize()
        else:  # Default to DialoGPT
            ai_engine = LocalAIEngine()
            ai_engine.initialize("microsoft/DialoGPT-medium")
    
    return ai_engine


def chat_with_ai(message, conversation_history=None):
    """
    Main chat function - use this in views
    
    Args:
        message: User message
        conversation_history: Previous conversation
    
    Returns:
        AI response
    """
    engine = get_ai_engine()
    
    if not engine or not engine.initialized:
        return "AI engine not available. Please check server configuration."
    
    return engine.chat(message, conversation_history)


# Quick test function
if __name__ == "__main__":
    print("🧪 Testing Local AI Engine...")
    
    # Test DialoGPT
    print("\n1️⃣ Testing DialoGPT:")
    engine = LocalAIEngine()
    if engine.initialize("microsoft/DialoGPT-medium"):
        response = engine.chat("Hello! How are you?")
        print(f"Response: {response}")
    
    # Test BlenderBot
    print("\n2️⃣ Testing BlenderBot:")
    blender = BlenderBotEngine()
    if blender.initialize():
        response = blender.chat("What's the weather like?")
        print(f"Response: {response}")
    
    # Test FLAN-T5
    print("\n3️⃣ Testing FLAN-T5:")
    flan = FLANT5Engine()
    if flan.initialize():
        response = flan.generate("Explain what AI is in simple terms")
        print(f"Response: {response}")
