//Frontend/website/src/components/layout/AppHeader.vue
<template>
  <header class="header">
    <h2>{{ title }}</h2>
    <div class="header-actions">
      <slot name="actions" />
    </div>
  </header>
</template>

<script>
export default {
  name: 'AppHeader',
  props: {
    title: { type: String, required: true }
  }
};
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--border-color);
}

.header h2 {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  gap: 15px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .header-actions {
    width: 100%;
    flex-wrap: wrap;
  }
}
</style>