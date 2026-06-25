<script setup lang="ts">
defineProps<{
  value: unknown;
}>();
</script>

<template>
  <pre class="json-block">{{ JSON.stringify(value, null, 2) }}</pre>
</template>
