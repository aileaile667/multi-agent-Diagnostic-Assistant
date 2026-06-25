import { createRouter, createWebHistory } from "vue-router";
import AnalysisView from "@/views/AnalysisView.vue";
import DDIView from "@/views/DDIView.vue";
import HealthView from "@/views/HealthView.vue";
import ICD10View from "@/views/ICD10View.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/analysis" },
    { path: "/analysis", name: "analysis", component: AnalysisView },
    { path: "/icd10", name: "icd10", component: ICD10View },
    { path: "/ddi", name: "ddi", component: DDIView },
    { path: "/health", name: "health", component: HealthView },
  ],
});

export default router;
