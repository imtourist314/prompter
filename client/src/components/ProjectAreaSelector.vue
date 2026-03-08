<template>
  <div class="selector">
    <div class="field">
      <label for="project-select">Project</label>
      <select id="project-select" :value="selectedProject" @change="onProjectChange($event.target.value)">
        <option value="" disabled>
          {{ projects?.length ? 'Select project' : 'No projects available' }}
        </option>
        <option v-for="project in projects" :key="project" :value="project">
          {{ project }}
        </option>
      </select>
    </div>
    <div class="field">
      <label for="area-select">Area</label>
      <select
        id="area-select"
        :value="selectedArea"
        :disabled="!areas?.length"
        @change="onAreaChange($event.target.value)"
      >
        <option value="" disabled>
          {{ areas?.length ? 'Select area' : 'Select project first' }}
        </option>
        <option v-for="area in areas" :key="area" :value="area">
          {{ area }}
        </option>
      </select>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  projects: {
    type: Array,
    default: () => [],
  },
  areas: {
    type: Array,
    default: () => [],
  },
  selectedProject: {
    type: String,
    default: '',
  },
  selectedArea: {
    type: String,
    default: '',
  },
});

const emit = defineEmits(['update:project', 'update:area']);

const onProjectChange = (value) => {
  emit('update:project', value);
};
const onAreaChange = (value) => {
  emit('update:area', value);
};
</script>

<style scoped>
.selector {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

label {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
}

select {
  padding: 0.35rem 0.75rem;
  border-radius: 0.5rem;
  background: var(--color-input-bg);
  color: var(--color-text);
  border: 1px solid var(--color-input-border);
  min-width: 160px;
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
