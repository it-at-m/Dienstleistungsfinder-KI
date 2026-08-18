<script setup lang="ts">
import dlfExampleListItem from "@/components/dlf-example-list-item.vue";

defineProps<{
  examples: string[];
  submitQuery: (query: string) => void;
}>();
</script>

<template>
  <div class="m-component example-list-container">
    <div class="m-component__grid">
      <h2 class="m-component__title">Häufige Fragen an die KI:</h2>
      <div class="m-component__summary list-body">
        <ul class="m-linklist__list">
          <dlf-example-list-item
            v-for="query in examples"
            :key="query"
            :content="query"
            :submit-query="submitQuery"
          ></dlf-example-list-item>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.example-list-container {
  padding-left: 3%;
  padding-right: 3%;
  padding-top: 0;
  padding-bottom: 0;
}
.list-body {
  width: 100%;
}
</style>
