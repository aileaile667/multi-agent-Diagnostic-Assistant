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
    error.value = err instanceof Error ? err.message : "Search failed.";
  } finally {
    isLoading.value = false;
  }
}

async function selectCode(code: string) {
  error.value = "";
  try {
    selected.value = await getICD10(code);
  } catch (err) {
    error.value = err instanceof Error ? err.message : "Lookup failed.";
  }
}
</script>

<template>
  <section class="tool-grid">
    <div class="panel">
      <div class="panel-header">
        <h2>ICD-10 search</h2>
      </div>
      <div class="panel-body form-grid">
        <div class="field">
          <label for="icd-query">Diagnosis text</label>
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
          {{ isLoading ? "Searching" : "Search codes" }}
        </button>
        <div v-if="error" class="alert">{{ error }}</div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">
        <h2>Matches</h2>
      </div>
      <div class="panel-body">
        <div v-if="results.length" class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Code</th>
                <th>Description</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="result in results" :key="result.code">
                <td><strong>{{ result.code }}</strong></td>
                <td>{{ result.description }}</td>
                <td>
                  <button class="button" type="button" @click="selectCode(result.code)">
                    Detail
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="empty-state">Search results will appear here.</p>
      </div>
    </div>

    <div v-if="selected" class="panel">
      <div class="panel-header">
        <h2>Code detail</h2>
      </div>
      <div class="panel-body kv-grid">
        <div class="kv">
          <span>ICD-10</span>
          <strong>{{ selected.icd10.code }}</strong>
        </div>
        <div class="kv">
          <span>DRG</span>
          <strong>{{ selected.drg_group?.drg_code || "Not available" }}</strong>
        </div>
        <div class="kv">
          <span>Description</span>
          <strong>{{ selected.icd10.description }}</strong>
        </div>
        <div class="kv">
          <span>DRG description</span>
          <strong>{{ selected.drg_group?.description || "Not available" }}</strong>
        </div>
      </div>
    </div>
  </section>
</template>
