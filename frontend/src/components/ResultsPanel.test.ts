import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import ResultsPanel from "@/components/ResultsPanel.vue";

describe("ResultsPanel", () => {
  it("renders primary diagnosis when available", () => {
    const wrapper = mount(ResultsPanel, {
      props: {
        result: {
          patient_info: null,
          diagnosis: {
            primary_diagnosis: {
              disease_name: "Pneumonia",
              confidence: 0.88,
            },
            recommended_tests: ["Chest X-ray"],
          },
          treatment_plan: null,
          coding_result: null,
          audit_result: null,
          errors: [],
        },
      },
    });

    expect(wrapper.text()).toContain("Pneumonia");
    expect(wrapper.text()).toContain("Chest X-ray");
  });
});
