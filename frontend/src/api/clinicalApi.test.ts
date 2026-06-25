import { describe, expect, it, vi } from "vitest";
import { analyze, searchICD10 } from "@/api/clinicalApi";

describe("clinicalApi", () => {
  it("posts analyze requests to the FastAPI endpoint", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ errors: [], patient_info: { name: "A" } }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await analyze({
      patient_description: "Patient narrative with enough detail.",
      thread_id: "thread-1",
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/clinical/analyze",
      expect.objectContaining({ method: "POST" }),
    );
    expect(result.patient_info).toEqual({ name: "A" });
  });

  it("posts ICD-10 search queries", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ query: "pneumonia", results: [], count: 0 }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await searchICD10("pneumonia");

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/clinical/icd10/search",
      expect.objectContaining({ method: "POST" }),
    );
    expect(result.query).toBe("pneumonia");
  });
});
