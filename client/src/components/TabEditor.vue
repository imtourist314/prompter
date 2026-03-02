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

      <MarkdownTextBox
        title="Completed/processed instructions (persisted as completed_instructions.md)"
        v-model="completedInstructions"
      />
    </div>
  </section>
</template>

<script setup>
import { ref, watch } from 'vue'
import MarkdownTextBox from './MarkdownTextBox.vue'
import { fetchInstructionFile, saveInstructionFile } from '../api'

const props = defineProps({
  area: { type: String, required: true }
})

const loading = ref(false)
const error = ref('')
const status = ref('')

const currentInstructions = ref('')
const completedInstructions = ref('')
const submitNeedsAttention = ref(false)

async function persistBoth() {
  await Promise.all([
    saveInstructionFile(props.area, 'instructions.md', currentInstructions.value),
    saveInstructionFile(props.area, 'completed_instructions.md', completedInstructions.value)
  ])
}

async function reloadFromDisk() {
  loading.value = true
  error.value = ''
  status.value = ''
  try {
    const [cur, done] = await Promise.all([
      fetchInstructionFile(props.area, 'instructions.md'),
      fetchInstructionFile(props.area, 'completed_instructions.md')
    ])
    currentInstructions.value = cur
    completedInstructions.value = done
    submitNeedsAttention.value = false
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
    submitNeedsAttention.value = false
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
  () => props.area,
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
  border: 1px solid var(--border);
  background: rgba(255,255,255,0.04);
  color: var(--text);
  padding: 10px 12px;
  border-radius: 10px;
  font-size: 13px;
  cursor: pointer;
}

.btn:disabled { opacity: 0.55; cursor: not-allowed; }

.btn.danger {
  /* Cancel button (red) */
  background: rgba(255, 59, 48, 0.22);
  border-color: rgba(255, 59, 48, 0.75);
}

.btn.danger:hover:not(:disabled) {
  background: rgba(255, 59, 48, 0.3);
  border-color: rgba(255, 59, 48, 0.9);
}

.btn.primary {
  /* Submit button (green) */
  background: rgba(52, 199, 89, 0.22);
  border-color: rgba(52, 199, 89, 0.75);
}

.btn.primary:hover:not(:disabled) {
  background: rgba(52, 199, 89, 0.3);
  border-color: rgba(52, 199, 89, 0.9);
}

.btn.primary.attention {
  border-color: rgba(255, 215, 102, 0.95);
  box-shadow: 0 0 0 3px rgba(255, 215, 102, 0.22);
}

.error {
  margin: 0;
  padding: 10px 12px;
  border: 1px solid rgba(255, 107, 107, 0.45);
  background: rgba(255, 107, 107, 0.1);
  border-radius: 10px;
  color: var(--text);
}

.status {
  margin: 0;
  padding: 10px 12px;
  border: 1px solid rgba(122, 162, 255, 0.35);
  background: rgba(122, 162, 255, 0.08);
  border-radius: 10px;
  color: var(--muted);
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
