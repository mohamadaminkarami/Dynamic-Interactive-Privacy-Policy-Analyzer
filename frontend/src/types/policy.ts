// Types matching the API response structure
export interface PrivacyPolicy {
  processing_id: string;
  policy_analysis: PolicyAnalysis;
  ui_components: UIComponent[];
  user_feedback: any;
  processing_time: number;
  version: string;
}

export interface PolicyAnalysis {
  document_analysis: DocumentAnalysis;
  risk_level: RiskLevel;
  user_friendliness: number;
  recommendations: string[];
  summary: string;
}

export interface DocumentAnalysis {
  metadata: DocumentMetadata;
  content_overview: ContentOverview;
  key_entities: KeyEntity[];
  user_impact_assessment: UserImpactAssessment;
  importance_scores: ImportanceScore[];
}

export interface DocumentMetadata {
  title: string;
  language: string;
  word_count: number;
  last_updated: string;
}

export interface ContentOverview {
  data_types: DataType[];
  purposes: string[];
  third_parties: string[];
  storage_period: string;
  user_rights: UserRight[];
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

export interface KeyEntity {
  name: string;
  type: "company" | "regulator" | "third_party" | "concept";
  description: string;
  relevance: "high" | "medium" | "low";
}

export interface UserImpactAssessment {
  overall_risk: RiskLevel;
  user_benefit: "high" | "medium" | "low";
  transparency: "high" | "medium" | "low";
  user_control: "high" | "medium" | "low";
  privacy_implications: string[];
}

export interface ImportanceScore {
  content_area: string;
  score: number;
  reasoning: string;
}

export type RiskLevel = "low" | "medium" | "high";

export interface UIComponent {
  id: string;
  type: "highlight_card" | "risk_warning" | "rights_interactive" | "data_collection_card" | "standard_card";
  title: string;
  content: string;
  metadata: ComponentMetadata;
  importance_score: number;
}

export interface ComponentMetadata {
  visual_style: "info" | "warning" | "error" | "success";
  requires_attention: boolean;
  user_action_required: boolean;
  related_sections: string[];
}

export interface PolicyRequest {
  content: string;
  company_name: string;
  company_url?: string;
  document_type?: string;
  contact_email?: string;
} 