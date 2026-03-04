<template>
  <div class="mdbox">
    <div class="toolbar">
      <div class="title">{{ title }}</div>
      <div class="spacer"></div>
      <label class="toggle">
        <input type="checkbox" v-model="showPreview" />
        Preview
      </label>
    </div>

    <div class="content" :class="{ preview: showPreview }">
      <textarea
        class="textarea"
        :value="modelValue"
        rows="40"
        @input="$emit('update:modelValue', $event.target.value)"
        spellcheck="false"
      />

      <div v-if="showPreview" class="previewPane" v-html="rendered"></div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  title: { type: String, required: true },
  modelValue: { type: String, default: '' }
})

defineEmits(['update:modelValue'])

const showPreview = ref(true)

// Avoid rendering on every keystroke if content is huge.
const rendered = computed(() => {
  const md = props.modelValue ?? ''
  return marked.parse(md, { mangle: false, headerIds: false })
})

watch(
  () => props.modelValue,
  (v) => {
    if (v == null) return
  }
)
</script>

<style scoped>
.mdbox {
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  background: var(--panel-overlay);
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
  background: var(--surface-soft);
}

.title { font-size: 13px; color: var(--muted); }
.spacer { flex: 1; }
.toggle { font-size: 12px; color: var(--muted); display: flex; align-items: center; gap: 6px; }

.content {
  display: grid;
  grid-template-columns: 1fr;
}

.content.preview {
  grid-template-columns: 1fr 1fr;
}

.textarea {
  width: 100%;
  /* Minimum of ~40 lines ("40 characters in height") */
  min-height: calc(40 * 1.35em);
  min-height: 40lh;
  resize: vertical;
  padding: 12px;
  border: 0;
  outline: none;
  background: transparent;
  color: var(--text);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 13px;
  line-height: 1.35;
  border-right: 1px solid var(--border);
}

.previewPane {
  padding: 12px;
  min-height: calc(40 * 1.35em);
  min-height: 40lh;
  overflow: auto;
  color: var(--text);
}

.previewPane :deep(h1),
.previewPane :deep(h2),
.previewPane :deep(h3) {
  margin-top: 1.0em;
}

.previewPane :deep(code) {
  background: var(--code-inline-bg);
  padding: 0 4px;
  border-radius: 4px;
}

.previewPane :deep(pre) {
  background: var(--code-block-bg);
  padding: 10px;
  border-radius: 8px;
  overflow: auto;
  border: 1px solid var(--border);
}

.previewPane :deep(a) { color: var(--accent); }
</style>
