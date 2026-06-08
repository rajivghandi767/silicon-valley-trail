import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";
import eslintReact from "@eslint-react/eslint-plugin";

export default tseslint.config(
  {
    ignores: [
      "dist",
      "src/test/**/*",
      "src/**/*.test.ts",
      "src/**/*.test.tsx",
      "src/**/*.spec.ts",
      "src/**/*.spec.tsx"
    ]
  },
  {
    extends: [
      js.configs.recommended,
      ...tseslint.configs.recommendedTypeChecked,
      ...tseslint.configs.stylisticTypeChecked,
    ],
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parserOptions: {
        project: ["./tsconfig.node.json", "./tsconfig.app.json"],
        tsconfigRootDir: import.meta.dirname,
      },
    },
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
      "@eslint-react": eslintReact,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true },
      ],
      ...eslintReact.configs.recommended.rules,
      
      // Relax rules for API payloads and any assignments
      "@typescript-eslint/no-unsafe-assignment": "off",
      "@typescript-eslint/no-unsafe-member-access": "off",
      "@typescript-eslint/no-unsafe-argument": "off",
      "@typescript-eslint/no-explicit-any": "off",
      "@typescript-eslint/no-floating-promises": "off",
      "@typescript-eslint/prefer-nullish-coalescing": "off",
      "@typescript-eslint/no-empty-function": "off",
      "@typescript-eslint/no-misused-promises": "off",
      "@eslint-react/set-state-in-effect": "off",
      "react-hooks/set-state-in-effect": "off",

      // Additional relaxations for upgrading existing codebase
      "@typescript-eslint/no-inferrable-types": "off",
      "@typescript-eslint/no-unnecessary-type-assertion": "off",
      "@typescript-eslint/non-nullable-type-assertion-style": "off",
      "@typescript-eslint/no-unused-vars": ["warn", { "argsIgnorePattern": "^_" }],
      "prefer-const": "off",
      "@eslint-react/no-nested-component-definitions": "off",
      "@eslint-react/static-components": "off",
      "@eslint-react/purity": "off",
      "@eslint-react/no-context-provider": "off",
      "@eslint-react/no-use-context": "off",
      "@typescript-eslint/prefer-for-of": "off"
    },
  }
);
