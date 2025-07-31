// Types matching the actual backend API response structure
export interface PrivacyPolicy {
  processing_id: string;
  document: PrivacyPolicyDocument;
  ui_components: UIComponent[];
  processing_time: number;
  timestamp: string;
}

export interface PrivacyPolicyDocument {
  id: string;
  company_name: string;
  title: string;
  version?: string;
  effective_date?: string;
  sections: ProcessedSection[];
  // Legacy analysis (backward compatibility)
  overall_risk_level: RiskLevel;
  user_friendliness_score: number;
  // Enhanced numerical analysis
  overall_sensitivity_score: number;
  overall_privacy_impact: number;
  compliance_score: number;
  readability_score: number;
  // Document statistics
  total_word_count: number;
  estimated_reading_time: number;
  high_risk_sections: number;
  interactive_sections: number;
  // Processing metadata
  processing_status: string;
  created_at: string;
  updated_at: string;
}

export interface ProcessedSection {
  id: string;
  title: string;
  content: string;
  summary: string;
  // Enhanced content with styling
  styled_content?: StyledContent;
  styled_summary?: StyledContent;
  data_types: DataType[];
  user_rights: UserRight[];
  entities: ExtractedEntity[];
  user_impact: UserImpactAnalysis;
  legal_frameworks: LegalFramework[];
  importance_score: number;
  section_priority: number;
  word_count: number;
  reading_time: number;
  processing_timestamp: string;
}

export interface ExtractedEntity {
  entity_type: string;
  value: string;
  context: string;
  confidence: number;
}

export interface UserImpactAnalysis {
  risk_level: RiskLevel;
  // Enhanced numerical scores (0-10)
  sensitivity_score: number;
  privacy_impact_score: number;
  data_sharing_risk: number;
  // Original scores (1-5)
  user_control: number;
  transparency_score: number;
  key_concerns: string[];
  actionable_rights: UserRight[];
  // Enhanced UI features
  engagement_level: string;
  requires_quiz: boolean;
  requires_visual_aid: boolean;
  text_emphasis_level: number;
  highlight_color: string;
  font_weight: string;
}

export interface DataType {
  type: string;
  description: string;
  sources: string[];
  sensitivity: "low" | "medium" | "high";
  user_control: boolean;
}

export interface UserRight {
  right: "access" | "correction" | "deletion" | "portability" | "objection" | "restriction";
  description: string;
  limitations: string[];
}

export interface LegalFramework {
  framework: string;
  description: string;
  compliance_required: boolean;
}

export type RiskLevel = "low" | "medium" | "high";

export interface UIComponent {
  id: string;
  type: "highlight_card" | "risk_warning" | "rights_interactive" | "data_collection_card" | "standard_card" | "interactive_card" | "quiz_component";
  priority: number;
  content: {
    title: string;
    summary: string;
    risk_level: RiskLevel;
    user_control: number;
    transparency_score: number;
    key_concerns: string[];
    user_rights: string[];
    data_types: string[];
    importance_score: number;
    original_content: string;
    // Enhanced numerical scores
    sensitivity_score: number;
    privacy_impact_score: number;
    data_sharing_risk: number;
    // Enhanced UI features
    engagement_level: string;
    requires_quiz: boolean;
    requires_visual_aid: boolean;
    text_emphasis_level: number;
    highlight_color: string;
    font_weight: string;
    // Quiz content
    quiz?: InteractiveQuiz;
    // Styled content
    styled_content?: StyledContent;
    styled_summary?: StyledContent;
  };
  metadata: {
    processing_timestamp: string;
    entities_count: number;
    actionable_rights: string[];
  };
}

export interface PolicyAnalyzeRequest {
  company_name: string;
  company_url?: string;
  contact_email?: string;
  policy_content: string;
}

// Types for text visualization and styling
export interface TextSegment {
  id: string;
  text: string;
  sensitivity_score: number;
  start_position: number;
  end_position: number;
  highlight_color: string;
  text_color: string;
  font_weight: string;
  text_emphasis: number;
  requires_attention: boolean;
  context_type: string;
  key_terms: string[];
}

export interface StyledContent {
  original_text: string;
  segments: TextSegment[];
  overall_sensitivity: number;
  styling_applied: boolean;
  high_sensitivity_count: number;
  medium_sensitivity_count: number;
  total_segments: number;
}

// Quiz-related interfaces
export interface QuizOption {
  id: string;
  text: string;
  is_correct: boolean;
  explanation?: string;
}

export interface QuizQuestion {
  id: string;
  question_text: string;
  question_type: 'multiple_choice' | 'true_false' | 'fill_blank';
  options: QuizOption[];
  correct_explanation: string;
  difficulty: 'easy' | 'medium' | 'hard';
  points: number;
  related_content: string;
  sensitivity_score: number;
  learning_objective: string;
}

export interface InteractiveQuiz {
  id: string;
  title: string;
  description: string;
  section_id: string;
  questions: QuizQuestion[];
  estimated_time_minutes: number;
  passing_score: number;
  total_points: number;
  sensitivity_threshold: number;
  created_at: Date;
  learning_objectives: string[];
  key_takeaways: string[];
}

export interface QuizResult {
  quiz_id: string;
  user_id?: string;
  score: number;
  total_points: number;
  percentage: number;
  passed: boolean;
  time_taken_seconds: number;
  answers: Record<string, string>;
  completed_at: Date;
} 