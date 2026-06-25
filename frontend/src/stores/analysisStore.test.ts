import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it } from "vitest";
import { useAnalysisStore } from "@/stores/analysisStore";

describe("analysisStore", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("merges stream stage payloads into the result", () => {
    const store = useAnalysisStore();

    store.applyStreamEvent({
      thread_id: "t-1",
      stage: "diagnosis",
      status: "completed",
      payload: { diagnosis: { primary_diagnosis: { disease_name: "Pneumonia" } } },
      errors: [],
    });

    expect(store.stageStatuses.diagnosis).toBe("completed");
    expect(store.result.diagnosis).toEqual({
      primary_diagnosis: { disease_name: "Pneumonia" },
    });
  });

  it("records stream errors", () => {
    const store = useAnalysisStore();

    store.applyStreamEvent({
      thread_id: "t-1",
      stage: "error",
      status: "failed",
      payload: {},
      errors: ["Pipeline error"],
    });

    expect(store.error).toBe("Pipeline error");
  });
});
