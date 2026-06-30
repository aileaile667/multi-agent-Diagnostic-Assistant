<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";
import {
  Activity,
  FileHeart,
  HeartPulse,
  Pill,
  Search,
  Server,
} from "lucide-vue-next";
import { health } from "@/api/clinicalApi";
import type { HealthResponse } from "@/types/clinical";

const route = useRoute();
const healthState = ref<HealthResponse | null>(null);
const healthError = ref("");

const navItems = [
  { to: "/analysis", label: "病例分析", icon: FileHeart },
  { to: "/icd10", label: "ICD-10 编码", icon: Search },
  { to: "/ddi", label: "药物交互", icon: Pill },
  { to: "/health", label: "服务状态", icon: Activity },
];

const routeTitle = computed(() => {
  const item = navItems.find((nav) => nav.to === route.path);
  return item?.label ?? "病例分析";
});

const healthLabel = computed(() => {
  if (healthState.value?.status === "healthy") {
    return "服务正常";
  }
  return healthState.value?.status || healthError.value || "检查中";
});

async function refreshHealth() {
  try {
    healthError.value = "";
    healthState.value = await health();
  } catch (error) {
    healthState.value = null;
    healthError.value = error instanceof Error ? error.message : "离线";
  }
}

onMounted(() => {
  void refreshHealth();
});
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar" aria-label="主导航">
      <div class="brand">
        <div class="brand-mark">
          <HeartPulse :size="22" />
        </div>
        <div>
          <strong>临床智能体</strong>
          <span>临床决策工作台</span>
        </div>
      </div>

      <nav class="nav-list">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          class="nav-item"
          :class="{ active: route.path === item.to }"
          :to="item.to"
        >
          <component :is="item.icon" :size="18" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>
    </aside>

    <main class="main-shell">
      <header class="topbar">
        <div>
          <p class="eyebrow">Python FastAPI 演示</p>
          <h1>{{ routeTitle }}</h1>
        </div>
        <button class="status-pill" type="button" @click="refreshHealth">
          <Server :size="16" />
          <span
            class="status-dot"
            :class="{ online: healthState?.status === 'healthy' }"
          ></span>
          {{ healthLabel }}
        </button>
      </header>

      <RouterView />
    </main>
  </div>
</template>
