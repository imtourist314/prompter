<template>
  <div class="app-shell">
    <header class="app-header">
      <div>
        <h1>Prompter</h1>
        <p>Author instructions, preview them live, and publish via AgentAPI.</p>
      </div>
      <div class="header-controls">
        <button
          type="button"
          class="theme-toggle"
          @click="toggleTheme"
          :aria-pressed="!isDarkMode"
          :aria-label="isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'"
        >
          <span class="theme-icon" aria-hidden="true">
            {{ isDarkMode ? '🌙' : '☀️' }}
          </span>
        </button>
        <ProjectAreaSelector
          :projects="projects"
          :areas="areas"
          :selected-project="selectedProject"
          :selected-area="selectedArea"
          @update:project="(value) => (selectedProject = value)"
          @update:area="(value) => (selectedArea = value)"
        />
        <div class="inline-errors">
          <span v-if="errors.projects">{{ errors.projects }}</span>
          <span v-else-if="errors.areas">{{ errors.areas }}</span>
        </div>
      </div>
    </header>

    <section class="main-pane">
      <div class="component-bar">
        <div class="tabs-wrapper">
          <ComponentTabs
            v-if="components.length"
            :components="components"
            :active-component="activeComponent"
            @update:active-component="(value) => (activeComponent = value)"
          />
          <p v-else class="placeholder">Select a project and area to load components.</p>
        </div>
        <div class="action-buttons">
          <button type="button" class="ghost" @click="handleCancel" :disabled="!activeComponent || loading.submitting">
            Cancel
          </button>
          <button
            type="button"
            class="primary"
            @click="handleSubmit"
            :disabled="!canSubmit || loading.submitting"
          >
            {{ loading.submitting ? 'Submitting…' : 'Submit' }}
          </button>
        </div>
      </div>
      <p v-if="errors.components" class="inline-errors">{{ errors.components }}</p>
      <p v-if="errors.submit" class="inline-errors">{{ errors.submit }}</p>

      <InstructionEditor
        v-if="activeComponent"
        v-model="activeDraft"
        :preview-html="previewHtml"
        :preview-enabled="previewEnabled"
        @toggle-preview="togglePreview"
      />
      <div v-else class="empty-state">
        <p>Choose a component tab to start drafting instructions.</p>
      </div>
    </section>

    <StatusTable
      :files="files"
      :loading="loading.files"
      :error="errors.files"
      @refresh="fetchFiles"
      @view-file="handleFileView"
    />

    <div
      v-if="selectedFile"
      class="modal-backdrop"
      role="dialog"
      aria-modal="true"
      @click.self="closeFileDialog"
    >
      <div class="modal-dialog">
        <div class="modal-header">
          <h3>{{ selectedFile.file_name }}</h3>
        </div>
        <div class="modal-body">
          <pre>{{ selectedFile.content || 'No content available.' }}</pre>
        </div>
        <div class="modal-footer">
          <button type="button" class="primary" @click="closeFileDialog">OK</button>
        </div>
      </div>
    </div>

    <div v-if="toastMessage" class="toast">{{ toastMessage }}</div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue';
import DOMPurify from 'dompurify';
import { marked } from 'marked';

import { AgentApi } from './api/agentApi';
import ProjectAreaSelector from './components/ProjectAreaSelector.vue';
import ComponentTabs from './components/ComponentTabs.vue';
import InstructionEditor from './components/InstructionEditor.vue';
import StatusTable from './components/StatusTable.vue';

marked.setOptions({
  breaks: true,
  gfm: true,
});

const searchParams = new URLSearchParams(window.location.search);
const initialSelections = {
  project:
    searchParams.get('project') ||
    import.meta.env.VITE_PROMPTER_PROJECT ||
    import.meta.env.VITE_PROJECT_NAME ||
    '',
  area: searchParams.get('area') || '',
  component: searchParams.get('component') || '',
};

const projects = ref([]);
const areas = ref([]);
const components = ref([]);
const files = ref([]);
const selectedFile = ref(null);

