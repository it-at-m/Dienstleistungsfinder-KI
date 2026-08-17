<script setup lang="ts">
import type DLFAnswer from "@/types/DLFAnswer";
import type { RetrievedDocument } from "@/types/RetrievalResult";

import { ref } from "vue";

import dlfToggle from "@/components/common/dlf-toggle.vue";
import dlfDocumentView from "@/components/dlf-document-view.vue";

const show_original_sources = ref<boolean>(false);

defineProps<{
  documents: DLFAnswer[];
  loadingDocuments: RetrievedDocument[];
}>();
</script>

<template>
  <div>
    <div class="document-list-container">
      <div class="header">
        <h3 class="m-component__title">
          {{ documents.length }}
          {{ documents.length == 1 ? "Antwort" : "Antworten" }}:
        </h3>
        <div class="togglecontainer">
          <div
            :class="
              show_original_sources
                ? 'toggle-labels-left'
                : 'toggle-labels-left bluecolor'
            "
          >
            KI-generierte Antwort
          </div>
          <dlf-toggle
            v-model="show_original_sources"
            aria-label="Anzeige umschalten: KI-Antwort oder Originaltext"
            title="Anzeige umschalten: KI-Antwort oder Originaltext"
          ></dlf-toggle>
          <div
            :class="
              show_original_sources
                ? 'toggle-label-right bluecolor'
                : 'toggle-label-right'
            "
          >
            Orginaltext
          </div>
        </div>
      </div>
      <div class="m-listing__body">
        <ul class="m-listing__list">
          <template
            v-for="(document, index) in documents"
            :key="document.doc_url"
          >
            <li
              :aria-label="index + 1 + '. Dokument: ' + document.doc_base_name"
              :class="[
                'm-listing__list-item document-container',
                index === documents.length - 1 ? 'last-document' : '',
              ]"
            >
              <dlf-document-view
                :dlf-doc="document"
                header-prefix=""
                :show-orginal-text="show_original_sources"
              />
            </li>
          </template>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.document-list-container {
  list-style: none;
  padding-left: 2.5%;
  padding-right: 2%;
}

ul {
  list-style-type: none;
  display: contents;
}

ul > li {
  padding: 0;
  margin: 0;
}

.bluecolor {
  color: var(--color-brand-main-blue);
}

.header {
  display: flex;
  justify-content: space-between;
  flex-direction: row;
  width: 100%;
}

.togglecontainer {
  display: flex;
  justify-content: center;
  flex-direction: row;
  align-items: start;
}

.toggle-labels-left {
  padding-right: 10px;
  padding-top: 5px;
}

.toggle-label-right {
  padding-left: 10px;
  padding-top: 5px;
}

@media screen and (max-width: 768px) {
  .togglecontainer {
    flex-direction: row;
    margin-bottom: 32px;
    justify-content: start;
  }

  .header {
    flex-direction: column;
  }
}

.document-container {
  margin-bottom: 32px;
  padding-bottom: 32px;
  border-bottom: 1px solid #e5eef5;
  padding-left: 2.5%;
  padding-right: 2%;
}

.last-document {
  margin-bottom: 0px;
  padding-bottom: 32px;
  border-bottom: 1px solid #e5eef5;
  padding-left: 2.5%;
  padding-right: 2%;
}
</style>
