<template>
  <div class="app">
    <header class="header">
      <div class="headerTop">
        <div class="titleBlock">
          <h1>Prompter</h1>
          <p class="subtitle">Edit and persist instruction markdown locally per tab.</p>
        </div>

        <div class="projectControls">
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
import { onMounted, ref, watch } from 'vue'
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

.header {
  margin-bottom: 16px;
  padding: 12px 8px 0;
}

.headerTop {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.header h1 { margin: 0 0 4px; font-size: 22px; }
.subtitle { margin: 0; color: var(--muted); font-size: 13px; }

.projectControls {
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
}

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
  border: 1px solid rgba(122, 162, 255, 0.65);
  background: rgba(122, 162, 255, 0.12);
  border-radius: 12px;
  font-size: 14px;
}

.projectsError {
  margin: 10px 0 0;
  padding: 10px 12px;
  border: 1px solid rgba(255, 107, 107, 0.45);
  background: rgba(255, 107, 107, 0.08);
  border-radius: 10px;
  color: var(--muted);
  font-size: 13px;
}

.tabs {
  display: flex;
  gap: 8px;
  padding: 8px;
  background: rgba(255,255,255,0.04);
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
  margin: 0 8px 16px;
}
</style>
