import os
import requests
import json
from dotenv import load_dotenv
import re
import time
from typing import Dict, Optional
import hashlib

load_dotenv()

class AIService:
    def __init__(self):
        self.api_key = os.getenv("SAMBANOVA_API_KEY")
        self.base_url = "https://api.sambanova.ai/v1"  # SambaNova API endpoint
        self.model = "Meta-Llama-3.1-8B-Instruct"  # Try the full model name
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        } if self.api_key else None
        
        # Rate limiting and caching
        self.last_request_time = 0
        self.min_request_interval = 5.0  # Increased to 5 seconds between requests due to strict rate limits
        self.response_cache: Dict[str, Dict] = {}
        self.cache_ttl = 600  # Cache responses for 10 minutes (longer cache)
    
    def _get_cache_key(self, messages: list, temperature: float) -> str:
        """Generate a cache key for the request"""
        content = json.dumps(messages, sort_keys=True) + str(temperature)
        return hashlib.md5(content.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid"""
        return time.time() - cache_entry["timestamp"] < self.cache_ttl
    
    async def _make_request(self, messages: list, temperature: float = 0.7) -> str:
        """Make a request to SambaNova API with rate limiting and caching"""
        if not self.api_key or not self.headers:
            print("SambaNova API key not configured")
            return "I'm sorry, AI features are currently unavailable. Please check your API configuration."
        
        # Check cache first
        cache_key = self._get_cache_key(messages, temperature)
        if cache_key in self.response_cache and self._is_cache_valid(self.response_cache[cache_key]):
            print("Returning cached response")
            return self.response_cache[cache_key]["response"]
        
        # Rate limiting - ensure minimum interval between requests
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            print(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 500,  # Reduced from 1000 to save on rate limits
                "stream": False
            }
            
            print(f"Making request to SambaNova API with model: {self.model}")
            
            self.last_request_time = time.time()
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                response_text = result["choices"][0]["message"]["content"].strip()
                
                # Cache the response
                self.response_cache[cache_key] = {
                    "response": response_text,
                    "timestamp": time.time()
                }
                
                print("Request successful, response cached")
                return response_text
            elif response.status_code == 429:
                print("Rate limit exceeded, using fallback response")
                return self._get_fallback_response(messages)
            elif response.status_code == 401:
                print("Authentication failed - check API key")
                return "I'm having authentication issues. Please check the API configuration."
            elif response.status_code == 404:
                print("Model not found - trying different model name")
                return "The AI model is currently unavailable. Please try again later."
            else:
                print(f"SambaNova API error: {response.status_code} - {response.text}")
                # Try to get more details about the error
                try:
                    error_data = response.json()
                    if "error" in error_data and "message" in error_data["error"]:
                        print(f"Error message: {error_data['error']['message']}")
                except:
                    pass
                return self._get_fallback_response(messages)
                
        except Exception as e:
            print(f"Error calling SambaNova API: {e}")
            return self._get_fallback_response(messages)
    
    def _get_fallback_response(self, messages: list) -> str:
        """Provide intelligent fallback responses when API is unavailable"""
        if not messages:
            return "Hello! I'm Cura AI, your healthcare assistant. I can help you find clinical trials, understand medical research, and answer health questions. What would you like to know?"
        
        last_message = messages[-1]["content"].lower()
        
        # Greeting responses
        if any(word in last_message for word in ["hello", "hi", "hey", "cura"]):
            return "Hello! I'm Cura AI, ready to help you with medical questions and clinical trial information. You can ask me about specific health conditions, treatment options, or browse our clinical trials and publications sections."
        
        # Cancer-related queries
        if any(word in last_message for word in ["cancer", "tumor", "oncology", "chemotherapy", "radiation"]):
            return "For cancer-related questions, I can help you find relevant clinical trials and research. Cancer treatment is rapidly evolving with new therapies like immunotherapy and targeted treatments. You can browse our Clinical Trials section for the latest studies, or ask me about specific cancer types for more targeted information."
        
        # Blood-related queries  
        if any(word in last_message for word in ["blood", "leukemia", "lymphoma", "anemia"]):
            return "Blood disorders and hematological conditions have many treatment options available. There are numerous clinical trials for blood cancers, clotting disorders, and other blood-related conditions. I can help you find relevant studies in our Clinical Trials section."
        
        # Heart/cardiovascular queries
        if any(word in last_message for word in ["heart", "cardiac", "cardiovascular", "blood pressure", "hypertension"]):
            return "Cardiovascular health is crucial, and there are many ongoing studies for heart conditions. From new medications to device trials, you can find relevant research in our Clinical Trials section. I can also help explain treatment options and research findings."
        
        # Diabetes queries
        if any(word in last_message for word in ["diabetes", "insulin", "glucose", "blood sugar"]):
            return "Diabetes management continues to improve with new treatments and technologies. There are clinical trials for Type 1, Type 2 diabetes, and related complications. Check our Clinical Trials section for studies on new medications, devices, and treatment approaches."
        
        # General treatment/medication queries
        if any(word in last_message for word in ["treatment", "medication", "therapy", "drug", "clinical trial"]):
            return "I can help you understand treatment options and find relevant clinical trials. Our platform has information on various therapies, from traditional treatments to cutting-edge experimental approaches. Browse the Clinical Trials and Publications sections for the latest research."
        
        # Precautions/safety queries
        if any(word in last_message for word in ["precaution", "safety", "side effect", "risk"]):
            return "Safety is always important when considering treatments. Clinical trials have strict safety protocols, and I can help you understand the risks and benefits of different approaches. Always consult with your healthcare provider about any treatment decisions."
        
        # Python/technical queries (redirect appropriately)
        if "python" in last_message:
            return "I'm focused on healthcare and medical research assistance. For programming questions, you might want to use a different AI assistant. However, I'm here to help with any health-related questions you might have!"
        
        # Default helpful response
        return "I'm here to help with your healthcare questions! You can ask me about medical conditions, treatment options, clinical trials, or research findings. I can also help you navigate our Clinical Trials and Publications sections to find relevant information for your specific needs."
    
    async def extract_medical_condition(self, text: str) -> dict:
        """Extract medical condition from natural language input"""
        if not self.api_key:
            # Fallback: simple keyword extraction
            return {"condition": text, "location": None}
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a medical text analyzer. Extract medical conditions and locations from text."
                },
                {
                    "role": "user", 
                    "content": f"""Extract the medical condition and location from the following text.
Text: "{text}"

Return in this format:
Condition: [medical condition]
Location: [location if mentioned, otherwise "Not specified"]"""
                }
            ]
            
            content = await self._make_request(messages)
            
            # Parse response
            condition_match = re.search(r'Condition:\s*(.+)', content)
            location_match = re.search(r'Location:\s*(.+)', content)
            
            condition = condition_match.group(1).strip() if condition_match else text
            location = location_match.group(1).strip() if location_match else "Not specified"
            
            if location == "Not specified":
                location = None
            
            return {"condition": condition, "location": location}
        except Exception as e:
            print(f"Error extracting medical condition: {e}")
            return {"condition": text, "location": None}
    
    async def summarize_publication(self, title: str, abstract: str) -> str:
        """Generate AI-powered summary for a publication with fallback"""
        if not abstract or len(abstract.strip()) < 50:
            return abstract or "No abstract available"
        
        # Try AI summarization first
        try:
            if self.api_key:
                messages = [
                    {
                        "role": "system",
                        "content": "You are a medical research summarizer. Create a concise, easy-to-understand summary of scientific abstracts in 2-3 sentences. Focus on key findings, methods, and implications. Use simple language accessible to patients and researchers."
                    },
                    {
                        "role": "user",
                        "content": f"Title: {title}\n\nAbstract: {abstract}\n\nPlease provide a clear, concise summary in 2-3 sentences:"
                    }
                ]
                
                ai_summary = await self._make_request(messages, temperature=0.3)
                if ai_summary and len(ai_summary) > 20:
                    return ai_summary
        except Exception as e:
            print(f"AI summarization failed, using fallback: {e}")
        
        # Fallback to simple text processing
        if len(abstract) <= 200:
            return abstract
        
        # Extract first 2 sentences as a simple summary
        sentences = abstract.split('. ')
        if len(sentences) >= 2:
            return '. '.join(sentences[:2]) + '.'
        
        return abstract[:200] + "..."
    
    async def summarize_clinical_trial(self, title: str, summary: str, detailed: str = "") -> str:
        """Generate AI-powered summary for a clinical trial with fallback"""
        content = detailed if detailed else summary
        
        if not content or len(content.strip()) < 50:
            return content or "No trial description available"
        
        # Try AI summarization first
        try:
            if self.api_key:
                messages = [
                    {
                        "role": "system",
                        "content": "You are a clinical trial summarizer. Create a concise, patient-friendly summary of clinical trials in 2-3 sentences. Explain the purpose, who can participate, and key details in simple terms. Focus on what patients need to know."
                    },
                    {
                        "role": "user",
                        "content": f"Trial Title: {title}\n\nDescription: {content}\n\nPlease provide a clear, concise summary for patients in 2-3 sentences:"
                    }
                ]
                
                ai_summary = await self._make_request(messages, temperature=0.3)
                if ai_summary and len(ai_summary) > 20:
                    return ai_summary
        except Exception as e:
            print(f"AI trial summarization failed, using fallback: {e}")
        
        # Fallback to simple text processing
        if len(content) <= 200:
            return content
        
        # Extract first 2 sentences as a simple summary
        sentences = content.split('. ')
        if len(sentences) >= 2:
            return '. '.join(sentences[:2]) + '.'
        
        return content[:200] + "..."
    
    async def chat_query(self, user_message: str, context: str = "") -> str:
        """Handle chat queries from Cura AI assistant"""
        if not self.api_key:
            return "I'm sorry, AI features are currently unavailable. Please check your API configuration."
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are Cura AI, a helpful medical research assistant for the CuraLink platform.
You help patients find clinical trials, publications, and connect with researchers.
Be empathetic, clear, and provide actionable guidance.
If you don't have specific information, guide users on how to search the platform.
Keep responses concise and helpful."""
                },
                {
                    "role": "user",
                    "content": f"Context: {context}\n\nUser: {user_message}"
                }
            ]
            
            response = await self._make_request(messages)
            return response
        except Exception as e:
            print(f"Error in chat query: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again."
    
    async def recommend_experts(self, condition: str, researchers: list) -> list:
        """Rank and recommend experts based on condition match with scores"""
        if not researchers:
            return []
        
        try:
            # Enhanced scoring with multiple factors
            condition_keywords = condition.lower().split()
            location_keywords = []  # Could be extracted from user profile
            
            scored_researchers = []
            
            for researcher in researchers:
                score = 0
                max_score = 100
                
                # Specialty matching (40% weight)
                specialty_text = researcher.get('specialty', '').lower()
                specialty_matches = sum(1 for keyword in condition_keywords if keyword in specialty_text)
                score += (specialty_matches / max(1, len(condition_keywords))) * 40
                
                # Research interests matching (35% weight)
                interests_text = researcher.get('research_interests', '').lower()
                interests_matches = sum(1 for keyword in condition_keywords if keyword in interests_text)
                score += (interests_matches / max(1, len(condition_keywords))) * 35
                
                # Institution prestige (10% weight) - simple heuristic
                institution = researcher.get('institution', '').lower()
                prestige_keywords = ['harvard', 'stanford', 'mit', 'johns hopkins', 'mayo clinic', 'cleveland clinic', 'mass general', 'nih']
                if any(keyword in institution for keyword in prestige_keywords):
                    score += 10
                
                # Verification bonus (10% weight)
                if researcher.get('verified', False):
                    score += 10
                
                # Availability bonus (5% weight)
                if researcher.get('available_for_meetings', True):
                    score += 5
                
                # Cap at 100%
                score = min(score, 100)
                
                scored_researchers.append({
                    **researcher,
                    'match_score': round(score),
                    'match_reason': self._generate_match_reason(score, researcher, condition)
                })
            
            # Sort by score descending
            scored_researchers.sort(key=lambda x: x['match_score'], reverse=True)
            return scored_researchers
            
        except Exception as e:
            print(f"Error recommending experts: {e}")
            # Return researchers with default scores if AI fails
            return [{
                **researcher,
                'match_score': 50,
                'match_reason': 'General match based on research area'
            } for researcher in researchers[:10]]
    
    def _generate_match_reason(self, score: float, researcher: dict, condition: str) -> str:
        """Generate human-readable match reason"""
        reasons = []
        
        if score >= 90:
            reasons.append("Excellent match")
        elif score >= 80:
            reasons.append("Strong match")
        elif score >= 70:
            reasons.append("Good match")
        elif score >= 60:
            reasons.append("Moderate match")
        else:
            reasons.append("Potential match")
        
        specialty = researcher.get('specialty', '')
        if specialty:
            reasons.append(f"specializes in {specialty}")
        
        institution = researcher.get('institution', '')
        if institution:
            reasons.append(f"at {institution}")
        
        condition_keywords = condition.lower().split()
        interests = researcher.get('research_interests', '').lower()
        matching_keywords = [kw for kw in condition_keywords if kw in interests]
        if matching_keywords:
            reasons.append(f"research includes {', '.join(matching_keywords[:2])}")
        
        return " - ".join(reasons)

# Global AI service instance
ai_service = AIService()
