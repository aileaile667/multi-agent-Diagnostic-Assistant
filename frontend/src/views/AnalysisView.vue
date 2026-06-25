<script setup lang="ts">
import { storeToRefs } from "pinia";
import { Download, Play, RotateCcw, Sparkles } from "lucide-vue-next";
import ResultsPanel from "@/components/ResultsPanel.vue";
import StageProgress from "@/components/StageProgress.vue";
import { useAnalysisStore } from "@/stores/analysisStore";

const store = useAnalysisStore();
const {
  patientDescription,
  threadId,
  isRunning,
  usedFallback,
  error,
  stageStatuses,
  result,
  canExport,
} = storeToRefs(store);
</script>

<template>
  <section class="analysis-grid">
    <div class="panel">
      <div class="panel-header">
        <div>
          <h2>Patient narrative</h2>
          <p class="muted">Submit free text to the five-agent pipeline.</p>
        </div>
        <button class="icon-button" type="button" title="Load sample" @click="store.useSampleCase">
          <Sparkles :size="17" />
        </button>
      </div>
      <div class="panel-body form-grid">
        <div class="field">
          <label for="thread-id">Thread ID</label>
          <input id="thread-id" v-model="threadId" class="input" />
        </div>
        <div class="field">
          <label for="patient-description">Case description</label>
          <textarea
            id="patient-description"
            v-model="patientDescription"
            class="textarea"
            :disabled="isRunning"
          ></textarea>
        </div>
        <div v-if="error" class="alert">{{ error }}</div>
        <div v-if="usedFallback" class="badge warning">
          Stream unavailable. Loaded non-streaming result.
        </div>
        <div class="action-row">
          <button
            class="button primary"
            type="button"
            :disabled="isRunning || patientDescription.length < 10"
            @click="store.runAnalysis"
          >
            <Play :size="17" />
            {{ isRunning ? "Running" : "Run analysis" }}
          </button>
          <button class="button" type="button" :disabled="isRunning" @click="store.resetRun">
            <RotateCcw :size="17" />
            Reset
          </button>
          <button class="button" type="button" :disabled="!canExport" @click="store.exportJson">
            <Download :size="17" />
            Export JSON
          </button>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">
        <div>
          <h2>Agent results</h2>
          <p class="muted">Each section unlocks as the stream completes a stage.</p>
        </div>
      </div>
      <div class="panel-body">
        <ResultsPanel :result="result" />
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">
        <div>
          <h2>Pipeline</h2>
          <p class="muted">Intake to audit execution state.</p>
        </div>
      </div>
      <div class="panel-body">
        <StageProgress :statuses="stageStatuses" />
      </div>
    </div>
  </section>
</template>
