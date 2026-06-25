import { defineStore } from "pinia";
import { analyze, streamAnalyze } from "@/api/clinicalApi";
import type {
  AgentStage,
  AnalyzeResponse,
  StageStatus,
  StreamEvent,
} from "@/types/clinical";

export const sampleCase = [
  "45-year-old male presenting with fever 39.2 C for 3 days, productive cough",
  "with yellow sputum, and right-sided chest pain. History of type 2 diabetes",
  "and hypertension. Current medications: metformin 500mg BID, lisinopril",
  "10mg daily. Allergies: penicillin rash. Labs: WBC 15000/uL, CRP 85 mg/L,",
  "chest X-ray shows right lower lobe infiltrate.",
].join(" ");

export const agentStages: Array<{ key: AgentStage; label: string; description: string }> = [
  { key: "intake", label: "Intake", description: "Extract patient facts" },
  { key: "diagnosis", label: "Diagnosis", description: "Rank differential diagnosis" },
  { key: "treatment", label: "Treatment", description: "Plan care and medications" },
  { key: "coding", label: "Coding", description: "Map ICD-10 and DRG" },
  { key: "audit", label: "Audit", description: "Check HIPAA signals" },
];

function createStageStatuses(): Record<AgentStage, StageStatus> {
  return {
    intake: "idle",
    diagnosis: "idle",
    treatment: "idle",
    coding: "idle",
    audit: "idle",
  };
}

function mergePayload(result: AnalyzeResponse, payload: Record<string, unknown>): AnalyzeResponse {
  return {
    ...result,
    patient_info: (payload.patient_info as Record<string, unknown> | null) ?? result.patient_info,
    diagnosis: (payload.diagnosis as Record<string, unknown> | null) ?? result.diagnosis,
    treatment_plan:
      (payload.treatment_plan as Record<string, unknown> | null) ?? result.treatment_plan,
    coding_result:
      (payload.coding_result as Record<string, unknown> | null) ?? result.coding_result,
    audit_result: (payload.audit_result as Record<string, unknown> | null) ?? result.audit_result,
    errors: (payload.errors as string[] | undefined) ?? result.errors,
  };
}

export const useAnalysisStore = defineStore("analysis", {
  state: () => ({
    patientDescription: sampleCase,
    threadId: `demo-${Date.now()}`,
    isRunning: false,
    usedFallback: false,
    error: "",
    stageStatuses: createStageStatuses(),
    result: {
      patient_info: null,
      diagnosis: null,
      treatment_plan: null,
      coding_result: null,
      audit_result: null,
      errors: [],
    } as AnalyzeResponse,
  }),
  getters: {
    canExport: (state) =>
      Boolean(
        state.result.patient_info ||
          state.result.diagnosis ||
          state.result.treatment_plan ||
          state.result.coding_result ||
          state.result.audit_result,
      ),
  },
  actions: {
    resetRun() {
      this.error = "";
      this.usedFallback = false;
      this.stageStatuses = createStageStatuses();
      this.result = {
        patient_info: null,
        diagnosis: null,
        treatment_plan: null,
        coding_result: null,
        audit_result: null,
        errors: [],
      };
    },
    useSampleCase() {
      this.patientDescription = sampleCase;
    },
    applyStreamEvent(event: StreamEvent) {
      if (event.stage === "error") {
        this.error = event.errors.join("; ") || "Pipeline stream failed.";
        return;
      }

      if (event.stage === "done") {
        this.result = mergePayload(this.result, event.payload as Record<string, unknown>);
        this.isRunning = false;
        return;
      }

      this.stageStatuses[event.stage] = event.status;
      if (event.status === "completed") {
        this.result = mergePayload(this.result, event.payload as Record<string, unknown>);
      }
    },
    async runAnalysis() {
      this.resetRun();
      this.isRunning = true;

      const request = {
        patient_description: this.patientDescription,
        thread_id: this.threadId || `demo-${Date.now()}`,
      };

      try {
        await streamAnalyze(request, (event) => this.applyStreamEvent(event));
      } catch (streamError) {
        this.usedFallback = true;
        try {
          const response = await analyze(request);
          this.result = response;
          this.stageStatuses = {
            intake: "completed",
            diagnosis: "completed",
            treatment: "completed",
            coding: "completed",
            audit: "completed",
          };
        } catch (fallbackError) {
          this.error =
            fallbackError instanceof Error
              ? fallbackError.message
              : "Clinical analysis failed.";
        } finally {
          this.isRunning = false;
        }
        return;
      }

      this.isRunning = false;
    },
    exportJson() {
      const blob = new Blob([JSON.stringify(this.result, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${this.threadId || "clinical-analysis"}.json`;
      link.click();
      URL.revokeObjectURL(url);
    },
  },
});
