<script setup lang="ts">
defineProps<{
  labelfor: string;
}>();
</script>

<template>
  <div
    class="m-intro m-intro-static-image"
    style="background-color: var(--color-neutrals-blue-xlight)"
  >
    <div class="container">
      <div class="muc-intro-content padded-intro">
        <h1 class="m-intro-vertical__title">KI-Suche</h1>

        <div class="m-intro-vertical__content">
          <div
            class="intro-info"
            :for="labelfor"
          >
            <p>
              Stellen Sie Ihre Frage zu städtischen Leistungen & Angeboten an
              unsere Künstliche Intelligenz! Bitte geben Sie dabei keine
              personenbezogenen Daten gemäß Datenschutzgrundverordnung (DSGVO)
              an.
            </p>
            <div style="margin-bottom: 24px"></div>
            <slot></slot>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.padded-intro {
  padding-left: 20%;
  padding-right: 20%;
}

@media screen and (max-width: 768px) {
  .padded-intro {
    padding-left: 0;
    padding-right: 0;
  }
}

.intro-info {
  font-size: 16px;
  font-weight: 400;
  padding-bottom: 48px;
  line-height: 24px;
  word-wrap: break-word;
}

.intro-highlight {
  font-weight: 700;
}

.m-intro-static-image {
  padding-bottom: 0;
  margin-bottom: 0;
  padding-top: 0;
}
</style>
