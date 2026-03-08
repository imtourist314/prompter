<template>
  <div class="workspace" :class="{ 'preview-hidden': !previewEnabled }">
    <div class="workspace-toolbar">
      <label class="preview-toggle">
        <input type="checkbox" :checked="previewEnabled" @change="() => emit('toggle-preview')" />
        Show preview
      </label>
      <span v-if="!previewEnabled" class="preview-status">Preview hidden</span>
    </div>
    <div class="pane editor-pane">
      <div class="pane-header">
        <div>
          <span class="label">Instructions</span>
          <span class="hint">25-line editor</span>
        </div>
        <span class="meta">{{ characters }} chars</span>
      </div>
      <textarea
        rows="25"
        :value="modelValue"
        @input="(event) => emit('update:modelValue', event.target.value)"
        placeholder="Describe the change you want the agent to make..."
      />
    </div>
    <div v-if="previewEnabled" class="pane preview-pane">
      <div class="pane-header">
        <span class="label">Preview</span>
      </div>
      <div class="preview-content" v-html="previewHtml"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  previewHtml: {
    type: String,
    default: '',
  },
  previewEnabled: {
    type: Boolean,
    default: true,
  },
});

const emit = defineEmits(['update:modelValue', 'toggle-preview']);

const characters = computed(() => props.modelValue.length);
</script>

<style scoped>
.workspace {
  --editor-rows: 25;
  --editor-font-size: 0.95rem;
  --editor-line-height: 1.4;
  --editor-vertical-padding: 0.75rem;
  --editor-horizontal-padding: 0.75rem;
  --editor-row-height: calc(var(--editor-font-size) * var(--editor-line-height));
  --editor-min-height: calc(
    var(--editor-row-height) * var(--editor-rows) + (var(--editor-vertical-padding) * 2)
  );
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  align-items: start;
}

.workspace.preview-hidden {
  grid-template-columns: 1fr;
}

.workspace-toolbar {
  grid-column: 1 / -1;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 0.5rem;
}

.pane {
  background: var(--color-surface-alt);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1rem;
  min-height: 400px;
  transition: background 0.2s ease, border-color 0.2s ease;
  display: flex;
  flex-direction: column;
}

.pane-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  font-size: 0.9rem;
}

.label {
  font-weight: 600;
  color: var(--color-text);
}

.hint {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin-left: 0.5rem;
}

.meta {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

textarea {
  width: 100%;
  flex: 1;
  min-height: var(--editor-min-height);
  border: 1px solid var(--color-border);
  background: var(--color-input-bg);
  color: var(--color-text);
  resize: vertical;
  border-radius: 0.5rem;
  padding: var(--editor-vertical-padding) var(--editor-horizontal-padding);
  font-size: var(--editor-font-size);
  line-height: var(--editor-line-height);
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

textarea:focus {
  outline: 2px solid rgba(99, 102, 241, 0.6);
}

.preview-pane {
  display: flex;
  flex-direction: column;
}

.preview-toggle {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}

.preview-status {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.preview-content {
  flex: 1;
  min-height: var(--editor-min-height);
  overflow: auto;
  padding: var(--editor-vertical-padding) var(--editor-horizontal-padding);
  background: var(--color-input-bg);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
  font-size: var(--editor-font-size);
  line-height: var(--editor-line-height);
  transition: background 0.2s ease, border-color 0.2s ease;
}

.preview-content :deep(pre) {
  background: var(--color-code-bg);
  padding: 0.5rem;
  border-radius: 0.5rem;
  overflow-x: auto;
}

@media (max-width: 1024px) {
  .workspace {
    grid-template-columns: 1fr;
  }
}
</style>
