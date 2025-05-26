<template>
  <section class="settings-section">
    <h2>Settings</h2>
    <div class="options">
      <div
        class="option"
        v-for="item in toggleSettings"
        :key="item.key"
      >
        <span>{{ item.label }}</span>
        <div
          class="toggle-switch"
          :aria-pressed="settings[item.key]"
          role="switch"
          tabindex="0"
          @click="toggleSetting(item.key)"
          @keydown.space.prevent="toggleSetting(item.key)"
          @keydown.enter.prevent="toggleSetting(item.key)"
          :style="getToggleStyle(item.key)"
        >
          <div
            class="toggle-knob"
            :style="getKnobStyle(item.key)"
          ></div>
        </div>
        <p class="status-text">{{ getStatusText(item.key) }}</p>
      </div>

      <div class="option action-option">
        <button @click="openBlockedUsers">Blocked Users</button>
      </div>
      <div class="option action-option">
        <button @click="viewMyActivity">My Activity</button>
      </div>
      <div class="option action-option">
        <button @click="logOut">Log Out</button>
      </div>

      <button class="save-button" @click="saveSettings">Save Settings</button>
    </div>
  </section>
</template>

<script>
export default {
  name: "Settings",
  props: {
    settings: {
      type: Object,
      default: () => ({
        darkMode: false,
        notifications: true,
        privateAccount: false,
        showOnlineStatus: true,
        twoFactorAuth: false,
      }),
    },
  },
  computed: {
    toggleSettings() {
      return [
        { key: "darkMode", label: "Enable Dark Mode" },
        { key: "notifications", label: "Enable Notifications" },
        { key: "privateAccount", label: "Enable Private Account" },
        { key: "showOnlineStatus", label: "Show Online Status" },
        { key: "twoFactorAuth", label: "Enable Two-Factor Authentication" },
      ];
    },
  },
  methods: {
    toggleSetting(key) {
      this.settings[key] = !this.settings[key];
      if (key === "darkMode") {
        this.toggleDarkMode();
      }
    },
    toggleDarkMode() {
      document.body.classList.toggle("dark", this.settings.darkMode);
    },
    getStatusText(key) {
      switch (key) {
        case "darkMode":
          return this.settings.darkMode ? "On" : "Off";
        case "notifications":
          return this.settings.notifications ? "On" : "Off";
        case "privateAccount":
          return this.settings.privateAccount ? "On" : "Off";
        case "showOnlineStatus":
          return this.settings.showOnlineStatus ? "Visible" : "Hidden";
        case "twoFactorAuth":
          return this.settings.twoFactorAuth ? "Enabled" : "Disabled";
        default:
          return "";
      }
    },
    getToggleStyle(key) {
      const isOn = this.settings[key];
      return {
        width: "50px",
        height: "28px",
        borderRadius: "14px",
        backgroundColor: isOn ? "#4caf50" : "#ccc",
        position: "relative",
        cursor: "pointer",
        transition: "background-color 0.3s ease",
        flexShrink: 0,
        display: "inline-block",
      };
    },
    getKnobStyle(key) {
      const isOn = this.settings[key];
      return {
        height: "22px",
        width: "22px",
        backgroundColor: "#fff",
        borderRadius: "50%",
        position: "absolute",
        top: "3px",
        left: isOn ? "25px" : "3px",
        transition: "left 0.3s ease",
        boxShadow: "0 1px 3px rgba(0,0,0,0.4)",
      };
    },
    saveSettings() {
      console.log("Settings saved:", this.settings);
      alert("Settings saved successfully!");
    },
    openBlockedUsers() {
      alert("Navigating to Blocked Users...");
    },
    viewMyActivity() {
      alert("Navigating to My Activity...");
    },
    logOut() {
      alert("Logging out...");
    },
  },
  mounted() {
    // Apply dark mode if enabled initially
    if (this.settings.darkMode) {
      document.body.classList.add("dark");
    }
  },
};
</script>

<style scoped>
.settings-section {
  max-width: 600px;
  margin: 1.5rem auto;
  background: #fff;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
}
h2 {
  margin-bottom: 1.5rem;
  font-weight: 700;
  font-size: 1.8rem;
  color: #222;
  text-align: center;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.option {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.option span {
  font-size: 1rem;
  font-weight: 500;
  flex-grow: 1;
}

.status-text {
  margin-left: 1rem;
  font-size: 0.9rem;
  color: #666;
  min-width: 90px;
  text-align: right;
  user-select: none;
}

/* Action buttons */

.action-option button {
  padding: 0.55rem 1rem;
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  background-color: #1976d2;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  width: 100%;
  max-width: 220px;
  text-align: center;
}

.action-option button:hover {
  background-color: #125ea2;
}

.save-button {
  margin-top: 2rem;
  width: 100%;
  padding: 0.75rem;
  font-size: 1.2rem;
  font-weight: 700;
  color: white;
  background-color: #007bff;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.save-button:hover {
  background-color: #0056b3;
}

/* Responsive */

@media (max-width: 480px) {
  .option {
    flex-direction: column;
    align-items: flex-start;
  }
  .status-text {
    margin-left: 0;
    margin-top: 0.25rem;
    text-align: left;
  }
  .action-option button {
    max-width: 100%;
  }
}
</style>
