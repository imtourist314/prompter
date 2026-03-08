<template>
  <div class="status-card">
    <div class="status-header">
      <div>
        <h3>Published Files</h3>
        <p>Latest submissions for the selected project & area</p>
      </div>
      <button type="button" @click="emit('refresh')" :disabled="loading">
        {{ loading ? 'Refreshing…' : 'Refresh' }}
      </button>
    </div>

    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="!files?.length && !loading" class="empty">
      No files found for this selection.
    </div>

    <div class="table-wrapper" v-else>
      <table>
        <thead>
          <tr>
            <th>File</th>
            <th>Component</th>
            <th>Status</th>
            <th>Description</th>
            <th>Updated</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="file in files" :key="file.id">
            <td>
              <button type="button" class="file-link" @click="() => emit('view-file', file)">
                {{ file.file_name }}
              </button>
            </td>
            <td>{{ file.component }}</td>
            <td>
              <span class="badge" :class="file.status.toLowerCase()">{{ file.status }}</span>
            </td>
            <td>{{ file.description || '—' }}</td>
            <td>{{ formatDate(file.updated_at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  files: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: '',
  },
});

const emit = defineEmits(['refresh', 'view-file']);

const formatDate = (value) => {
  if (!value) return '—';
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(new Date(value));
  } catch (err) {
    return value;
  }
};
</script>

<style scoped>
.status-card {
  background: var(--color-surface-alt);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1.25rem;
  margin-top: 1.5rem;
  transition: background 0.2s ease, border-color 0.2s ease;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

h3 {
  margin: 0;
  font-size: 1.1rem;
}

p {
  margin: 0.15rem 0 0;
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

button {
  border: none;
  background: #6366f1;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 999px;
  font-weight: 600;
}

button:disabled {
  opacity: 0.5;
}

.error {
  margin-top: 1rem;
  color: #f87171;
}

.empty {
  margin-top: 1rem;
  color: var(--color-text-muted);
}

.file-link {
  background: none;
  border: none;
  color: var(--color-link, #6366f1);
  padding: 0;
  font: inherit;
  text-decoration: underline;
  cursor: pointer;
}

.file-link:hover,
.file-link:focus-visible {
  color: var(--color-link-hover, #4338ca);
}

.table-wrapper {
  overflow-x: auto;
  margin-top: 1rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

th,
td {
  text-align: left;
  padding: 0.75rem 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.badge {
  padding: 0.15rem 0.65rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge.pending {
  background: rgba(250, 204, 21, 0.2);
  color: #facc15;
}

.badge.delivered {
  background: rgba(14, 165, 233, 0.2);
  color: #0ea5e9;
}

.badge.running {
  background: rgba(249, 115, 22, 0.2);
  color: #f97316;
}

.badge.completed {
  background: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.badge.errored {
  background: rgba(248, 113, 113, 0.2);
  color: #f87171;
}
</style>
