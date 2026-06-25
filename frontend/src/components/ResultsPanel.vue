<script setup lang="ts">
import { computed } from "vue";
import JsonPreview from "@/components/JsonPreview.vue";
import type { AnalyzeResponse } from "@/types/clinical";

const props = defineProps<{
  result: AnalyzeResponse;
}>();

const patient = computed(() => props.result.patient_info ?? {});
const diagnosis = computed(() => props.result.diagnosis ?? {});
const primaryDiagnosis = computed(() => {
  const value = diagnosis.value.primary_diagnosis;
  return value && typeof value === "object" ? (value as Record<string, unknown>) : {};
});
const treatment = computed(() => props.result.treatment_plan ?? {});
const coding = computed(() => props.result.coding_result ?? {});
const audit = computed(() => props.result.audit_result ?? {});

function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function text(value: unknown, fallback = "Not available"): string {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }
  return String(value);
}
</script>

<template>
  <div class="result-grid">
    <section class="result-card">
      <h3>Patient summary</h3>
      <div v-if="result.patient_info" class="kv-grid">
        <div class="kv">
          <span>Name</span>
          <strong>{{ text(patient.name) }}</strong>
        </div>
        <div class="kv">
          <span>Age / Gender</span>
          <strong>{{ text(patient.age) }} / {{ text(patient.gender) }}</strong>
        </div>
        <div class="kv">
          <span>Chief complaint</span>
          <strong>{{ text(patient.chief_complaint) }}</strong>
        </div>
        <div class="kv">
          <span>Current medications</span>
          <strong>{{ asArray(patient.current_medications).length }}</strong>
        </div>
      </div>
      <p v-else class="empty-state">Patient intake output will appear here.</p>
    </section>

    <section class="result-card">
      <h3>Diagnosis</h3>
      <div v-if="result.diagnosis">
        <div class="kv-grid">
          <div class="kv">
            <span>Primary diagnosis</span>
            <strong>{{ text(primaryDiagnosis.disease_name) }}</strong>
          </div>
          <div class="kv">
            <span>Confidence</span>
            <strong>{{ text(primaryDiagnosis.confidence) }}</strong>
          </div>
        </div>
        <h3>Recommended tests</h3>
        <ul class="list">
          <li v-for="item in asArray(diagnosis.recommended_tests)" :key="String(item)">
            {{ item }}
          </li>
        </ul>
      </div>
      <p v-else class="empty-state">Diagnosis output will appear here.</p>
    </section>

    <section class="result-card">
      <h3>Treatment</h3>
      <div v-if="result.treatment_plan">
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Medication</th>
                <th>Dosage</th>
                <th>Frequency</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="med in asArray(treatment.medications)"
                :key="JSON.stringify(med)"
              >
                <td>{{ text((med as Record<string, unknown>).drug_name) }}</td>
                <td>{{ text((med as Record<string, unknown>).dosage) }}</td>
                <td>{{ text((med as Record<string, unknown>).frequency) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="muted">{{ text(treatment.follow_up_plan, "") }}</p>
      </div>
      <p v-else class="empty-state">Treatment output will appear here.</p>
    </section>

    <section class="result-card">
      <h3>Coding</h3>
      <div v-if="result.coding_result" class="kv-grid">
        <div class="kv">
          <span>Primary ICD-10</span>
          <strong>
            {{ text((coding.primary_icd10 as Record<string, unknown>)?.code) }}
          </strong>
        </div>
        <div class="kv">
          <span>DRG</span>
          <strong>
            {{ text((coding.drg_group as Record<string, unknown>)?.drg_code) }}
          </strong>
        </div>
      </div>
      <p v-else class="empty-state">ICD-10 and DRG output will appear here.</p>
    </section>

    <section class="result-card">
      <h3>HIPAA audit</h3>
      <div v-if="result.audit_result" class="kv-grid">
        <div class="kv">
          <span>Compliant</span>
          <strong>{{ text(audit.hipaa_compliant) }}</strong>
        </div>
        <div class="kv">
          <span>Risk level</span>
          <strong>{{ text(audit.overall_risk_level) }}</strong>
        </div>
      </div>
      <p v-else class="empty-state">Audit output will appear here.</p>
    </section>

    <details v-if="result.patient_info || result.diagnosis" class="result-card">
      <summary>Raw response JSON</summary>
      <JsonPreview :value="result" />
    </details>
  </div>
</template>
