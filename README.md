
# Programming Language: JavaScript/TypeScript 

Requires using npm to set up the ecosystem, rather than venv (since we're not using python)

# Framework

CSS (UI) Framework (toolkit or a collection of pre-built tools) —> Bootstrap (Not using Tailwind CSS) [.css]

JS Framework/library (Renders UI and manages state) —> React [.ts]

    Note: React generates the HTML via [.tsx] or [.jsx] as well

# Installation

The actual Vite/npm project (`package.json`, `node_modules`, `src/`, `public/`) lives in the [app/](./app) subfolder — this README stays at the project root. Config files (`vite.config.ts`, `eslint.config.js`, `tsconfig*.json`) are further split out into [app/config/](./app/config) to keep `app/`'s top level clean; the npm scripts in `package.json` already point at them, so day-to-day usage below is unaffected. Steps 2 onward assume you're inside `app/`.

1. Install Node.js (includes npm) — https://nodejs.org (LTS recommended)
   - Verify: `node -v` and `npm -v`

2. Scaffold the project into `app/`. Several tools provide HMR + React Fast Refresh out of the box — pick one:

   | Tool | Scaffold command | Notes |
   |---|---|---|
   | **Vite** (recommended) | `npm create vite@latest app -- --template react-ts` | Native ES modules + esbuild/Rollup; fastest, lowest-config |
   | webpack (Create React App) | `npx create-react-app app --template typescript` | Classic HMR via `webpack-dev-server`; CRA is largely unmaintained now |
   | Next.js | `npx create-next-app@latest app` | Built-in dev server (webpack or Turbopack) + routing/SSR features |
   | Parcel | `mkdir app && cd app && npm init -y && npm install parcel` (manual setup) | Zero-config bundler with HMR built in |
   | Expo (React Native) | `npx create-expo-app app` | For native apps; HMR via Metro bundler's Fast Refresh |

   This project uses **Vite**.

        Use ESLint for the linter. Currently, the Oxlint is a new version, which may not be mature enough. Oxlint is faster than ESlint, but it has less documentation to go off of.

        After scaffolding, the config files (`vite.config.ts`, `eslint.config.js`, `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json`) were moved into `app/config/`, with their internal relative paths (`src`, `node_modules`, `dist`) and the `package.json` scripts updated to still resolve correctly (e.g. `vite --config config/vite.config.ts`).

   For further details, refer to [Appendix](#appendix)

        Do not move package-lock.json, package.json, nor tsconfig.json anywhere. VS Code's Typescript server was implemented so that it had to autodiscover it by walking up the file you're editing, which would conflict with the import of bootstrap later on within the main.tsx file

3. `cd app` then install dependencies:
   npm install 

4. Add Bootstrap:
   npm install bootstrap react-bootstrap

        E.g., cd /Users/trinhpham/UtilityPrograms/FrontendMaker/app npm install bootstrap react-bootstrap

5. Import Bootstrap's CSS once in your entry point (e.g. src/main.tsx):
   import "bootstrap/dist/css/bootstrap.min.css";

6. Run the dev server (from inside `app/`):
   npm run dev

7. (If finished completely) Run the build (from inside `app/`; nothing to update, so it optimizes the dist folder for npm):
    npm run build

        Sanity check (before running it): npm run preview

# Appendix

**Why Vite?**

- **HMR (Hot Module Replacement):** A dev-server feature that only pushes the *changed* code into the running browser page instantly. It does not need a browser refresh to update it.
- **Native ES modules:** modern browsers can `import`/`export` modules directly. Vite does the same, meaning that you do not need to bundle (combine) the app's Components, Hooks, and APIs *upfront*  with the CSS and HTML files. This means you don't have to reupdate the other one once you changed your current one. 
- **esbuild:** a Go-based transpiler/bundler, which is often 10-100x faster than JS code, due to JS's dependency on an interpreter (instead of solely being a compiler). It allows the program to quickly pre-bundle (pre-combine) `node_modules` dependencies (the libraries the ecosystem needs).
- **Rollup:** a bundler known for strong **tree-shaking** (stripping unused code). Vite switches to Rollup only for `npm run build`, to produce the final optimized production bundle.

**Why not the alternatives:**

| Tool | Reason not chosen |
|---|---|
| webpack / Create React App | Re-bundles the whole app on every change (slower dev loop); CRA is officially deprecated by the React teaCannot find module or type declarations for side-effect import of 'bootstrap/dist/css/bootstrap.min.css'.ts(2882)m |
| Next.js | A full-stack application framework focus (routing, SSR, SEO), requiring  more complexity/conventions than what this project intends to experiment with |
| Parcel | Reasonable alternative, but with a smaller React/TS ecosystem and community than Vite today |
| Expo | For mobile apps (iOS/Android) via Metro — not applicable to a web frontend |

**Summary:** Vite gives the fastest, lowest-config dev loop (instant HMR) for a plain React + TypeScript web app, without taking on framework-level features (routing/SSR) this project doesn't need.




# ADDITIONAL INFORMATION ABOUT THE VITE PACKAGE BELOW
## React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

### React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

### Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])

```

You can also install [eslint-plugin-react-x](https://npmx.dev/package/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://npmx.dev/package/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])

```
