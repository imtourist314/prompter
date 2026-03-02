<template>
  <div class="app">
    <header class="header">
      <h1>Prompter</h1>
      <p class="subtitle">Edit and persist instruction markdown locally per tab.</p>
    </header>

    <nav class="tabs" role="tablist">
      <button
        v-for="a in areas"
        :key="a.key"
        class="tab"
        :class="{ active: a.key === activeArea }"
        role="tab"
        :aria-selected="a.key === activeArea"
        @click="activeArea = a.key"
      >
        {{ a.label }}
      </button>
    </nav>

    <main class="main">
      <TabEditor :area="activeArea" />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import TabEditor from './components/TabEditor.vue'

const areas = [
  { key: 'front-end', label: 'Front-end development' },
  { key: 'back-end', label: 'Back-end development' },
  { key: 'testing', label: 'Testing development' }
]

const activeArea = ref('front-end')
</script>

<style>
:root {
  --bg: #0b1020;
  --panel: #111a33;
  --panel2: #0f1730;
  --text: #e7ecff;
  --muted: rgba(231, 236, 255, 0.7);
  --border: rgba(231, 236, 255, 0.14);
  --accent: #7aa2ff;
  --danger: #ff6b6b;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji";
  background: radial-gradient(1000px 600px at 10% 0%, #14204b, var(--bg));
  color: var(--text);
}

.app {
  width: 100%;
  max-width: none;
  margin: 0;
  padding: 0;
}

.header { margin-bottom: 16px; }
.header h1 { margin: 0 0 4px; font-size: 22px; }
.subtitle { margin: 0; color: var(--muted); font-size: 13px; }

.tabs {
  display: flex;
  gap: 8px;
  padding: 8px;
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border);
  border-radius: 10px;
  margin-bottom: 16px;
}

.tab {
  appearance: none;
  border: 1px solid var(--border);
  background: var(--panel2);
  color: var(--text);
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
}
.tab.active {
  border-color: rgba(122, 162, 255, 0.65);
  box-shadow: 0 0 0 2px rgba(122, 162, 255, 0.18) inset;
}

.main {
  border: 1px solid var(--border);
  border-radius: 12px;
  background: rgba(255,255,255,0.03);
  padding: 16px;
}
</style>
