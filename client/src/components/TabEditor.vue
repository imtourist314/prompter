<template>
  <section class="tabEditor">
    <div class="topRow">
      <div class="areaTitle">
        <div class="label">Active tab</div>
        <div class="value">{{ area }}</div>
      </div>

      <div class="actions">
        <button class="btn danger" :disabled="loading" @click="reloadFromDisk">Cancel (reload)</button>
        <button class="btn" :disabled="loading" @click="markCompleted">Completed</button>
        <button
          class="btn primary"
          :class="{ attention: submitNeedsAttention }"
          :disabled="loading"
          @click="saveToDisk"
        >
          Submit (save)
        </button>
      </div>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="status" class="status">{{ status }}</p>

    <div class="grid">
      <MarkdownTextBox
        title="Current instructions (persisted as instructions.md)"
        v-model="currentInstructions"
      />

      <div class="completedBlock">
        <div class="completedHistory">
          <label class="completedHistoryLabel">
            <span>Completed history</span>
            <select
              v-model="selectedCompletedFile"
              :disabled="loading || completedFilesLoading"
              @change="onCompletedFileSelected"
            >
              <option value="">Load a previous snapshot…</option>
              <option value="__latest__">Latest (completed_instructions.md)</option>
              <option v-for="f in completedFiles" :key="f" :value="f">{{ formatCompletedFilename(f) }}</option>
            </select>
          </label>
          <button class="btn" :disabled="loading || completedFilesLoading" @click="reloadCompletedFiles">
            Refresh
          </button>
        </div>

        <MarkdownTextBox
          title="Completed/processed instructions (persisted as completed_instructions.md)"
          v-model="completedInstructions"
        />
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, watch } from 'vue'
import MarkdownTextBox from './MarkdownTextBox.vue'
import {
  fetchInstructionFile,
  saveInstructionFile,
  fetchCompletedInstructionFiles,
  fetchCompletedInstructionFile
} from '../api'

const props = defineProps({
  area: { type: String, required: true },
  project: { type: String, required: true }
})

const loading = ref(false)
const error = ref('')
const status = ref('')

const currentInstructions = ref('')
const completedInstructions = ref('')
const submitNeedsAttention = ref(false)

const completedFiles = ref([])
const completedFilesLoading = ref(false)
const selectedCompletedFile = ref('__latest__')

// Used to warn before loading a snapshot on top of unsaved edits.
const lastPersistedCurrent = ref('')
const lastPersistedCompleted = ref('')

function hasUnsavedChanges() {
  return (
    currentInstructions.value !== lastPersistedCurrent.value ||
    completedInstructions.value !== lastPersistedCompleted.value
  )
}

function formatCompletedFilename(name) {
  // completed_instructions.YYYYMMDD_HHMMSS.md
  const m = /^completed_instructions\.(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})\.md$/.exec(name)
  if (!m) return name
  const [, yyyy, mm, dd, hh, mi, ss] = m
  return `${yyyy}-${mm}-${dd} ${hh}:${mi}:${ss}`
}

async function reloadCompletedFiles() {
  completedFilesLoading.value = true
  try {
    const data = await fetchCompletedInstructionFiles(props.area, props.project)
    completedFiles.value = Array.isArray(data?.files) ? data.files : []
  } catch (e) {
    // Don't hard-fail the editor if history can't be loaded.
    completedFiles.value = []
  } finally {
    completedFilesLoading.value = false
  }
}

async function onCompletedFileSelected() {
  const sel = selectedCompletedFile.value
  if (!sel) return

  if (hasUnsavedChanges()) {
    const ok = window.confirm(
      'You have unsaved changes. Loading a snapshot will overwrite the current text boxes. Continue?'
    )
    if (!ok) {
      // Reset UI to "Latest" since that's what reloadFromDisk shows.
      selectedCompletedFile.value = '__latest__'
      return
    }
  }

  loading.value = true
  error.value = ''
  status.value = ''
  try {
    if (sel === '__latest__') {
      const done = await fetchInstructionFile(props.area, 'completed_instructions.md', props.project)
      completedInstructions.value = done
      lastPersistedCompleted.value = done
      submitNeedsAttention.value = false
      status.value = 'Loaded latest completed_instructions.md from disk.'
      return
    }

    const done = await fetchCompletedInstructionFile(props.area, sel, props.project)
    completedInstructions.value = done

    // Intentionally *not* updating lastPersistedCompleted: this content is not the current alias file.
    submitNeedsAttention.value = true
    status.value = `Loaded snapshot: ${sel}. Click Submit (save) to make it the latest.`
  } catch (e) {
    error.value = e?.message ?? String(e)
  } finally {
    loading.value = false
  }
}

