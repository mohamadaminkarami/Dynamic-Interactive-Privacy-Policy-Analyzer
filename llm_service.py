import json
import os
import time
import asyncio
from typing import Dict, List, Optional, Any, Union
import openai

from config import config
from models import (
    LLMRequest, LLMResponse, ContentChunk, ProcessedSection, 
    UserImpactAnalysis, ExtractedEntity, RiskLevel, DataType, 
    UserRight, LegalFramework
)

class LLMService:
    """Service for processing privacy policies using OpenAI LLMs"""
    
    def __init__(self):
        """Initialize the LLM service"""
        if not config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required")
        
        try:
            # Configure OpenAI client (old format)
            openai.api_key = config.OPENAI_API_KEY
            
            # Check if custom base URL is set (for LiteLLM proxy)
            base_url = os.getenv('OPENAI_BASE_URL')
            if base_url:
                openai.api_base = base_url
                print(f"🔗 Using custom OpenAI base URL: {base_url}")
            
        except Exception as e:
            raise ValueError(f"Failed to configure OpenAI client: {str(e)}")
        
        self.primary_model = config.OPENAI_MODEL_PRIMARY
        self.secondary_model = config.OPENAI_MODEL_SECONDARY
        
        # Rate limiting
        self.request_times: List[float] = []
        self.max_requests_per_minute = config.MAX_REQUESTS_PER_MINUTE
        
    async def _rate_limit_check(self) -> None:
        """Check and enforce rate limiting"""
        current_time = time.time()
        
        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if current_time - t < 60]
        
        # Wait if we've hit the rate limit
        if len(self.request_times) >= self.max_requests_per_minute:
            sleep_time = 60 - (current_time - self.request_times[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
                
        self.request_times.append(current_time)
    
    async def _call_llm(self, request: LLMRequest) -> LLMResponse:
        """Make a call to the LLM API"""
        await self._rate_limit_check()
        
        start_time = time.time()
        
        try:
            # Prepare the chat completion request
            messages = [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": request.prompt}
            ]
            
            # Prepare parameters for the old OpenAI client
            params = {
                "model": request.model,
                "messages": messages,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
            }
            
            # Add response format if specified (note: older client may not support this)
            if request.response_format == "json":
                # For older client, we'll add it to the prompt instead
                messages[-1]["content"] += "\n\nIMPORTANT: You must respond with valid JSON format only. No additional text or explanation."
            
            # Make the API call using the old client
            response = openai.ChatCompletion.create(**params)
            
            processing_time = time.time() - start_time
            
            return LLMResponse(
                content=response.choices[0].message.content,
                llm_model=request.model,
                tokens_used=response.usage.total_tokens,
                processing_time=processing_time
            )
            
        except Exception as e:
            raise Exception(f"LLM API call failed: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for privacy policy processing"""
        return """You are a privacy law expert and user advocate specialized in analyzing privacy policies. 
        Your role is to:
        1. Extract key information from privacy policies
        2. Assess user impact and risks
        3. Identify user rights and company obligations
        4. Provide clear, accurate analysis focused on user protection
        
        Always be precise, avoid assumptions, and flag any ambiguities.
        When providing JSON responses, ensure valid JSON format."""
    
    async def analyze_structure(self, content: str) -> Dict[str, Any]:
        """Analyze the structure of a privacy policy section"""
        prompt = f"""
        Analyze this privacy policy section and identify its structure:
        
        {content}
        
        Provide a JSON response with:
        {{
            "section_type": "definition/rights/obligations/data_collection/third_parties/other",
            "main_topics": ["list of main topics covered"],
            "subsections": ["list of subsections if any"],
            "legal_references": ["any legal framework references"],
            "complexity_level": "simple/moderate/complex"
        }}
        """
        
        request = LLMRequest(
            prompt=prompt,
            model=self.secondary_model,
            temperature=0.1,
            max_tokens=500,
            response_format="json"
        )
        
        response = await self._call_llm(request)
        try:
            content = response.content.strip()
            # Remove markdown code blocks if present
            if content.startswith('```json'):
                content = content[7:]  # Remove ```json
            if content.endswith('```'):
                content = content[:-3]  # Remove ```
            content = content.strip()
            
            return json.loads(content)
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return a default structure
            print(f"⚠️  JSON parsing failed: {e}")
            print(f"Raw response: {response.content}")
            return {
                "section_type": "other",
                "main_topics": ["analysis_failed"],
                "subsections": [],
                "legal_references": [],
                "complexity_level": "moderate"
            }
    
    async def extract_entities(self, content: str) -> List[ExtractedEntity]:
        """Extract entities from privacy policy content"""
        prompt = f"""
        Extract key entities from this privacy policy section:
        
        {content}
        
        Provide a JSON response with an array of entities:
        {{
            "entities": [
                {{
                    "entity_type": "data_type/user_right/company_obligation/third_party/legal_basis",
                    "value": "the extracted value",
                    "context": "surrounding context where found",
                    "confidence": 0.95
                }}
            ]
        }}
        """
        
        request = LLMRequest(
            prompt=prompt,
            model=self.secondary_model,
            temperature=0.1,
            max_tokens=800,
            response_format="json"
        )
        
        response = await self._call_llm(request)
        try:
            content = response.content.strip()
            # Remove markdown code blocks if present
            if content.startswith('```json'):
                content = content[7:]  # Remove ```json
            if content.endswith('```'):
                content = content[:-3]  # Remove ```
            content = content.strip()
            
            data = json.loads(content)
            
            entities = []
            for entity_data in data.get("entities", []):
                entities.append(ExtractedEntity(**entity_data))
            
            return entities
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"⚠️  Entity extraction failed: {e}")
            print(f"Raw response: {response.content}")
            return []  # Return empty list if parsing fails
    
    async def analyze_user_impact(self, content: str) -> UserImpactAnalysis:
        """Analyze the impact of a privacy policy section on users"""
        prompt = f"""
        Analyze how this privacy policy section affects users:
        
        {content}
        
        Provide a JSON response:
        {{
            "risk_level": "high/medium/low",
            "user_control": 3,
            "transparency_score": 4,
            "key_concerns": ["list of key concerns for users"],
            "actionable_rights": ["access", "deletion", "opt_out", etc.]
        }}
        
        Consider:
        - Real-world impact on users
        - Level of control users have
        - Clarity of information
        - Potential risks and benefits
        """
        
        request = LLMRequest(
            prompt=prompt,
            model=self.primary_model,
            temperature=0.1,
            max_tokens=600,
            response_format="json"
        )
        
        response = await self._call_llm(request)
        try:
            content = response.content.strip()
            # Remove markdown code blocks if present
            if content.startswith('```json'):
                content = content[7:]  # Remove ```json
            if content.endswith('```'):
                content = content[:-3]  # Remove ```
            content = content.strip()
            
            data = json.loads(content)
            
            # Map actionable rights to valid enum values
            if "actionable_rights" in data:
                mapped_rights = []
                right_mapping = {
                    "access": "access",
                    "deletion": "deletion", 
                    "delete": "deletion",
                    "portability": "portability",
                    "opt_out": "opt_out",
                    "opt-out": "opt_out",
                    "correction": "correction",
                    "modify": "correction",
                    "modification": "correction",
                    "consent_withdrawal": "consent_withdrawal",
                    "consent withdrawal": "consent_withdrawal",
                    "withdraw": "consent_withdrawal",
                }
                
                for right in data["actionable_rights"]:
                    right_key = right.lower().replace(" ", "_")
                    if right_key in right_mapping:
                        mapped_rights.append(right_mapping[right_key])
                    else:
                        # Try partial matching
                        for key, value in right_mapping.items():
                            if key in right_key or right_key in key:
                                mapped_rights.append(value)
                                break
                
                data["actionable_rights"] = list(set(mapped_rights))  # Remove duplicates
            
            return UserImpactAnalysis(**data)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"⚠️  User impact analysis failed: {e}")
            print(f"Raw response: {response.content}")
            # Return default analysis
            return UserImpactAnalysis(
                risk_level=RiskLevel.MEDIUM,
                user_control=3,
                transparency_score=3,
                key_concerns=["Analysis failed - please review manually"],
                actionable_rights=[]
            )
    
    async def generate_summary(self, content: str) -> str:
        """Generate a user-friendly summary of a privacy policy section"""
        prompt = f"""
        Create a clear, user-friendly summary of this privacy policy section:
        
        {content}
        
        The summary should:
        - Be written in plain language
        - Highlight key points that affect users
        - Be concise but comprehensive
        - Focus on what users need to know
        """
        
        request = LLMRequest(
            prompt=prompt,
            model=self.primary_model,
            temperature=0.2,
            max_tokens=400
        )
        
        response = await self._call_llm(request)
        return response.content.strip()
    
    async def calculate_importance_score(self, content: str, user_impact: UserImpactAnalysis) -> float:
        """Calculate importance score for ranking sections"""
        prompt = f"""
        Calculate an importance score (0.0 to 1.0) for this privacy policy section:
        
        Content: {content}
        User Impact: Risk Level: {user_impact.risk_level}, User Control: {user_impact.user_control}
        
        Consider:
        - User rights and freedoms impact
        - Data sensitivity
        - Legal obligations
        - Potential consequences
        - User decision-making needs
        
        Respond with just a number between 0.0 and 1.0.
        """
        
        request = LLMRequest(
            prompt=prompt,
            model=self.primary_model,
            temperature=0.1,
            max_tokens=50
        )
        
        response = await self._call_llm(request)
        try:
            score = float(response.content.strip())
            return max(0.0, min(1.0, score))  # Ensure it's between 0 and 1
        except ValueError:
            return 0.5  # Default score if parsing fails
    
    def _map_user_rights(self, rights_list: List[str]) -> List[UserRight]:
        """Map LLM output to valid UserRight enum values"""
        right_mapping = {
            "access": UserRight.ACCESS,
            "deletion": UserRight.DELETION,
            "delete": UserRight.DELETION,
            "portability": UserRight.PORTABILITY,
            "opt_out": UserRight.OPT_OUT,
            "opt-out": UserRight.OPT_OUT,
            "correction": UserRight.CORRECTION,
            "modify": UserRight.CORRECTION,
            "modification": UserRight.CORRECTION,
            "consent_withdrawal": UserRight.CONSENT_WITHDRAWAL,
            "consent withdrawal": UserRight.CONSENT_WITHDRAWAL,
            "withdraw": UserRight.CONSENT_WITHDRAWAL,
        }
        
        mapped_rights = []
        for right in rights_list:
            right_key = right.lower().replace(" ", "_")
            if right_key in right_mapping:
                mapped_rights.append(right_mapping[right_key])
            else:
                # Try partial matching for common variations
                for key, value in right_mapping.items():
                    if key in right_key or right_key in key:
                        mapped_rights.append(value)
                        break
        
        return list(set(mapped_rights))  # Remove duplicates

    async def process_section(self, chunk: ContentChunk) -> ProcessedSection:
        """Process a complete section of a privacy policy"""
        try:
            # Run analysis tasks in parallel for efficiency
            entities_task = self.extract_entities(chunk.content)
            impact_task = self.analyze_user_impact(chunk.content)
            summary_task = self.generate_summary(chunk.content)
            
            # Wait for all tasks to complete
            entities, user_impact, summary = await asyncio.gather(
                entities_task, impact_task, summary_task
            )
            
            # Calculate importance score
            importance_score = await self.calculate_importance_score(chunk.content, user_impact)
            
            # Extract data types and user rights from entities
            data_types = []
            user_rights = []
            
            for entity in entities:
                if entity.entity_type == "data_type":
                    try:
                        data_types.append(DataType(entity.value.lower()))
                    except ValueError:
                        pass  # Skip invalid data types
                elif entity.entity_type == "user_right":
                    try:
                        user_rights.append(UserRight(entity.value.lower().replace(" ", "_")))
                    except ValueError:
                        pass  # Skip invalid user rights
            
            # Map user rights from the impact analysis
            if user_impact.actionable_rights:
                mapped_rights = self._map_user_rights(user_impact.actionable_rights)
                user_rights.extend(mapped_rights)
                user_rights = list(set(user_rights))  # Remove duplicates
            
            return ProcessedSection(
                id=chunk.id,
                title=chunk.section_title or f"Section {chunk.position}",
                content=chunk.content,
                summary=summary,
                data_types=data_types,
                user_rights=user_rights,
                entities=entities,
                user_impact=user_impact,
                legal_frameworks=[],  # TODO: Implement legal framework detection
                importance_score=importance_score
            )
            
        except Exception as e:
            raise Exception(f"Failed to process section {chunk.id}: {str(e)}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the LLM service is working properly"""
        try:
            test_request = LLMRequest(
                prompt="Respond with 'OK' if you can process this message.",
                model=self.secondary_model,
                temperature=0.1,
                max_tokens=10
            )
            
            response = await self._call_llm(test_request)
            
            return {
                "status": "healthy",
                "model_primary": self.primary_model,
                "model_secondary": self.secondary_model,
                "test_response": response.content,
                "response_time": response.processing_time
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            } 