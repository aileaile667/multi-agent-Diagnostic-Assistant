<script setup lang="ts">
import { agentStages } from "@/stores/analysisStore";
import type { AgentStage, StageStatus } from "@/types/clinical";

defineProps<{
  statuses: Record<AgentStage, StageStatus>;
}>();

const statusLabels: Record<StageStatus, string> = {
  idle: "等待中",
  started: "执行中",
  completed: "已完成",
  failed: "失败",
};
</script>

<template>
  <div class="stage-list" aria-label="智能体流水线进度">
    <article
      v-for="(stage, index) in agentStages"
      :key="stage.key"
      class="stage-item"
      :class="statuses[stage.key]"
    >
      <div class="stage-number">{{ index + 1 }}</div>
      <div>
        <strong>{{ stage.label }}</strong>
        <p class="muted">{{ stage.description }}</p>
      </div>
      <span class="badge" :class="{ success: statuses[stage.key] === 'completed' }">
        {{ statusLabels[statuses[stage.key]] }}
      </span>
    </article>
  </div>
</template>