const selectedProject = ref('');
const selectedArea = ref('');
const activeComponent = ref('');

const componentDrafts = ref({});
const lastSubmitted = ref({});
const previewEnabled = ref(true);

const THEME_STORAGE_KEY = 'prompter-theme';
const isDarkMode = ref(true);

const loading = reactive({
  projects: false,
  areas: false,
  components: false,
  submitting: false,
  files: false,
});

const errors = reactive({
  projects: '',
  areas: '',
  components: '',
  submit: '',
  files: '',
});

const toastMessage = ref('');
let toastTimer;

const hasHydratedProject = ref(false);
const hasHydratedArea = ref(false);
const hasHydratedComponent = ref(false);

const activeDraft = computed({
  get() {
    return componentDrafts.value[activeComponent.value] ?? '';
  },
  set(value) {
    if (!activeComponent.value) return;
    componentDrafts.value = {
      ...componentDrafts.value,
      [activeComponent.value]: value,
    };
  },
});

const previewHtml = computed(() => {
  const raw = activeDraft.value || '';
  const html = marked.parse(raw || '');
  return DOMPurify.sanitize(html);
});

const canSubmit = computed(() => {
  if (!selectedProject.value || !selectedArea.value || !activeComponent.value) return false;
  return Boolean(activeDraft.value.trim().length && !loading.submitting);
});

const togglePreview = () => {
  previewEnabled.value = !previewEnabled.value;
};

const applyTheme = (mode) => {
  if (typeof document === 'undefined') return;
  document.documentElement.setAttribute('data-theme', mode);
};

const persistTheme = (mode) => {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage?.setItem(THEME_STORAGE_KEY, mode);
  } catch {
    // Ignore persistence errors (e.g., storage disabled)
  }
};

const initializeTheme = () => {
  if (typeof window === 'undefined') return;
  let mode = window.localStorage?.getItem(THEME_STORAGE_KEY);
  if (mode !== 'light' && mode !== 'dark') {
    const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches;
    mode = prefersDark ? 'dark' : 'light';
  }
  isDarkMode.value = mode === 'dark';
  applyTheme(mode);
  persistTheme(mode);
};

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value;
};

const buildUiFilename = () => {
  const now = new Date();
  const pad = (value) => String(value).padStart(2, '0');
  const datePart = [now.getFullYear(), pad(now.getMonth() + 1), pad(now.getDate())].join('');
  const timePart = [pad(now.getHours()), pad(now.getMinutes()), pad(now.getSeconds())].join('');
  return `prompter_${datePart}_${timePart}`;
};

const resolveComponentValue = (component) => {
  if (component === null || component === undefined) return '';
  if (typeof component === 'string' || typeof component === 'number') return String(component);
  if (typeof component === 'object') {
    return (
      component.value ??
      component.component ??
      component.component_name ??
      component.componentName ??
      component.slug ??
      component.key ??
      component.name ??
      component.id ??
      component.code ??
      ''
    );
  }
  return '';
};

const resolveComponentLabel = (component, fallback = '') => {
  if (component === null || component === undefined) return fallback;
  if (typeof component === 'string' || typeof component === 'number') return String(component);
  if (typeof component === 'object') {
    return (
      component.label ??
      component.display_name ??
      component.displayName ??
      component.title ??
      component.name ??
      component.component ??
      component.component_name ??
      component.value ??
      fallback
    );
  }
  return fallback;
};

const normalizeComponentOptions = (items) => {
  const seen = new Set();
  return items
    .map((item, index) => {
      const value = resolveComponentValue(item);
      const label = resolveComponentLabel(item, value);
      if (!value && !label) return null;
      const safeValue = value || label || `component-${index + 1}`;
      const safeLabel = label || value || `Component ${index + 1}`;
      return {
        value: safeValue,
        label: safeLabel,
      };
    })
    .filter((option) => {
      if (!option) return false;
      if (seen.has(option.value)) return false;
      seen.add(option.value);
      return true;
    });
};

