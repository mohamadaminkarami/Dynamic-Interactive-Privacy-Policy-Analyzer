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
  overall_risk_level: RiskLevel;
  user_friendliness_score: number;
  processing_status: string;
  created_at: string;
  updated_at: string;
}

export interface ProcessedSection {
  id: string;
  title: string;
  content: string;
  summary: string;
  data_types: DataType[];
  user_rights: UserRight[];
  entities: ExtractedEntity[];
  user_impact: UserImpactAnalysis;
  legal_frameworks: LegalFramework[];
  importance_score: number;
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
  user_control: number;
  transparency_score: number;
  key_concerns: string[];
  actionable_rights: UserRight[];
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
  type: "highlight_card" | "risk_warning" | "rights_interactive" | "data_collection_card" | "standard_card";
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
  };
  metadata: {
    processing_timestamp: string;
    entities_count: number;
    actionable_rights: string[];
  };
}

export interface PolicyRequest {
  policy_content: string;
  company_name: string;
  company_url?: string;
  document_type?: string;
  contact_email?: string;
} 