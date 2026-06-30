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
          <h2>患者叙述</h2>
          <p class="muted">提交自然语言病情描述，运行五智能体流水线。</p>
        </div>
        <button class="icon-button" type="button" title="载入示例病例" @click="store.useSampleCase">
          <Sparkles :size="17" />
        </button>
      </div>
      <div class="panel-body form-grid">
        <div class="field">
          <label for="thread-id">会话 ID</label>
          <input id="thread-id" v-model="threadId" class="input" />
        </div>
        <div class="field">
          <label for="patient-description">病例描述</label>
          <textarea
            id="patient-description"
            v-model="patientDescription"
            class="textarea"
            :disabled="isRunning"
          ></textarea>
        </div>
        <div v-if="error" class="alert">{{ error }}</div>
        <div v-if="usedFallback" class="badge warning">
          流式接口不可用，已加载普通接口结果。
        </div>
        <div class="action-row">
          <button
            class="button primary"
            type="button"
            :disabled="isRunning || patientDescription.length < 10"
            @click="store.runAnalysis"
          >
            <Play :size="17" />
            {{ isRunning ? "分析中" : "开始分析" }}
          </button>
          <button class="button" type="button" :disabled="isRunning" @click="store.resetRun">
            <RotateCcw :size="17" />
            重置
          </button>
          <button class="button" type="button" :disabled="!canExport" @click="store.exportJson">
            <Download :size="17" />
            导出 JSON
          </button>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">
        <div>
          <h2>智能体结果</h2>
          <p class="muted">每个阶段完成后，对应结果会逐步显示。</p>
        </div>
      </div>
      <div class="panel-body">
        <ResultsPanel :result="result" />
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">
        <div>
          <h2>处理流水线</h2>
          <p class="muted">从问诊采集到合规审计的执行状态。</p>
        </div>
      </div>
      <div class="panel-body">
        <StageProgress :statuses="stageStatuses" />
      </div>
    </div>
  </section>
</template>
