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
    UserRight, LegalFramework, TextSegment, StyledContent,
    InteractiveQuiz, QuizQuestion, QuizOption
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
        """Analyze the impact of a privacy policy section on users with numerical scoring"""
        prompt = f"""
        Analyze how this privacy policy section affects users with detailed numerical scoring:
        
        {content}
        
        Provide a JSON response:
        {{
            "risk_level": "high/medium/low",
            "sensitivity_score": 7.5,
            "privacy_impact_score": 8.0,
            "data_sharing_risk": 6.5,
            "user_control": 3,
            "transparency_score": 4,
            "key_concerns": ["list of key concerns for users"],
            "actionable_rights": ["access", "deletion", "opt_out", etc.],
            "engagement_level": "standard/interactive/quiz",
            "requires_quiz": true,
            "requires_visual_aid": false,
            "text_emphasis_level": 4,
            "highlight_color": "neutral/yellow/orange/red",
            "font_weight": "normal/medium/bold"
        }}
        
        Scoring Guidelines (0-10):
        - sensitivity_score: How sensitive/concerning is this content to users?
        - privacy_impact_score: How much does this impact user privacy?
        - data_sharing_risk: Risk of data being shared/misused
        
        UI Enhancement Rules:
        - engagement_level: "quiz" for scores 8+, "interactive" for 6-7, "standard" for <6
        - requires_quiz: true for sensitivity_score >= 8.0
        - requires_visual_aid: true for privacy_impact_score >= 8.0
        - text_emphasis_level: 1-5 based on importance (5 = highest emphasis)
        - highlight_color: "red" for 8+, "orange" for 6-7, "yellow" for 4-5, "neutral" for <4
        - font_weight: "bold" for 8+, "medium" for 6-7, "normal" for <6
        
        Consider:
        - Real-world impact on users
        - Level of control users have
        - Clarity of information
        - Potential risks and benefits
        - Need for user attention and engagement
        """
        
        request = LLMRequest(
            prompt=prompt,
            model=self.primary_model,
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
            
            # Ensure all required fields are present with defaults
            defaults = {
                "sensitivity_score": 5.0,
                "privacy_impact_score": 5.0,
                "data_sharing_risk": 5.0,
                "engagement_level": "standard",
                "requires_quiz": False,
                "requires_visual_aid": False,
                "text_emphasis_level": 2,
                "highlight_color": "neutral",
                "font_weight": "normal"
            }
            
            for key, default_value in defaults.items():
                if key not in data:
                    data[key] = default_value
            
            # Validate numeric ranges
            for score_field in ["sensitivity_score", "privacy_impact_score", "data_sharing_risk"]:
                if score_field in data:
                    data[score_field] = max(0.0, min(10.0, float(data[score_field])))
            
            if "text_emphasis_level" in data:
                data["text_emphasis_level"] = max(1, min(5, int(data["text_emphasis_level"])))
                
            return UserImpactAnalysis(**data)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"⚠️  User impact analysis failed: {e}")
            print(f"Raw response: {response.content}")
            # Return default analysis with new fields
            return UserImpactAnalysis(
                risk_level=RiskLevel.MEDIUM,
                sensitivity_score=5.0,
                privacy_impact_score=5.0,
                data_sharing_risk=5.0,
                user_control=3,
                transparency_score=3,
                key_concerns=["Analysis failed - please review manually"],
                actionable_rights=[],
                engagement_level="standard",
                requires_quiz=False,
                requires_visual_aid=False,
                text_emphasis_level=2,
                highlight_color="neutral",
                font_weight="normal"
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
            
            # Generate styled content based on sensitivity scores
            styled_content_task = self.analyze_text_segments(chunk.content, user_impact.sensitivity_score)
            styled_summary_task = self.analyze_text_segments(summary, user_impact.sensitivity_score)
            
            # Wait for styling tasks to complete
            styled_content, styled_summary = await asyncio.gather(
                styled_content_task, styled_summary_task
            )
            
            # Check if quiz should be generated
            requires_quiz = self.should_generate_quiz(user_impact)
            quiz = None
            
            if requires_quiz:
                quiz = await self.generate_quiz_for_section(
                    chunk.content, 
                    chunk.section_title or f"Section {chunk.position}", 
                    chunk.id, 
                    user_impact.sensitivity_score
                )
            
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
            
            # Calculate section statistics
            word_count = len(chunk.content.split())
            reading_time = max(1, word_count // 3)  # ~3 words per second for careful reading
            
            return ProcessedSection(
                id=chunk.id,
                title=chunk.section_title or f"Section {chunk.position}",
                original_content=chunk.content,
                summary=summary,
                styled_content=styled_content,
                styled_summary=styled_summary,
                user_impact=user_impact,
                component_type=self.determine_component_type(user_impact),
                section_priority=chunk.position + 1,  # Convert to 1-based indexing
                quiz=quiz,
                requires_quiz=requires_quiz,
                data_types=data_types,
                user_rights=user_rights,
                entities=entities,
                legal_frameworks=[],  # TODO: Implement legal framework detection
                importance_score=importance_score,
                word_count=word_count,
                reading_time=reading_time
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
    
    async def analyze_text_segments(self, content: str, overall_sensitivity: float) -> StyledContent:
        """Analyze text and create segments with sensitivity-based styling"""
        prompt = f"""
        Analyze this privacy policy text and break it into segments with sensitivity scoring for text visualization:
        
        {content}
        
        Overall Content Sensitivity: {overall_sensitivity}/10
        
        Create segments that should have different visual emphasis. Focus on:
        - Data collection statements
        - Data sharing/selling mentions
        - User rights and options
        - Third-party partnerships
        - Data retention policies
        - Contact information
        
        Provide a JSON response:
        {{
            "segments": [
                {{
                    "text": "specific text segment",
                    "sensitivity_score": 7.5,
                    "context_type": "data_collection/sharing/rights/retention/contact/general",
                    "key_terms": ["personal data", "third party"],
                    "highlight_color": "red/orange/yellow/blue/neutral",
                    "text_color": "default/red/orange/blue",
                    "font_weight": "normal/medium/bold",
                    "text_emphasis": 3,
                    "requires_attention": true
                }}
            ]
        }}
        
        Guidelines:
        - Break text into logical segments (sentences or phrases)
        - High sensitivity (8+): red highlights, bold text
        - Medium sensitivity (5-7): orange/yellow highlights, medium weight
        - Low sensitivity (<5): neutral/blue highlights, normal weight
        - Keep segments readable and not overwhelming
        - Focus on parts that users need to pay attention to
        """
        
        request = LLMRequest(
            prompt=prompt,
            model=self.primary_model,
            temperature=0.1,
            max_tokens=1500,
            response_format="json"
        )
        
        response = await self._call_llm(request)
        try:
            content_response = response.content.strip()
            # Remove markdown code blocks if present
            if content_response.startswith('```json'):
                content_response = content_response[7:]
            if content_response.endswith('```'):
                content_response = content_response[:-3]
            content_response = content_response.strip()
            
            data = json.loads(content_response)
            
            segments = []
            current_position = 0
            
            for i, segment_data in enumerate(data.get("segments", [])):
                # Find the segment text in the original content
                segment_text = segment_data.get("text", "")
                if not segment_text:
                    continue
                
                # Try to find the position in the original text
                position = content.find(segment_text, current_position)
                if position == -1:
                    # If exact match not found, approximate position
                    position = current_position
                
                # Apply styling rules based on sensitivity
                sensitivity = float(segment_data.get("sensitivity_score", 5.0))
                sensitivity = max(0.0, min(10.0, sensitivity))  # Clamp to 0-10
                
                # Auto-determine styling based on sensitivity
                if sensitivity >= 8.0:
                    highlight_color = "red"
                    text_color = "red"
                    font_weight = "bold"
                    text_emphasis = 5
                    requires_attention = True
                elif sensitivity >= 6.0:
                    highlight_color = "orange"
                    text_color = "orange"
                    font_weight = "medium"
                    text_emphasis = 4
                    requires_attention = True
                elif sensitivity >= 4.0:
                    highlight_color = "yellow"
                    text_color = "default"
                    font_weight = "medium"
                    text_emphasis = 3
                    requires_attention = False
                else:
                    highlight_color = "neutral"
                    text_color = "default"
                    font_weight = "normal"
                    text_emphasis = 1
                    requires_attention = False
                
                # Override with LLM suggestions if provided
                highlight_color = segment_data.get("highlight_color", highlight_color)
                text_color = segment_data.get("text_color", text_color)
                font_weight = segment_data.get("font_weight", font_weight)
                text_emphasis = segment_data.get("text_emphasis", text_emphasis)
                requires_attention = segment_data.get("requires_attention", requires_attention)
                
                segment = TextSegment(
                    id=f"segment_{i}",
                    text=segment_text,
                    sensitivity_score=sensitivity,
                    start_position=position,
                    end_position=position + len(segment_text),
                    highlight_color=highlight_color,
                    text_color=text_color,
                    font_weight=font_weight,
                    text_emphasis=text_emphasis,
                    requires_attention=requires_attention,
                    context_type=segment_data.get("context_type", "general"),
                    key_terms=segment_data.get("key_terms", [])
                )
                
                segments.append(segment)
                current_position = position + len(segment_text)
            
            # Calculate statistics
            high_sensitivity_count = sum(1 for s in segments if s.sensitivity_score >= 8.0)
            medium_sensitivity_count = sum(1 for s in segments if s.sensitivity_score >= 5.0 and s.sensitivity_score < 8.0)
            
            return StyledContent(
                original_text=content,
                segments=segments,
                overall_sensitivity=overall_sensitivity,
                styling_applied=True,
                high_sensitivity_count=high_sensitivity_count,
                medium_sensitivity_count=medium_sensitivity_count,
                total_segments=len(segments)
            )
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"⚠️  Text segmentation failed: {e}")
            print(f"Raw response: {response.content}")
            
            # Return basic segmentation as fallback
            return StyledContent(
                original_text=content,
                segments=[],
                overall_sensitivity=overall_sensitivity,
                styling_applied=False,
                high_sensitivity_count=0,
                medium_sensitivity_count=0,
                total_segments=0
            )

    async def generate_quiz_for_section(self, section_content: str, section_title: str, 
                                       section_id: str, sensitivity_score: float) -> Optional[InteractiveQuiz]:
        """Generate an interactive quiz for high-sensitivity content"""
        
        if sensitivity_score < 8.0:
            return None
        
        # Create quiz generation prompt
        prompt = f"""
        You are an expert privacy policy educator. Create an interactive quiz to help users understand the most concerning aspects of this privacy policy section.

        SECTION TITLE: {section_title}
        SECTION CONTENT: {section_content}
        SENSITIVITY SCORE: {sensitivity_score}/10

        Create a quiz with 2-4 questions that test understanding of:
        1. Key privacy risks and implications
        2. User rights and options
        3. Data handling practices
        4. Potential consequences for users

        REQUIREMENTS:
        - Focus on the most concerning privacy aspects
        - Include multiple choice questions with 3-4 options each
        - Provide detailed explanations for correct answers
        - Make questions educational, not just factual
        - Include real-world implications
        - Ensure questions help users make informed decisions

        QUESTION TYPES:
        - Multiple choice (primary)
        - True/false (for clear-cut facts)
        - Fill-in-the-blank (for key terms)

        DIFFICULTY LEVELS:
        - Easy: Basic understanding of key concepts
        - Medium: Implications and consequences
        - Hard: Nuanced understanding and decision-making

        Response format: JSON with quiz structure
        """
        
        try:
            # Use the existing LLM service infrastructure
            request = LLMRequest(
                prompt=prompt,
                model=self.primary_model,
                temperature=0.7,
                max_tokens=2000,
                response_format="json"
            )
            
            response = await self._call_llm(request)
            
            # Parse the JSON response
            content_response = response.content.strip()
            if content_response.startswith('```json'):
                content_response = content_response[7:]
            if content_response.endswith('```'):
                content_response = content_response[:-3]
            content_response = content_response.strip()
            
            quiz_data = json.loads(content_response)
            
            # Extract quiz data from nested structure
            if "quiz" in quiz_data:
                quiz_content = quiz_data["quiz"]
                # Check if quiz_content is a list of questions or a dictionary
                if isinstance(quiz_content, list):
                    # Direct list of questions
                    raw_questions = quiz_content
                    quiz_metadata = {}
                else:
                    # Dictionary with questions inside
                    raw_questions = quiz_content.get("questions", [])
                    quiz_metadata = quiz_content
            else:
                quiz_content = quiz_data
                raw_questions = quiz_content.get("questions", [])
                quiz_metadata = quiz_content
            
            # Convert to our model format
            quiz_id = f"quiz_{section_id}_{int(time.time())}"
            
            questions = []
            total_points = 0
            
            for i, q_data in enumerate(raw_questions):
                question_id = f"q_{quiz_id}_{i+1}"
                
                # Map LLM field names to our format first
                question_text = q_data.get("question", q_data.get("question_text", ""))
                question_type = q_data.get("type", q_data.get("question_type", "multiple_choice"))
                
                # Normalize question type
                if "multiple" in question_type.lower():
                    question_type = "multiple_choice"
                elif "true" in question_type.lower() or "false" in question_type.lower():
                    question_type = "true_false"
                elif "fill" in question_type.lower() or "blank" in question_type.lower():
                    question_type = "fill_blank"
                
                # Create options
                options = []
                raw_options = q_data.get("options", [])
                correct_answer = q_data.get("correct_answer", q_data.get("correctAnswer", ""))
                
                # Handle true/false questions specially
                if question_type == "true_false":
                    # Always create True/False options for true/false questions
                    is_true_correct = correct_answer.lower() in ["true", "t", "yes", "1"]
                    
                    options.append(QuizOption(
                        id=f"opt_{question_id}_true",
                        text="True",
                        is_correct=is_true_correct,
                        explanation=None
                    ))
                    
                    options.append(QuizOption(
                        id=f"opt_{question_id}_false", 
                        text="False",
                        is_correct=not is_true_correct,
                        explanation=None
                    ))
                elif question_type == "fill_blank":
                    # For fill-in-the-blank, create a single option with the correct answer
                    options.append(QuizOption(
                        id=f"opt_{question_id}_answer",
                        text=correct_answer,
                        is_correct=True,
                        explanation=None
                    ))
                else:
                    # Handle multiple choice questions
                    for j, option_text in enumerate(raw_options):
                        option_id = f"opt_{question_id}_{j+1}"
                        # For multiple choice, determine if this is correct based on the answer
                        is_correct = False
                        if correct_answer and isinstance(option_text, str):
                            # Check if this option matches the correct answer
                            if option_text.strip() == correct_answer.strip():
                                is_correct = True
                            elif correct_answer in option_text or option_text in correct_answer:
                                is_correct = True
                        
                        options.append(QuizOption(
                            id=option_id,
                            text=option_text,
                            is_correct=is_correct,
                            explanation=None  # Individual option explanations not provided by LLM
                        ))
                
                # Determine points based on difficulty
                difficulty = q_data.get("difficulty", "medium")
                points = {"easy": 1, "medium": 2, "hard": 3}.get(difficulty, 2)
                total_points += points
                
                question = QuizQuestion(
                    id=question_id,
                    question_text=question_text,
                    question_type=question_type,
                    options=options,
                    correct_explanation=q_data.get("explanation", ""),
                    difficulty=difficulty,
                    points=points,
                    related_content=section_content[:500],  # Truncate for storage
                    sensitivity_score=sensitivity_score,
                    learning_objective=q_data.get("learning_objective", "")
                )
                questions.append(question)
            
            # Create quiz
            quiz = InteractiveQuiz(
                id=quiz_id,
                title=quiz_metadata.get("title", f"Understanding {section_title}"),
                description=quiz_metadata.get("description", f"Test your understanding of the privacy implications in {section_title}"),
                section_id=section_id,
                questions=questions,
                estimated_time_minutes=max(2, len(questions)),
                passing_score=quiz_metadata.get("passing_score", 70),
                total_points=total_points,
                sensitivity_threshold=sensitivity_score,
                learning_objectives=quiz_metadata.get("learning_objectives", []),
                key_takeaways=quiz_metadata.get("key_takeaways", [])
            )
            
            return quiz
            
        except Exception as e:
            print(f"Error generating quiz for section '{section_title}': {e}")
            return None

    def should_generate_quiz(self, user_impact: UserImpactAnalysis) -> bool:
        """Determine if a section should have a quiz based on sensitivity scores"""
        # Generate quiz for high-sensitivity content
        if user_impact.sensitivity_score >= 8.0:
            return True
        
        # Generate quiz for high privacy impact
        if user_impact.privacy_impact_score >= 8.0:
            return True
        
        # Generate quiz for high data sharing risk
        if user_impact.data_sharing_risk >= 8.0:
            return True
        
        # Generate quiz for specific concerning scenarios
        if (user_impact.sensitivity_score >= 7.0 and 
            user_impact.privacy_impact_score >= 7.0):
            return True
        
        return False
    
    def determine_component_type(self, user_impact: UserImpactAnalysis) -> str:
        """Determine the best UI component type for this section"""
        # Interactive components for high-sensitivity content
        if user_impact.sensitivity_score >= 8.0:
            return "interactive_card"
        
        # Alert components for high privacy impact
        if user_impact.privacy_impact_score >= 8.0:
            return "alert_card"
        
        # Warning components for high data sharing risk
        if user_impact.data_sharing_risk >= 8.0:
            return "warning_card"
        
        # Enhanced components for moderate sensitivity
        if user_impact.sensitivity_score >= 6.0:
            return "enhanced_card"
        
        # Default card for low sensitivity
        return "basic_card" 