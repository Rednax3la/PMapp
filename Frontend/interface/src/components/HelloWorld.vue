<template>
  <div id="admin-dashboard" :class="{ dark: isDark, light: !isDark }">
    <aside class="sidebar">
      <h2 class="logo">
        <img src="../assets/logo.png" alt="Zain logo" class="logo-img" />
        ZainPM
      </h2>
      <nav>
        <ul>
          <li class="active">Dashboard</li>
          <li>Projects</li>
          <li>Tasks</li>
          <li>Users</li>
          <li>Settings</li>
        </ul>
      </nav>
    </aside>

    <div class="main">
      <header class="header">
        <div class="header-left">
          <h1>Dashboard</h1>
        </div>
        <div class="header-right">
          <button class="theme-toggle" @click="isDark = !isDark">
            {{ isDark ? "☀️ Light" : "🌙 Dark" }}
          </button>
          <button class="btn-cta">New Project</button>
        </div>
      </header>

      <section class="cards">
        <div class="card">
          <h3>Total Projects</h3>
          <p>12</p>
        </div>
        <div class="card">
          <h3>Active Tasks</h3>
          <p>34</p>
        </div>
        <div class="card">
          <h3>Completed</h3>
          <p>128</p>
        </div>
        <div class="card">
          <h3>Team Members</h3>
          <p>8</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";

const isDark = ref(true);

// Persist in localStorage
watch(isDark, (val) => {
  localStorage.setItem("zainpm-theme", val ? "dark" : "light");
});

// Load preference on mount
const saved = localStorage.getItem("zainpm-theme");
if (saved === "light") {
  isDark.value = false;
}
</script>

<style lang="less">
/* color variables */
@primary: #00fff7;
@accent: #00e0ff;
@highlight: #00ffb3;
@dark-base: #0a0f1c;
@soft-grid: #1e2f3a;
@shadow-glow: #006b80;

/* Light mode overrides */
.light {
  --bg-base: #f5fafb;
  --bg-section: #d6eff3;
  --text-primary: #102530;
  --text-secondary: #5c7a89;
  --border-color: #c7e3ec;
}

.dark {
  --bg-base: @dark-base;
  --bg-section: @soft-grid;
  --text-primary: #ffffff;
  --text-secondary: rgba(255, 255, 255, 0.7);
  --border-color: @shadow-glow;
}

#admin-dashboard {
  display: flex;
  height: 100vh;
  background: var(--bg-base);
  color: var(--text-primary);
  padding: 0;
  margin: 0;
}

html body #app {
  margin: 0;
  padding: 0;
  height: 100%;
  background: var(--bg-base);
}

* {
  box-sizing: border-box;
  margin: 0;
  border: none;
}

.sidebar {
  width: 240px;
  background: var(--bg-section);
  padding: 2rem 1rem;
  display: flex;
  flex-direction: column;

  .logo {
    font-size: 1.5rem;
    color: @primary;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
  }
  .logo-img {
    width: 20%;
    border-radius: 50%;
    margin-right: 0.5rem;
  }

  nav ul {
    list-style: none;
    padding: 0;

    li {
      padding: 0.75rem 1rem;
      border-radius: 0.5rem;
      cursor: pointer;
      margin-bottom: 0.5rem;
      color: var(--text-secondary);

      &:hover,
      &.active {
        background: var(--border-color);
        color: @accent;
      }
    }
  }
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 2rem;
    background: var(--bg-section);

    .header-left h1 {
      font-size: 1.75rem;
      color: @primary;
    }

    .header-right {
      display: flex;
      gap: 1rem;

      .theme-toggle {
        background: transparent;
        border: 1px solid var(--border-color);
        color: var(--text-primary);
        padding: 0.5rem;
        border-radius: 0.5rem;
        cursor: pointer;
      }

      .btn-cta {
        padding: 0.5rem 1rem;
        background: @accent;
        border: none;
        border-radius: 0.5rem;
        color: #000000;
        font-weight: bold;
        cursor: pointer;

        &:hover {
          background: #00c7e2;
        }
      }
    }
  }

  .cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 1.5rem;
    padding: 2rem;
    background: var(--bg-base);

    .card {
      background: var(--bg-section);
      padding: 1.5rem;
      border-radius: 1rem;
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);

      h3 {
        margin: 0;
        color: @highlight;
        font-size: 1.1rem;
      }

      p {
        font-size: 2rem;
        margin: 0.5rem 0 0;
      }
    }
  }
}
</style>