const ensureDraftSlot = (componentName) => {
  if (componentName && componentDrafts.value[componentName] === undefined) {
    componentDrafts.value = {
      ...componentDrafts.value,
      [componentName]: '',
    };
  }
  if (componentName && lastSubmitted.value[componentName] === undefined) {
    lastSubmitted.value = {
      ...lastSubmitted.value,
      [componentName]: '',
    };
  }
};

const showToast = (message) => {
  toastMessage.value = message;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toastMessage.value = '';
  }, 3500);
};

const loadProjects = async () => {
  loading.projects = true;
  errors.projects = '';
  try {
    const data = await AgentApi.getProjects();
    projects.value = data;
    if (!data.length) {
      selectedProject.value = '';
      return;
    }
    let nextProject = selectedProject.value && data.includes(selectedProject.value) ? selectedProject.value : '';
    if (!nextProject) {
      const preferred = initialSelections.project;
      if (!hasHydratedProject.value && preferred && data.includes(preferred)) {
        nextProject = preferred;
      } else {
        nextProject = data[0];
      }
    }
    hasHydratedProject.value = true;
    if (nextProject !== selectedProject.value) {
      selectedProject.value = nextProject;
    }
  } catch (error) {
    errors.projects = error.message;
    projects.value = [];
  } finally {
    loading.projects = false;
  }
};

const loadAreas = async () => {
  if (!selectedProject.value) {
    areas.value = [];
    selectedArea.value = '';
    return;
  }
  loading.areas = true;
  errors.areas = '';
  try {
    const data = await AgentApi.getAreas(selectedProject.value);
    areas.value = data;
    if (!data.length) {
      selectedArea.value = '';
      return;
    }
    let nextArea = selectedArea.value && data.includes(selectedArea.value) ? selectedArea.value : '';
    if (!nextArea) {
      const preferred = initialSelections.area;
      if (!hasHydratedArea.value && preferred && data.includes(preferred)) {
        nextArea = preferred;
      } else {
        nextArea = data[0];
      }
    }
    hasHydratedArea.value = true;
    if (nextArea !== selectedArea.value) {
      selectedArea.value = nextArea;
    }
  } catch (error) {
    errors.areas = error.message;
    areas.value = [];
    selectedArea.value = '';
  } finally {
    loading.areas = false;
  }
};

const loadComponents = async () => {
  if (!selectedProject.value || !selectedArea.value) {
    components.value = [];
    activeComponent.value = '';
    return;
  }
  loading.components = true;
  errors.components = '';
  try {
    const data = await AgentApi.getComponents(selectedProject.value, selectedArea.value);
    const normalized = normalizeComponentOptions(data);
    components.value = normalized;
    normalized.forEach((option) => ensureDraftSlot(option.value));
    if (!normalized.length) {
      activeComponent.value = '';
      return;
    }
    const availableValues = normalized.map((option) => option.value);
    let nextComponent =
      activeComponent.value && availableValues.includes(activeComponent.value) ? activeComponent.value : '';
    if (!nextComponent) {
      const preferred = initialSelections.component;
      if (!hasHydratedComponent.value && preferred && availableValues.includes(preferred)) {
        nextComponent = preferred;
      } else {
        nextComponent = availableValues[0];
      }
    }
    hasHydratedComponent.value = true;
    if (nextComponent !== activeComponent.value) {
      activeComponent.value = nextComponent;
    }
  } catch (error) {
    errors.components = error.message;
    components.value = [];
    activeComponent.value = '';
  } finally {
    loading.components = false;
  }
};

const fetchFiles = async () => {
  if (!selectedProject.value || !selectedArea.value) {
    files.value = [];
    return;
  }
  loading.files = true;
  errors.files = '';
  try {
    files.value = await AgentApi.listFiles({ project: selectedProject.value, area: selectedArea.value, limit: 100 });
  } catch (error) {
    errors.files = error.message;
    files.value = [];
  } finally {
    loading.files = false;
  }
};

const handleFileView = (file) => {
  selectedFile.value = file;
};

