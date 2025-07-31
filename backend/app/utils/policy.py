from typing import List, Optional

from app.api.schemas import (
    UIComponent,
)
from models import ContentChunk, PrivacyPolicyDocument, ProcessedSection, RiskLevel


# Content Chunking Function
def chunk_content(
    content: str, max_chunk_size: int = 4000, overlap: int = 200
) -> List[ContentChunk]:
    """Intelligently chunk content for processing"""
    chunks = []

    # Split by paragraphs first
    paragraphs = content.split("\n\n")
    current_chunk = ""
    chunk_position = 0

    for paragraph in paragraphs:
        # If adding this paragraph would exceed chunk size
        if len(current_chunk) + len(paragraph) > max_chunk_size and current_chunk:
            # Create chunk from current content
            chunk_id = f"chunk_{chunk_position}"
            chunks.append(
                ContentChunk(
                    id=chunk_id,
                    content=current_chunk.strip(),
                    section_title=extract_section_title(current_chunk),
                    position=chunk_position,
                    tokens=estimate_tokens(current_chunk),
                )
            )

            # Start new chunk with overlap
            overlap_text = (
                current_chunk[-overlap:]
                if len(current_chunk) > overlap
                else current_chunk
            )
            current_chunk = overlap_text + "\n\n" + paragraph
            chunk_position += 1
        else:
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph

    # Add final chunk if there's remaining content
    if current_chunk.strip():
        chunk_id = f"chunk_{chunk_position}"
        chunks.append(
            ContentChunk(
                id=chunk_id,
                content=current_chunk.strip(),
                section_title=extract_section_title(current_chunk),
                position=chunk_position,
                tokens=estimate_tokens(current_chunk),
            )
        )

    return chunks


def extract_section_title(content: str) -> Optional[str]:
    """Extract section title from content"""
    lines = content.split("\n")
    for line in lines[:3]:  # Check first 3 lines
        line = line.strip()
        if line and len(line) < 100 and not line.endswith("."):
            # Likely a title
            return line
    return None


def estimate_tokens(text: str) -> int:
    """Estimate token count for text"""
    return int(len(text.split()) * 1.3)


# UI Component Generation
def generate_ui_components(document: PrivacyPolicyDocument) -> List[UIComponent]:
    """Generate dynamic UI components from processed document"""
    components = []

    # Sort sections by importance score
    sorted_sections = sorted(
        document.sections, key=lambda s: s.importance_score, reverse=True
    )

    for i, section in enumerate(sorted_sections):
        # Determine component type based on content and new scoring
        component_type = determine_component_type(section)

        # Create component with enhanced numerical scoring
        component = UIComponent(
            id=f"component_{section.id}",
            type=component_type,
            priority=i + 1,
            content={
                "title": section.title,
                "summary": section.summary,
                "risk_level": section.user_impact.risk_level.value,
                # Enhanced numerical scores
                "sensitivity_score": section.user_impact.sensitivity_score,
                "privacy_impact_score": section.user_impact.privacy_impact_score,
                "data_sharing_risk": section.user_impact.data_sharing_risk,
                # Original scores
                "user_control": section.user_impact.user_control,
                "transparency_score": section.user_impact.transparency_score,
                "key_concerns": section.user_impact.key_concerns,
                "user_rights": [right.value for right in section.user_rights],
                "data_types": [dt.value for dt in section.data_types],
                "importance_score": section.importance_score,
                "original_content": section.original_content,
                # Enhanced UI features
                "engagement_level": section.user_impact.engagement_level,
                "requires_quiz": section.user_impact.requires_quiz,
                "requires_visual_aid": section.user_impact.requires_visual_aid,
                "text_emphasis_level": section.user_impact.text_emphasis_level,
                "highlight_color": section.user_impact.highlight_color,
                "font_weight": section.user_impact.font_weight,
                # Additional metadata
                "word_count": section.word_count,
                "reading_time": section.reading_time,
                # Styled content for text visualization
                "styled_content": (
                    section.styled_content.dict() if section.styled_content else None
                ),
                "styled_summary": (
                    section.styled_summary.dict() if section.styled_summary else None
                ),
                # Quiz data for high-sensitivity sections
                "quiz": section.quiz.dict() if section.quiz else None,
            },
            metadata={
                "processing_timestamp": section.processing_timestamp.isoformat(),
                "entities_count": len(section.entities),
                "actionable_rights": [
                    right.value for right in section.user_impact.actionable_rights
                ],
                "section_priority": section.section_priority,
                "ui_enhancement_features": {
                    "needs_interaction": section.user_impact.engagement_level
                    in ["interactive", "quiz"],
                    "high_attention": section.user_impact.sensitivity_score >= 8.0,
                    "visual_aids_needed": section.user_impact.requires_visual_aid,
                    "quiz_recommended": section.user_impact.requires_quiz,
                    "styled_content_available": section.styled_content is not None
                    and section.styled_content.styling_applied,
                    "styled_summary_available": section.styled_summary is not None
                    and section.styled_summary.styling_applied,
                },
            },
        )

        components.append(component)

    return components


