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

function text(value: unknown, fallback = "暂无数据"): string {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }
  return String(value);
}
</script>

<template>
  <div class="result-grid">
    <section class="result-card">
      <h3>患者摘要</h3>
      <div v-if="result.patient_info" class="kv-grid">
        <div class="kv">
          <span>姓名</span>
          <strong>{{ text(patient.name) }}</strong>
        </div>
        <div class="kv">
          <span>年龄 / 性别</span>
          <strong>{{ text(patient.age) }} / {{ text(patient.gender) }}</strong>
        </div>
        <div class="kv">
          <span>主诉</span>
          <strong>{{ text(patient.chief_complaint) }}</strong>
        </div>
        <div class="kv">
          <span>当前用药数量</span>
          <strong>{{ asArray(patient.current_medications).length }}</strong>
        </div>
      </div>
      <p v-else class="empty-state">问诊采集结果将在此显示。</p>
    </section>

    <section class="result-card">
      <h3>诊断</h3>
      <div v-if="result.diagnosis">
        <div class="kv-grid">
          <div class="kv">
            <span>主要诊断</span>
            <strong>{{ text(primaryDiagnosis.disease_name) }}</strong>
          </div>
          <div class="kv">
            <span>置信度</span>
            <strong>{{ text(primaryDiagnosis.confidence) }}</strong>
          </div>
        </div>
        <h3>建议检查</h3>
        <ul class="list">
          <li v-for="item in asArray(diagnosis.recommended_tests)" :key="String(item)">
            {{ item }}
          </li>
        </ul>
      </div>
      <p v-else class="empty-state">诊断结果将在此显示。</p>
    </section>

    <section class="result-card">
      <h3>治疗方案</h3>
      <div v-if="result.treatment_plan">
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>药物</th>
                <th>剂量</th>
                <th>频次</th>
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
      <p v-else class="empty-state">治疗方案将在此显示。</p>
    </section>

    <section class="result-card">
      <h3>医学编码</h3>
      <div v-if="result.coding_result" class="kv-grid">
        <div class="kv">
          <span>主要 ICD-10</span>
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
      <p v-else class="empty-state">ICD-10 和 DRG 结果将在此显示。</p>
    </section>

    <section class="result-card">
      <h3>HIPAA 审计</h3>
      <div v-if="result.audit_result" class="kv-grid">
        <div class="kv">
          <span>是否合规</span>
          <strong>{{ text(audit.hipaa_compliant) }}</strong>
        </div>
        <div class="kv">
          <span>风险等级</span>
          <strong>{{ text(audit.overall_risk_level) }}</strong>
        </div>
      </div>
      <p v-else class="empty-state">合规审计结果将在此显示。</p>
    </section>

    <details v-if="result.patient_info || result.diagnosis" class="result-card">
      <summary>原始响应 JSON</summary>
      <JsonPreview :value="result" />
    </details>
  </div>
</template>
