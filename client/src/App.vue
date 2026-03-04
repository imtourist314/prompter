<template>
  <div class="app">
    <header class="header">
      <div class="headerTop">
        <div class="titleBlock">
          <h1>Prompter</h1>
          <p class="subtitle">Edit and persist instruction markdown locally per tab.</p>
        </div>

        <div class="projectControls">
          <button
            class="themeToggle"
            type="button"
            @click="toggleTheme"
            :aria-pressed="isDarkTheme"
            :aria-label="themeButtonAriaLabel"
            :title="themeButtonAriaLabel"
          >
            <span class="themeToggleIcon" aria-hidden="true">{{ themeIcon }}</span>
            <span class="themeToggleText">{{ themeButtonText }}</span>
          </button>

          <label class="projectSelect">
            <span class="projectSelectLabel">Project</span>
            <select v-model="selectedProject" :disabled="projectsLoading">
              <option v-for="p in projects" :key="p" :value="p">{{ p }}</option>
            </select>
          </label>
        </div>
      </div>

      <div class="projectBanner" aria-live="polite">
        Working on project: <strong>{{ selectedProject }}</strong>
      </div>

      <p v-if="projectsError" class="projectsError">{{ projectsError }}</p>
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
      <TabEditor :area="activeArea" :project="selectedProject" />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import TabEditor from './components/TabEditor.vue'
import { fetchProjects, getInitialProject } from './api'

const areas = [
  { key: 'front-end', label: 'Front-end development' },
  { key: 'back-end', label: 'Back-end development' },
  { key: 'testing', label: 'Testing development' }
]

const activeArea = ref('front-end')

function getStoredProject() {
  try {
    return localStorage.getItem('prompter.project') || ''
  } catch {
    return ''
  }
}

function setStoredProject(p) {
  try {
    localStorage.setItem('prompter.project', p)
  } catch {
    // ignore
  }
}

function urlHasProjectParam() {
  try {
    return Boolean(new URLSearchParams(window.location.search).get('project'))
  } catch {
    return false
  }
}

function setProjectInUrl(p) {
  try {
    const u = new URL(window.location.href)
    u.searchParams.set('project', p)
    window.history.replaceState({}, '', u.toString())
  } catch {
    // ignore
  }
}

const THEME_STORAGE_KEY = 'prompter.theme'
const DEFAULT_THEME = 'dark'

function detectInitialTheme() {
  if (typeof window === 'undefined') return DEFAULT_THEME
  try {
    const stored = localStorage.getItem(THEME_STORAGE_KEY)
    if (stored === 'light' || stored === 'dark') return stored
  } catch {
    // ignore
  }
  try {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  } catch {
    return DEFAULT_THEME
  }
}

function persistThemeSetting(value) {
  try {
    localStorage.setItem(THEME_STORAGE_KEY, value)
  } catch {
    // ignore
  }
}

function applyTheme(value) {
  if (typeof document === 'undefined') return
  document.documentElement.dataset.theme = value
}

const theme = ref(detectInitialTheme())
const isDarkTheme = computed(() => theme.value === 'dark')
const themeIcon = computed(() => (isDarkTheme.value ? '🌙' : '☀️'))
const themeButtonText = computed(() => (isDarkTheme.value ? 'Dark mode' : 'Light mode'))
const themeButtonAriaLabel = computed(() =>
  isDarkTheme.value ? 'Switch to light mode' : 'Switch to dark mode'
)

function toggleTheme() {
  theme.value = isDarkTheme.value ? 'light' : 'dark'
}

watch(
  theme,
  (value) => {
    const next = value === 'light' ? 'light' : 'dark'
    applyTheme(next)
    persistThemeSetting(next)
  },
  { immediate: true }
)

let initialProject = getInitialProject()
if (!urlHasProjectParam()) {
  const stored = getStoredProject().trim()
  if (stored) initialProject = stored
}

const selectedProject = ref(initialProject)
const projects = ref([selectedProject.value])
const projectsLoading = ref(false)
const projectsError = ref('')

