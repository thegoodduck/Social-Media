<template>
  <section class="settings-section">
    <h2>Settings</h2>
    <div class="options">
      <div class="option">
        <span>Enable Dark Mode</span>
        <label class="toggle">
          <input type="checkbox" v-model="settings.darkMode" @change="toggleDarkMode">
          <span class="slider"></span>
        </label>
        <p>Dark Mode: {{ settings.darkMode ? 'On' : 'Off' }}</p>
      </div>
      <div class="option">
        <span>Enable Notifications</span>
        <label class="toggle">
          <input type="checkbox" v-model="settings.notifications">
          <span class="slider"></span>
        </label>
      </div>
      <button @click="saveSettings">Save Settings</button>
    </div>
  </section>
</template>

<script>
export default {
  name: 'Settings',
  props: {
    settings: {
      type: Object,
      default: () => ({
        darkMode: false,
        notifications: true
      })
    }
  },
  methods: {
    toggleDarkMode() {
      document.body.classList.toggle('dark', this.settings.darkMode);
    },
    saveSettings() {
      console.log('Settings saved:', this.settings);
    }
  }
};
</script>