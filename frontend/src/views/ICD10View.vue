<script setup lang="ts">
import { ref } from "vue";
import { Search } from "lucide-vue-next";
import { getICD10, searchICD10 } from "@/api/clinicalApi";
import type { ICD10LookupResponse, ICD10SearchResult } from "@/types/clinical";

const query = ref("pneumonia");
const results = ref<ICD10SearchResult[]>([]);
const selected = ref<ICD10LookupResponse | null>(null);
const isLoading = ref(false);
const error = ref("");

async function runSearch() {
  if (query.value.trim().length < 2) {
    return;
  }

  isLoading.value = true;
  error.value = "";
  selected.value = null;
  try {
    const response = await searchICD10(query.value.trim());
    results.value = response.results;
  } catch (err) {
    error.value = err instanceof Error ? err.message : "搜索失败。";
  } finally {
    isLoading.value = false;
  }
}

async function selectCode(code: string) {
  error.value = "";
  try {
    selected.value = await getICD10(code);
  } catch (err) {
    error.value = err instanceof Error ? err.message : "编码查询失败。";
  }
}
</script>

<template>
  <section class="tool-grid">
    <div class="panel">
      <div class="panel-header">
        <h2>ICD-10 搜索</h2>
      </div>
      <div class="panel-body form-grid">
        <div class="field">
          <label for="icd-query">诊断文本</label>
          <input
            id="icd-query"
            v-model="query"
            class="input"
            placeholder="pneumonia"
            @keydown.enter="runSearch"
          />
        </div>
        <button class="button primary" type="button" :disabled="isLoading" @click="runSearch">
          <Search :size="17" />
          {{ isLoading ? "搜索中" : "搜索编码" }}
        </button>
        <div v-if="error" class="alert">{{ error }}</div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">
        <h2>匹配结果</h2>
      </div>
      <div class="panel-body">
        <div v-if="results.length" class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>编码</th>
                <th>描述</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="result in results" :key="result.code">
                <td><strong>{{ result.code }}</strong></td>
                <td>{{ result.description }}</td>
                <td>
                  <button class="button" type="button" @click="selectCode(result.code)">
                    详情
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="empty-state">搜索结果将在此显示。</p>
      </div>
    </div>

    <div v-if="selected" class="panel">
      <div class="panel-header">
        <h2>编码详情</h2>
      </div>
      <div class="panel-body kv-grid">
        <div class="kv">
          <span>ICD-10</span>
          <strong>{{ selected.icd10.code }}</strong>
        </div>
        <div class="kv">
          <span>DRG</span>
          <strong>{{ selected.drg_group?.drg_code || "暂无数据" }}</strong>
        </div>
        <div class="kv">
          <span>描述</span>
          <strong>{{ selected.icd10.description }}</strong>
        </div>
        <div class="kv">
          <span>DRG 描述</span>
          <strong>{{ selected.drg_group?.description || "暂无数据" }}</strong>
        </div>
      </div>
    </div>
  </section>
</template>
