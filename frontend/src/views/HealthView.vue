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
    error.value = err instanceof Error ? err.message : "健康检查失败。";
  } finally {
    isLoading.value = false;
  }
}

function statusText(status: string): string {
  return status === "healthy" ? "服务正常" : status;
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
          <h2>后端健康状态</h2>
          <p class="muted">检查 FastAPI `/health` 接口。</p>
        </div>
        <button class="button" type="button" :disabled="isLoading" @click="refresh">
          <RefreshCw :size="17" />
          刷新
        </button>
      </div>
      <div class="panel-body">
        <div v-if="response" class="kv-grid">
          <div class="kv">
            <span>状态</span>
            <strong>{{ statusText(response.status) }}</strong>
          </div>
          <div class="kv">
            <span>服务</span>
            <strong>{{ response.service }}</strong>
          </div>
          <div class="kv">
            <span>版本</span>
            <strong>{{ response.version }}</strong>
          </div>
        </div>
        <div v-else-if="error" class="alert">{{ error }}</div>
        <p v-else class="empty-state">正在检查后端状态。</p>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">
        <h2>原始响应</h2>
      </div>
      <div class="panel-body">
        <JsonPreview :value="response || { error }" />
      </div>
    </div>
  </section>
</template>
