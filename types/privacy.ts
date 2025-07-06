// Data types for privacy policies
export enum DataType {
  PERSONAL_INFO = 'personal_info',
  CONTACT_INFO = 'contact_info',
  LOCATION = 'location',
  BROWSING_HISTORY = 'browsing_history',
  COOKIES = 'cookies',
  DEVICE_INFO = 'device_info',
  USAGE_DATA = 'usage_data',
  FINANCIAL_INFO = 'financial_info',
  SENSITIVE_DATA = 'sensitive_data',
  BIOMETRIC_DATA = 'biometric_data',
  THIRD_PARTY_DATA = 'third_party_data',
  ANALYTICS_DATA = 'analytics_data',
  MARKETING_DATA = 'marketing_data',
  COMMUNICATION_DATA = 'communication_data',
  SOCIAL_MEDIA_DATA = 'social_media_data',
  BEHAVIORAL_DATA = 'behavioral_data',
  PREFERENCE_DATA = 'preference_data',
  ACCOUNT_DATA = 'account_data',
  TRANSACTION_DATA = 'transaction_data',
  DEMOGRAPHIC_DATA = 'demographic_data',
  HEALTH_DATA = 'health_data',
  EDUCATION_DATA = 'education_data',
  EMPLOYMENT_DATA = 'employment_data',
}

export enum UserRight {
  ACCESS = 'access',
  DELETION = 'deletion',
  PORTABILITY = 'portability',
  OPT_OUT = 'opt_out',
  CORRECTION = 'correction',
  CONSENT_WITHDRAWAL = 'consent_withdrawal',
}

export enum RiskLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
}

// Text styling interfaces
export interface TextSegment {
  text: string;
  sensitivity_score: number;
  context_type: string;
  key_terms: string[];
  highlight_color: string;
  text_color: string;
  font_weight: string;
  text_emphasis: number;
  requires_attention: boolean;
}

export interface StyledContent {
  segments: TextSegment[];
  total_segments: number;
  high_sensitivity_count: number;
  average_sensitivity: number;
}

// User impact analysis with enhanced numerical scoring
export interface UserImpactAnalysis {
  // Core numerical scores (0-10)
  sensitivity_score: number;
  privacy_impact_score: number;
  data_sharing_risk: number;
  
  // Enhanced UI features
  engagement_level: number;
  requires_quiz: boolean;
  requires_visual_aid: boolean;
  text_emphasis_level: number;
  highlight_color: string;
  font_weight: string;
  
  // Extracted information
  data_types: DataType[];
  user_rights: UserRight[];
  risk_level: RiskLevel;
  risk_factors: string[];
  actionable_rights: string[];
  
  // Descriptive analysis
  key_concerns: string[];
  impact_summary: string;
  recommendations: string[];
  
  // Temporal aspects
  data_retention: string;
  user_control: string;
  consent_type: string;
  
  // Third-party interactions
  third_party_sharing: boolean;
  data_selling: boolean;
  international_transfer: boolean;
  
  // Compliance indicators
  gdpr_compliant: boolean;
  ccpa_compliant: boolean;
  coppa_compliant: boolean;
}

export interface ExtractedEntity {
  entity_type: string;
  value: string;
  confidence_score: number;
  context: string;
  start_position: number;
  end_position: number;
}

export interface LegalFramework {
  name: string;
  applicability: string;
  compliance_status: string;
  requirements: string[];
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

export interface ProcessedSection {
  id: string;
  title: string;
  original_content: string;
  summary: string;
  styled_content?: StyledContent;
  styled_summary?: StyledContent;
  user_impact: UserImpactAnalysis;
  component_type: string;
  section_priority: number;
  quiz?: InteractiveQuiz;
  requires_quiz: boolean;
  data_types: DataType[];
  user_rights: UserRight[];
  entities: ExtractedEntity[];
  legal_frameworks: LegalFramework[];
  importance_score: number;
  word_count: number;
  reading_time: number;
  processing_timestamp: Date;
}

export interface PrivacyPolicyDocument {
  id: string;
  title: string;
  company_name: string;
  last_updated: Date;
  effective_date: Date;
  sections: ProcessedSection[];
  
  // Enhanced document analysis
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
  processing_timestamp: Date;
  processing_time_seconds: number;
  llm_model_used: string;
  api_version: string;
} 