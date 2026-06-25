export type AgentStage = "intake" | "diagnosis" | "treatment" | "coding" | "audit";

export type StreamStage = AgentStage | "done" | "error";

export type StageStatus = "idle" | "started" | "completed" | "failed";

export interface AnalyzeRequest {
  patient_description: string;
  thread_id: string;
}

export interface AnalyzeResponse {
  patient_info?: Record<string, unknown> | null;
  diagnosis?: Record<string, unknown> | null;
  treatment_plan?: Record<string, unknown> | null;
  coding_result?: Record<string, unknown> | null;
  audit_result?: Record<string, unknown> | null;
  errors: string[];
}

export interface StreamEvent {
  thread_id: string;
  stage: StreamStage;
  status: "started" | "completed" | "failed";
  payload: Partial<AnalyzeResponse> | Record<string, unknown>;
  errors: string[];
}

export interface ICD10SearchResult {
  code: string;
  description: string;
  category?: string;
}

export interface ICD10SearchResponse {
  query: string;
  results: ICD10SearchResult[];
  count: number;
}

export interface ICD10LookupResponse {
  icd10: ICD10SearchResult;
  drg_group?: {
    drg_code?: string;
    description?: string;
    weight?: number;
    mean_los?: number;
  } | null;
}

export interface DrugInteraction {
  drug_a: string;
  drug_b: string;
  severity: string;
  description: string;
  recommendation: string;
}

export interface DDICheckResponse {
  new_drugs: string[];
  current_drugs: string[];
  interactions: DrugInteraction[];
  interaction_count: number;
  has_major_interaction: boolean;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}