const closeFileDialog = () => {
  selectedFile.value = null;
};

const handleSubmit = async () => {
  if (!canSubmit.value) return;
  errors.submit = '';
  loading.submitting = true;
  try {
    const payload = {
      file_name: buildUiFilename(),
      project: selectedProject.value,
      area: selectedArea.value,
      component: activeComponent.value,
      description: `Prompter submission for ${selectedProject.value}/${selectedArea.value}/${activeComponent.value}`,
      content: activeDraft.value,
    };
    await AgentApi.publishFile(payload);
    lastSubmitted.value = {
      ...lastSubmitted.value,
      [activeComponent.value]: activeDraft.value,
    };
    showToast('Submission sent to AgentAPI.');
    fetchFiles();
  } catch (error) {
    errors.submit = error.message;
  } finally {
    loading.submitting = false;
  }
};

const handleCancel = () => {
  if (!activeComponent.value) return;
  const fallback = lastSubmitted.value[activeComponent.value] ?? '';
  activeDraft.value = fallback;
  showToast('Editor reset to last submitted content.');
};

watch(isDarkMode, (value) => {
  const mode = value ? 'dark' : 'light';
  applyTheme(mode);
  persistTheme(mode);
});

watch(selectedProject, () => {
  loadAreas();
});

watch(selectedArea, () => {
  loadComponents();
});

watch(
  () => [selectedProject.value, selectedArea.value],
  ([project, area]) => {
    if (project && area) {
      fetchFiles();
    } else {
      files.value = [];
    }
  }
);

onMounted(() => {
  initializeTheme();
  loadProjects();
});

onBeforeUnmount(() => {
  clearTimeout(toastTimer);
});
</script>

<style scoped>
.app-shell {
  padding: 2rem clamp(1.5rem, 4vw, 3rem) 4rem;
  color: var(--color-text);
  max-width: 1825px;
  margin: 0 auto;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.app-header h1 {
  margin: 0;
  font-size: 2rem;
}

.app-header p {
  margin-top: 0.35rem;
  color: var(--color-text-secondary);
}

.header-controls {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  align-items: flex-end;
}

.theme-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-border-subtle);
  background: transparent;
  color: var(--color-text);
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 999px;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
}

.theme-toggle:hover,
.theme-toggle:focus-visible {
  background: var(--color-tab-hover-bg);
}

.theme-icon {
  font-size: 1.3rem;
  line-height: 1;
}

.main-pane {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  padding: 1.5rem;
}

.component-bar {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
}

.tabs-wrapper {
  flex: 1;
}

.placeholder {
  color: var(--color-text-muted);
  margin: 0;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
}

button.primary {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 0.75rem;
  font-weight: 600;
}

button.ghost {
  background: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border-subtle);
  padding: 0.5rem 1.25rem;
  border-radius: 0.75rem;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.inline-errors {
  color: #f87171;
  margin: 0.5rem 0;
  font-size: 0.85rem;
}

.empty-state {
  border: 1px dashed var(--color-border);
  border-radius: 0.75rem;
  padding: 2rem;
  text-align: center;
  color: var(--color-text-muted);
}

.toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  background: var(--color-toast-bg);
  padding: 0.85rem 1.25rem;
  border-radius: 0.75rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  z-index: 1000;
}

.modal-dialog {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.85rem;
  width: min(90vw, 640px);
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
}

.modal-header {
  padding: 1.25rem 1.5rem 0.5rem;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.2rem;
}

.modal-body {
  padding: 0.5rem 1.5rem 1rem;
  flex: 1;
  overflow: auto;
}

.modal-body pre {
  margin: 0;
  background: var(--color-input-bg);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  padding: 1rem;
  color: var(--color-text);
  max-height: 100%;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.modal-footer {
  padding: 0 1.5rem 1.5rem;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 900px) {
  .app-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-controls {
    align-items: flex-start;
  }

  .component-bar {
    flex-direction: column;
    align-items: flex-start;
  }

  .action-buttons {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
