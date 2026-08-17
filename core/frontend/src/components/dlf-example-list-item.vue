<script setup lang="ts">
defineProps<{
  content: string;
  submitQuery: (query: string) => void;
}>();
</script>

<template>
  <li class="m-linklist__list__item">
    <a
      class="m-linklist-element m-linklist-element--download"
      href="#"
      @click.prevent="submitQuery(content)"
    >
      <div class="m-linklist-element__meta">
        <span class="m-linklist-element__title">{{ content }}</span>
      </div>
      <svg
        aria-hidden="true"
        class="icon"
      >
        <use xlink:href="#icon-search"></use>
      </svg>
    </a>
  </li>
</template>
