<template>
  <div class="skeleton-card glass-card" :style="{ height: height }">
    <div class="skeleton sk-title"></div>
    <div class="skeleton sk-line"></div>
    <div class="skeleton sk-line short"></div>
  </div>
</template>

<script>
export default {
  name: 'SkeletonCard',
  props: {
    height: { type: String, default: '120px' }
  }
}
</script>

<style scoped>
.skeleton-card {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow: hidden;
}

.sk-title {
  height: 18px;
  width: 55%;
}

.sk-line {
  height: 12px;
  width: 90%;
}

.sk-line.short {
  width: 65%;
}
</style>
