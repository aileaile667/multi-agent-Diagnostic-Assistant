<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RefreshCw } from "lucide-vue-next";
import { health } from "@/api/clinicalApi";
import JsonPreview from "@/components/JsonPreview.vue";
import type { HealthResponse } from "@/types/clinical";

const response = ref<HealthResponse | null>(null);
const error = ref("");
const isLoading = ref(false);

async function refresh() {
  isLoading.value = true;
  error.value = "";
  try {
    response.value = await health();
  } catch (err) {
    response.value = null;
    error.value = err instanceof Error ? err.message : "Health check failed.";
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  void refresh();
});
</script>

<template>
  <section class="health-grid">
    <div class="panel">
      <div class="panel-header">
        <div>
          <h2>Backend health</h2>
          <p class="muted">Checks the FastAPI `/health` endpoint.</p>
        </div>
        <button class="button" type="button" :disabled="isLoading" @click="refresh">
          <RefreshCw :size="17" />
          Refresh
        </button>
      </div>
      <div class="panel-body">
        <div v-if="response" class="kv-grid">
          <div class="kv">
            <span>Status</span>
            <strong>{{ response.status }}</strong>
          </div>
          <div class="kv">
            <span>Service</span>
            <strong>{{ response.service }}</strong>
          </div>
          <div class="kv">
            <span>Version</span>
            <strong>{{ response.version }}</strong>
          </div>
        </div>
        <div v-else-if="error" class="alert">{{ error }}</div>
        <p v-else class="empty-state">Checking backend status.</p>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">
        <h2>Raw response</h2>
      </div>
      <div class="panel-body">
        <JsonPreview :value="response || { error }" />
      </div>
    </div>
  </section>
</template>
