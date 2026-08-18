import { defineCustomElement } from "vue";

import DLFSearchVueComponent from "@/dlf-search-webcomponent.ce.vue";

// convert into custom element constructor
const DlfSearchWebcomponent = defineCustomElement(DLFSearchVueComponent);

// register
customElements.define("dlf-search-webcomponent", DlfSearchWebcomponent);