onMounted(async () => {
  projectsLoading.value = true
  projectsError.value = ''
  try {
    const data = await fetchProjects()
    const list = Array.isArray(data?.projects) ? data.projects : []

    // Ensure we always have a non-empty list for the dropdown.
    const unique = Array.from(new Set([...list, selectedProject.value].filter(Boolean)))
    projects.value = unique

    if (list.length > 0 && !list.includes(selectedProject.value)) {
      const fallback = list.includes(data?.defaultProject) ? data.defaultProject : list[0]
      selectedProject.value = fallback
    }
  } catch (e) {
    projectsError.value = `Could not load project list from server. Using “${selectedProject.value}”.`
  } finally {
    projectsLoading.value = false
  }
})

watch(
  selectedProject,
  (p) => {
    const project = (p || '').trim() || 'default'
    if (project !== p) selectedProject.value = project

    setStoredProject(project)
    setProjectInUrl(project)

    // Keep dropdown options in sync if user types a project via URL.
    if (!projects.value.includes(project)) projects.value = [project, ...projects.value]
  },
  { immediate: true }
)
</script>

<style>
:root {
  color-scheme: dark;
  --bg: #141c32;
  --panel: #1d2644;
  --panel2: #202a4c;
  --text: #f4f6ff;
  --muted: rgba(244, 246, 255, 0.75);
  --border: rgba(244, 246, 255, 0.18);
  --accent: #8cb3ff;
  --danger: #ff8a8a;
  --success: #6ee7b7;
  --warning: #ffd766;
  --body-gradient-start: #2b3a67;
  --body-gradient-end: var(--bg);
  --surface-soft: rgba(255, 255, 255, 0.08);
  --surface-strong: rgba(255, 255, 255, 0.12);
  --panel-overlay: rgba(20, 24, 46, 0.85);
  --code-inline-bg: rgba(255, 255, 255, 0.14);
  --code-block-bg: rgba(10, 14, 32, 0.65);
  --banner-border: rgba(140, 179, 255, 0.6);
  --banner-bg: rgba(140, 179, 255, 0.18);
  --error-panel-border: rgba(255, 138, 138, 0.45);
  --error-panel-bg: rgba(255, 138, 138, 0.1);
  --status-border: rgba(140, 179, 255, 0.35);
  --status-bg: rgba(140, 179, 255, 0.12);
  --accent-border-strong: rgba(140, 179, 255, 0.65);
  --accent-soft-bg: rgba(140, 179, 255, 0.18);
  --btn-bg: var(--surface-soft);
  --btn-border: var(--border);
  --btn-danger-bg: rgba(255, 138, 138, 0.2);
  --btn-danger-border: rgba(255, 138, 138, 0.72);
  --btn-danger-bg-hover: rgba(255, 138, 138, 0.28);
  --btn-danger-border-hover: rgba(255, 138, 138, 0.92);
  --btn-primary-bg: rgba(110, 231, 183, 0.22);
  --btn-primary-border: rgba(110, 231, 183, 0.78);
  --btn-primary-bg-hover: rgba(110, 231, 183, 0.3);
  --btn-primary-border-hover: rgba(110, 231, 183, 0.95);
  --btn-attention-border: rgba(255, 215, 102, 0.95);
  --btn-attention-glow: rgba(255, 215, 102, 0.25);
}

