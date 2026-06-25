<script setup lang="ts">
import { agentStages } from "@/stores/analysisStore";
import type { AgentStage, StageStatus } from "@/types/clinical";

defineProps<{
  statuses: Record<AgentStage, StageStatus>;
}>();
</script>

<template>
  <div class="stage-list" aria-label="Agent pipeline progress">
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
        {{ statuses[stage.key] }}
      </span>
    </article>
  </div>
</template>
