PARSE_POLICY_PROMPT = """
Parse this privacy policy into logical sections. Each section should have:
1. A clear title/heading. If the section already has a title, use that. If not, use the section title.
2. The whole content of that section. Do not include the section title in the content.

Privacy Policy Content:

{content}


Return a JSON array of sections with this structure:
[
    {{
        "title": "Section Title",
        "content": "Section content...",
    }}
]

Focus on major sections like:
- Data Collection
- Data Usage
- Data Sharing
- User Rights
- Cookies
- Contact Information
- Security
- Changes to Policy
"""

GENERATE_SECTION_SUMMARY_PROMPT = """
Create a comprehensive, user-friendly summary of this privacy policy section in plain English.

Privacy Policy Section Content:
{content}

Write a detailed summary that:
- Identifies and explains ALL major points, categories, or subcategories mentioned
- Highlights specific activities, technologies, or processes (not just general terms)
- Explains the practical implications and real-world meaning for users
- Mentions specific examples and details when provided in the content
- Covers the complete scope of what the section addresses
- Uses clear, simple language without legal jargon
- Is structured as 2-4 sentences that capture the full breadth

Focus on being comprehensive by:
- Including all significant points mentioned in the section
- Explaining what things actually mean in practical terms
- Mentioning specific details that users should be aware of
- Covering both the "what" and the "why" when stated
- Being specific rather than vague (use actual terms from the content)

Do not use quotation marks. Write as plain text only.
"""

EXTRACT_ENTITIES_PROMPT = """
Extract key entities from this privacy policy section, focusing on specific and detailed information:

{content}

Look for any significant entities mentioned, including but not limited to:
- Specific data types: name, email, phone, address, payment info, biometric data, location, device info, browsing history, etc.
- User rights: access, deletion, portability, opt-out, correction, consent withdrawal
- Third parties: advertisers, partners, service providers, affiliates, etc.
- Company obligations: data protection, security measures, consent, disclosure rules
- Legal basis: legitimate interest, consent, contract, compliance

Provide a JSON response with an array of entities:
{{
    "entities": [
        {{
            "entity_type": "data_type/user_right/company_obligation/third_party/legal_basis",
            "value": "specific extracted value (be detailed, not generic)",
            "context": "surrounding context where found",
            "confidence": 0.95
        }}
    ]
}}

Extract ALL significant entities mentioned, not just the obvious ones.
"""

ANALYZE_USER_IMPACT_PROMPT = """
Analyze how this privacy policy section affects users with detailed numerical scoring:

{content}

Return a JSON object with this structure. Do not include any other text or formatting.
{{
    "risk_level": "high/medium/low",
    "sensitivity_score": 7.5,
    "privacy_impact_score": 8.0,
    "data_sharing_risk": 6.5,
    "user_control": 3,
    "transparency_score": 4 [0-5],
    "key_concerns": ["specific, detailed concerns based on actual content"],
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

For key_concerns, identify ANY specific issues that impact users, such as:
- "Biometric data collection requires consent but is permanent"
- "Location data shared with ad partners for targeting"
- "Device fingerprinting enables cross-site tracking"
- "Payment information stored indefinitely"
- "Third-party data brokers provide additional personal data"

Pay attention to any high-impact items including but not limited to:
- Biometric/health data collection
- Precise location tracking
- Cross-device/cross-site tracking
- Inferred identity profiling
- Extensive third-party sharing
- Permanent data retention
- Limited user control options

UI Enhancement Rules:
- engagement_level: "quiz" for scores 8+, "interactive" for 6-7, "standard" for <6
- requires_quiz: true for sensitivity_score >= 8.0
- requires_visual_aid: true for privacy_impact_score >= 8.0
- text_emphasis_level: 1-5 based on importance (5 = highest emphasis)
- highlight_color: "red" for 8+, "orange" for 6-7, "yellow" for 4-5, "neutral" for <4
- font_weight: "bold" for 8+, "medium" for 6-7, "normal" for <6
"""

CALCULATE_IMPORTANCE_SCORE_PROMPT = """
Calculate an importance score (0.0 to 1.0) for this privacy policy section:

Content: {content}
User Impact: Risk Level: {risk_level}, User Control: {user_control}

Consider:
- User rights and freedoms impact
- Data sensitivity
- Legal obligations
- Potential consequences
- User decision-making needs

Respond with just a number between 0.0 and 1.0.
"""

ANALYZE_TEXT_SEGMENTS_PROMPT = """
Analyze this privacy policy text and break it into segments with sensitivity scoring for text visualization:

{content}

Overall Content Sensitivity: {overall_sensitivity}/10

Create segments that should have different visual emphasis. Look for any content that has significance for users, including but not limited to:
- Statements about data collection, usage, or sharing
- User rights, choices, and control options
- Third-party involvement and partnerships  
- Data retention, storage, and deletion policies
- Security measures and breach procedures
- Contact information and support channels
- Legal obligations and compliance requirements
- Any other content that impacts user privacy or requires user attention

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

GENERATE_QUIZ_PROMPT = """
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

DIFFICULTY LEVELS:
- Easy: Basic understanding of key concepts
- Medium: Implications and consequences
- Hard: Nuanced understanding and decision-making

Response format: Just the JSON with quiz structure. Do not include any other text or formatting.
"""