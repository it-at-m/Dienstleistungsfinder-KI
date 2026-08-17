import js from "@eslint/js";
import vuePrettierEslintConfigSkipFormatting from "@vue/eslint-config-prettier/skip-formatting";
import vueTsEslintConfig from "@vue/eslint-config-typescript";
import { ESLint } from "eslint";
import vueEslintConfig from "eslint-plugin-vue";

export default [
  ...ESLint.defaultConfig,
  js.configs.recommended,
  ...vueEslintConfig.configs["flat/recommended"],
  ...vueTsEslintConfig({
    extends: ["strict", "stylistic"],
  }),
  vuePrettierEslintConfigSkipFormatting,
  {
    ignores: [
      "dist",
      "target",
      "node_modules",
      "env.d.ts",
      "processes/**",
      "scripts/**",
    ],
  },
  {
    rules: {
      "no-console": "off",
      "no-undef": "off",
      "no-useless-assignment": "off",
      "@typescript-eslint/no-explicit-any": "off",
      "@typescript-eslint/no-extraneous-class": "off",
      "@typescript-eslint/no-invalid-void-type": "off",
      "@typescript-eslint/no-non-null-assertion": "off",
      "@typescript-eslint/no-unused-vars": "off",
      "@typescript-eslint/unified-signatures": "off",
      "vue/component-name-in-template-casing": [
        "error",
        "kebab-case",
        { registeredComponentsOnly: false },
      ],
    },
  },
];