:root[data-theme='light'] {
  color-scheme: light;
  --bg: #f6f8ff;
  --panel: #ffffff;
  --panel2: #f1f4ff;
  --text: #1d2340;
  --muted: rgba(29, 35, 64, 0.65);
  --border: rgba(29, 35, 64, 0.18);
  --accent: #3f5ceb;
  --danger: #c33434;
  --success: #2f9d59;
  --warning: #b17800;
  --body-gradient-start: #ffffff;
  --body-gradient-end: #e9efff;
  --surface-soft: rgba(0, 0, 0, 0.04);
  --surface-strong: rgba(0, 0, 0, 0.06);
  --panel-overlay: rgba(255, 255, 255, 0.9);
  --code-inline-bg: rgba(0, 0, 0, 0.04);
  --code-block-bg: rgba(0, 0, 0, 0.07);
  --banner-border: rgba(63, 92, 235, 0.35);
  --banner-bg: rgba(63, 92, 235, 0.12);
  --error-panel-border: rgba(195, 52, 52, 0.35);
  --error-panel-bg: rgba(195, 52, 52, 0.1);
  --status-border: rgba(63, 92, 235, 0.22);
  --status-bg: rgba(63, 92, 235, 0.1);
  --accent-border-strong: rgba(63, 92, 235, 0.55);
  --accent-soft-bg: rgba(63, 92, 235, 0.15);
  --btn-bg: var(--surface-soft);
  --btn-border: var(--border);
  --btn-danger-bg: rgba(195, 52, 52, 0.12);
  --btn-danger-border: rgba(195, 52, 52, 0.55);
  --btn-danger-bg-hover: rgba(195, 52, 52, 0.18);
  --btn-danger-border-hover: rgba(195, 52, 52, 0.7);
  --btn-primary-bg: rgba(47, 157, 89, 0.14);
  --btn-primary-border: rgba(47, 157, 89, 0.55);
  --btn-primary-bg-hover: rgba(47, 157, 89, 0.2);
  --btn-primary-border-hover: rgba(47, 157, 89, 0.75);
  --btn-attention-border: rgba(191, 140, 0, 0.9);
  --btn-attention-glow: rgba(191, 140, 0, 0.32);
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji";
  background: radial-gradient(1000px 600px at 10% 0%, var(--body-gradient-start), var(--body-gradient-end));
  background-color: var(--body-gradient-end);
  color: var(--text);
  min-height: 100vh;
  transition: background 0.3s ease, color 0.3s ease;
}

.app {
  width: 100%;
  max-width: none;
  margin: 0;
  padding: 0;
}

.header {
  margin-bottom: 16px;
  padding: 12px 8px 0;
}

.headerTop {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.header h1 { margin: 0 0 4px; font-size: 22px; }
.subtitle { margin: 0; color: var(--muted); font-size: 13px; }

.projectControls {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  flex-wrap: wrap;
}

.themeToggle {
  appearance: none;
  border: 1px solid var(--border);
  background: var(--panel2);
  color: var(--text);
  padding: 8px 14px;
  border-radius: 999px;
  font-size: 13px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: border-color 0.2s ease, background 0.2s ease;
}

.themeToggle:hover,
.themeToggle:focus-visible {
  border-color: var(--accent);
}

.themeToggle:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.themeToggleIcon { font-size: 16px; line-height: 1; }
.themeToggleText { font-weight: 600; }

.projectSelect {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12px;
  color: var(--muted);
}

.projectSelect select {
  appearance: none;
  border: 1px solid var(--border);
  background: var(--panel2);
  color: var(--text);
  padding: 10px 12px;
  border-radius: 10px;
  font-size: 13px;
  min-width: 220px;
}

.projectBanner {
  margin-top: 10px;
  padding: 10px 12px;
  border: 1px solid var(--banner-border);
  background: var(--banner-bg);
  border-radius: 12px;
  font-size: 14px;
}

.projectsError {
  margin: 10px 0 0;
  padding: 10px 12px;
  border: 1px solid var(--error-panel-border);
  background: var(--error-panel-bg);
  border-radius: 10px;
  color: var(--muted);
  font-size: 13px;
}

.tabs {
  display: flex;
  gap: 8px;
  padding: 8px;
  background: var(--surface-soft);
  border: 1px solid var(--border);
  border-radius: 10px;
  margin: 0 8px 16px;
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
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.tab.active {
  border-color: var(--accent-border-strong);
  box-shadow: 0 0 0 2px var(--accent-soft-bg) inset;
}

.main {
  border: 1px solid var(--border);
  border-radius: 12px;
  background: var(--surface-soft);
  padding: 16px;
  margin: 0 8px 16px;
}
</style>