async function persistBoth() {
  await Promise.all([
    saveInstructionFile(props.area, 'instructions.md', currentInstructions.value, props.project),
    saveInstructionFile(props.area, 'completed_instructions.md', completedInstructions.value, props.project)
  ])
}

async function reloadFromDisk() {
  loading.value = true
  error.value = ''
  status.value = ''
  try {
    const [cur, done] = await Promise.all([
      fetchInstructionFile(props.area, 'instructions.md', props.project),
      fetchInstructionFile(props.area, 'completed_instructions.md', props.project)
    ])
    currentInstructions.value = cur
    completedInstructions.value = done

    lastPersistedCurrent.value = cur
    lastPersistedCompleted.value = done

    selectedCompletedFile.value = '__latest__'
    submitNeedsAttention.value = false

    await reloadCompletedFiles()
    status.value = 'Reloaded from disk.'
  } catch (e) {
    error.value = e?.message ?? String(e)
  } finally {
    loading.value = false
  }
}

async function saveToDisk() {
  loading.value = true
  error.value = ''
  status.value = ''
  try {
    await persistBoth()

    lastPersistedCurrent.value = currentInstructions.value
    lastPersistedCompleted.value = completedInstructions.value

    selectedCompletedFile.value = '__latest__'
    submitNeedsAttention.value = false

    await reloadCompletedFiles()
    status.value = 'Saved.'
  } catch (e) {
    error.value = e?.message ?? String(e)
  } finally {
    loading.value = false
  }
}

async function markCompleted() {
  loading.value = true
  error.value = ''
  status.value = ''
  try {
    // 1) Save both current + completed as-is first.
    await persistBoth()

    lastPersistedCurrent.value = currentInstructions.value
    lastPersistedCompleted.value = completedInstructions.value
    selectedCompletedFile.value = ''

    // 2) Clear the completed textbox
    completedInstructions.value = ''

    // 3) Copy current instructions into completed textbox
    completedInstructions.value = currentInstructions.value

    // 4) Highlight Submit so the user knows they can persist the new state.
    submitNeedsAttention.value = true

    status.value = 'Copied current instructions into Completed. Click Submit (save) to persist.'
  } catch (e) {
    error.value = e?.message ?? String(e)
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.area, props.project],
  async () => {
    await reloadFromDisk()
  },
  { immediate: true }
)
</script>

<style scoped>
.tabEditor { display: flex; flex-direction: column; gap: 12px; }

.topRow {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.areaTitle .label { font-size: 12px; color: var(--muted); }
.areaTitle .value { font-size: 14px; }

.actions { display: flex; gap: 8px; }

.btn {
  appearance: none;
  border: 1px solid var(--btn-border);
  background: var(--btn-bg);
  color: var(--text);
  padding: 10px 12px;
  border-radius: 10px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.btn:disabled { opacity: 0.55; cursor: not-allowed; }

.btn.danger {
  background: var(--btn-danger-bg);
  border-color: var(--btn-danger-border);
}

.btn.danger:hover:not(:disabled) {
  background: var(--btn-danger-bg-hover);
  border-color: var(--btn-danger-border-hover);
}

.btn.primary {
  background: var(--btn-primary-bg);
  border-color: var(--btn-primary-border);
}

.btn.primary:hover:not(:disabled) {
  background: var(--btn-primary-bg-hover);
  border-color: var(--btn-primary-border-hover);
}

.btn.primary.attention {
  border-color: var(--btn-attention-border);
  box-shadow: 0 0 0 3px var(--btn-attention-glow);
}

.error {
  margin: 0;
  padding: 10px 12px;
  border: 1px solid var(--error-panel-border);
  background: var(--error-panel-bg);
  border-radius: 10px;
  color: var(--text);
}

.status {
  margin: 0;
  padding: 10px 12px;
  border: 1px solid var(--status-border);
  background: var(--status-bg);
  border-radius: 10px;
  color: var(--muted);
}

.completedBlock {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.completedHistory {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}

.completedHistoryLabel {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12px;
  color: var(--muted);
  flex: 1;
  min-width: 260px;
}

.completedHistoryLabel select {
  appearance: none;
  border: 1px solid var(--border);
  background: var(--panel2);
  color: var(--text);
  padding: 10px 12px;
  border-radius: 10px;
  font-size: 13px;
}

.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}

@media (min-width: 1000px) {
  .grid { grid-template-columns: 1fr; }
}
</style>
