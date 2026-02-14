export type RiskLevel = "Low" | "Medium" | "High";
export type ValidationStatus = "Pending" | "Validated" | "Needs Review";

export type User = {
  id: string;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
};

export type ProviderRecord = {
  id: string;
  provider_name: string;
  specialty: string | null;
  npi: string | null;
  phone: string | null;
  address: string | null;
  risk_level: RiskLevel;
  validation_status: ValidationStatus;
  confidence_score: number;
  primary_issue: string | null;
  source_file: string | null;
  created_at: string;
  updated_at: string;
};

export type ProviderSummary = {
  total_providers: number;
  high_risk_count: number;
  medium_risk_count: number;
  avg_confidence: number;
  requires_review: number;
};

export type ProviderListResponse = {
  items: ProviderRecord[];
  total: number;
  page: number;
  page_size: number;
};
