<script setup lang="ts">
import { computed, ref } from "vue";
import { ShieldAlert } from "lucide-vue-next";
import { checkDDI } from "@/api/clinicalApi";
import type { DDICheckResponse } from "@/types/clinical";

const newDrugText = ref("warfarin");
const currentDrugText = ref("aspirin");
const response = ref<DDICheckResponse | null>(null);
const isLoading = ref(false);
const error = ref("");

const newDrugs = computed(() =>
  newDrugText.value
    .split(",")
    .map((drug) => drug.trim())
    .filter(Boolean),
);
const currentDrugs = computed(() =>
  currentDrugText.value
    .split(",")
    .map((drug) => drug.trim())
    .filter(Boolean),
);

async function runCheck() {
  if (!newDrugs.value.length) {
    return;
  }
  isLoading.value = true;
  error.value = "";
  try {
    response.value = await checkDDI(newDrugs.value, currentDrugs.value);
  } catch (err) {
    error.value = err instanceof Error ? err.message : "药物交互检查失败。";
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <section class="tool-grid">
    <div class="panel">
      <div class="panel-header">
        <h2>药物交互检查</h2>
      </div>
      <div class="panel-body form-grid">
        <div class="field">
          <label for="new-drugs">新增处方</label>
          <input id="new-drugs" v-model="newDrugText" class="input" />
        </div>
        <div class="field">
          <label for="current-drugs">当前用药</label>
          <input id="current-drugs" v-model="currentDrugText" class="input" />
        </div>
        <button class="button primary" type="button" :disabled="isLoading" @click="runCheck">
          <ShieldAlert :size="17" />
          {{ isLoading ? "检查中" : "检查交互风险" }}
        </button>
        <div v-if="error" class="alert">{{ error }}</div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">
        <h2>安全性结果</h2>
        <span
          v-if="response"
          class="badge"
          :class="response.has_major_interaction ? 'danger' : 'success'"
        >
          {{ response.interaction_count }} 项交互
        </span>
      </div>
      <div class="panel-body">
        <div v-if="response?.interactions.length" class="result-grid">
          <article
            v-for="interaction in response.interactions"
            :key="JSON.stringify(interaction)"
            class="result-card"
          >
            <span class="badge danger">{{ interaction.severity }}</span>
            <h3>{{ interaction.drug_a }} + {{ interaction.drug_b }}</h3>
            <p>{{ interaction.description }}</p>
            <p class="muted">{{ interaction.recommendation }}</p>
          </article>
        </div>
        <p v-else-if="response" class="empty-state">未发现已知药物交互风险。</p>
        <p v-else class="empty-state">运行检查后将在此显示交互详情。</p>
      </div>
    </div>
  </section>
</template>