def determine_component_type(section: ProcessedSection) -> str:
    """Determine the best UI component type for a section based on enhanced scoring"""

    # Use engagement level as primary determinant
    if section.user_impact.engagement_level == "quiz":
        return "quiz_component"

    if section.user_impact.engagement_level == "interactive":
        return "interactive_component"

    # High sensitivity scores get special treatment
    if section.user_impact.sensitivity_score >= 8.0:
        return "high_sensitivity_card"

    # High privacy impact = warning component
    if section.user_impact.privacy_impact_score >= 7.0:
        return "privacy_warning"

    # High importance = highlight card
    if section.importance_score > 0.8:
        return "highlight_card"

    # High data sharing risk = risk warning
    if section.user_impact.data_sharing_risk >= 7.0:
        return "risk_warning"

    # User rights = interactive component
    if section.user_rights:
        return "rights_interactive"

    # Data collection = data card
    if section.data_types:
        return "data_collection_card"

    # Default = standard card
    return "standard_card"


def calculate_overall_risk(sections: List[ProcessedSection]) -> RiskLevel:
    """Calculate overall risk level from all sections"""
    risk_scores = {"high": 3, "medium": 2, "low": 1}

    if not sections:
        return RiskLevel.MEDIUM

    total_score = sum(
        risk_scores[section.user_impact.risk_level.value] for section in sections
    )
    avg_score = total_score / len(sections)

    if avg_score >= 2.5:
        return RiskLevel.HIGH
    elif avg_score >= 1.5:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW


def calculate_user_friendliness(sections: List[ProcessedSection]) -> int:
    """Calculate overall user friendliness score (1-5)"""
    if not sections:
        return 3

    total_transparency = sum(
        section.user_impact.transparency_score for section in sections
    )
    total_control = sum(section.user_impact.user_control for section in sections)

    avg_transparency = total_transparency / len(sections)
    avg_control = total_control / len(sections)

    # Combine transparency and control scores
    friendliness = (avg_transparency + avg_control) / 2
    return int(round(friendliness))


def calculate_overall_sensitivity(sections: List[ProcessedSection]) -> float:
    """Calculate overall sensitivity score (0-10) from all sections"""
    if not sections:
        return 5.0

    # Weight by importance score
    weighted_sum = sum(
        section.user_impact.sensitivity_score * section.importance_score
        for section in sections
    )
    total_weight = sum(section.importance_score for section in sections)

    if total_weight == 0:
        return sum(section.user_impact.sensitivity_score for section in sections) / len(
            sections
        )

    return round(weighted_sum / total_weight, 1)


def calculate_overall_privacy_impact(sections: List[ProcessedSection]) -> float:
    """Calculate overall privacy impact score (0-10) from all sections"""
    if not sections:
        return 5.0

    # Weight by importance score
    weighted_sum = sum(
        section.user_impact.privacy_impact_score * section.importance_score
        for section in sections
    )
    total_weight = sum(section.importance_score for section in sections)

    if total_weight == 0:
        return sum(
            section.user_impact.privacy_impact_score for section in sections
        ) / len(sections)

    return round(weighted_sum / total_weight, 1)


def calculate_compliance_score(sections: List[ProcessedSection]) -> float:
    """Calculate compliance score (0-10) based on transparency and user control"""
    if not sections:
        return 5.0

    # Calculate based on transparency and user control
    avg_transparency = sum(
        section.user_impact.transparency_score for section in sections
    ) / len(sections)
    avg_control = sum(section.user_impact.user_control for section in sections) / len(
        sections
    )

    # Convert from 1-5 scale to 0-10 scale
    compliance = ((avg_transparency + avg_control) / 2) * 2
    return round(compliance, 1)


def calculate_readability_score(sections: List[ProcessedSection]) -> float:
    """Calculate readability score (0-10) based on section complexity and clarity"""
    if not sections:
        return 5.0

    # Base score on transparency scores and content complexity
    avg_transparency = sum(
        section.user_impact.transparency_score for section in sections
    ) / len(sections)

    # Adjust based on content length (longer sections are typically harder to read)
    avg_word_count = sum(section.word_count for section in sections) / len(sections)
    length_penalty = min(2.0, avg_word_count / 200)  # Penalty for long sections

    readability = (avg_transparency * 2) - length_penalty
    return round(max(0.0, min(10.0, readability)), 1)
