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
  { to: "/analysis", label: "Analysis", icon: FileHeart },
  { to: "/icd10", label: "ICD-10", icon: Search },
  { to: "/ddi", label: "DDI", icon: Pill },
  { to: "/health", label: "Health", icon: Activity },
];

const routeTitle = computed(() => {
  const item = navItems.find((nav) => nav.to === route.path);
  return item?.label ?? "Analysis";
});

async function refreshHealth() {
  try {
    healthError.value = "";
    healthState.value = await health();
  } catch (error) {
    healthState.value = null;
    healthError.value = error instanceof Error ? error.message : "Offline";
  }
}

onMounted(() => {
  void refreshHealth();
});
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar" aria-label="Primary navigation">
      <div class="brand">
        <div class="brand-mark">
          <HeartPulse :size="22" />
        </div>
        <div>
          <strong>Clinical Agents</strong>
          <span>Decision workbench</span>
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
          <p class="eyebrow">Python FastAPI demo</p>
          <h1>{{ routeTitle }}</h1>
        </div>
        <button class="status-pill" type="button" @click="refreshHealth">
          <Server :size="16" />
          <span
            class="status-dot"
            :class="{ online: healthState?.status === 'healthy' }"
          ></span>
          {{ healthState?.status || healthError || "Checking" }}
        </button>
      </header>

      <RouterView />
    </main>
  </div>
</template>
