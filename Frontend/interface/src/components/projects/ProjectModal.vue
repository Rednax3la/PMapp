<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <header class="modal-header">
        <h3>{{ project.name }}</h3>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </header>
      <div class="modal-body">
        <p>{{ project.description }}</p>
        <div class="project-meta">
          <!-- reuse meta layout -->
        </div>
        <!-- additional details like budget, spent, tasks list -->
      </div>
      <footer class="modal-footer">
        <AppButton variant="primary" @click="$emit('close')">Close</AppButton>
      </footer>
    </div>
  </div>
</template>

<script>
import AppButton from '@/components/ui/AppButton.vue';

export default {
  name: 'ProjectModal',
  components: { AppButton },
  props: {
    project: { type: Object, required: true }
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal-content {
  background: var(--bg-section);
  color: var(--text-primary);
  border-radius: 10px;
  width: 90%;
  max-width: 600px;
  box-shadow: var(--shadow);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 16px 20px;
  background: rgba(0,0,0,0.1);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  color: var(--text-secondary);
  transition: color 0.2s ease;
}
.close-btn:hover {
  color: var(--danger);
}

.modal-body {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
}

.modal-body p {
  margin-bottom: 1rem;
  color: var(--text-secondary);
}

.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  background: rgba(0,0,0,0.05);
}
</style>

