<template>
  <div class="tabs" role="tablist">
    <button
      v-for="(component, index) in components"
      :key="componentKey(component, index)"
      :class="['tab', { active: isActive(component) }]"
      type="button"
      role="tab"
      @click="handleTabClick(component)"
    >
      {{ componentLabel(component) }}
    </button>
  </div>
</template>

<script setup>
const props = defineProps({
  components: {
    type: Array,
    default: () => [],
  },
  activeComponent: {
    type: [String, Object],
    default: '',
  },
});

const emit = defineEmits(['update:activeComponent']);

const normalizeValue = (value) => {
  if (value === null || value === undefined) return '';
  if (typeof value === 'string' || typeof value === 'number') return String(value);
  if (typeof value === 'object') {
    return (
      value.value ??
      value.component ??
      value.component_name ??
      value.componentName ??
      value.slug ??
      value.key ??
      value.name ??
      value.id ??
      value.code ??
      ''
    );
  }
  return '';
};

const componentLabel = (component) => {
  if (component === null || component === undefined) return '';
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
      normalizeValue(component)
    );
  }
  return '';
};

const componentKey = (component, index) => normalizeValue(component) || componentLabel(component) || `component-${index}`;

const isActive = (component) => {
  const componentValue = normalizeValue(component);
  const activeValue = normalizeValue(props.activeComponent);
  return Boolean(componentValue) && componentValue === activeValue;
};

const handleTabClick = (component) => {
  emit('update:activeComponent', normalizeValue(component));
};
</script>

<style scoped>
.tabs {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 0.35rem;
}

.tab {
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--color-text-secondary);
  padding: 0.2rem 0;
  border-radius: 0;
  font-weight: 500;
  transition: color 0.2s, border-color 0.2s;
}

.tab.active {
  color: var(--color-text);
  border-bottom-color: var(--color-tab-active-border);
}

.tab:not(.active):hover {
  color: var(--color-text);
  border-bottom-color: var(--color-border-subtle);
}

.tab:focus-visible {
  outline: none;
  color: var(--color-text);
  border-bottom-color: var(--color-tab-active-border);
}
</style>
