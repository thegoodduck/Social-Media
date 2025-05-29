<template>
  <section class="settings-section container mt-5">
    <h2 class="text-center mb-4">Settings</h2>
    <div class="row">
      <!-- Vertical Navigation with Content -->
      <div class="col-md-12">
        <ul class="nav flex-column nav-pills" role="tablist">
          <!-- Profile Tab -->
          <li class="nav-item mb-2">
            <a
              class="nav-link"
              :class="{ active: activeTab === 'profile' }"
              @click="toggleTab('profile')"
              href="#profile"
              role="tab"
              aria-expanded="activeTab === 'profile'"
            >
              Profile
            </a>
            <div
              v-show="activeTab === 'profile'"
              class="tab-content p-4 tab-border rounded shadow-sm mt-2"
            >
              <div class="mb-3 d-flex align-items-center">
                <strong class="me-2">Username:</strong>
                <span>{{ userProfile.username || 'Loading...' }}</span>
                <i class="fas fa-edit edit-icon ms-auto" @click="changeUsername"></i>
              </div>
              <hr>
              <div class="mb-3">
                <strong>Profile Picture:</strong>
                <div class="d-flex align-items-center mt-2">
                  <img
                    :src="userProfile.profilePicture"
                    alt="Profile Picture"
                    class="rounded-circle me-3"
                    style="width: 80px; height: 80px; object-fit: cover;"
                  />
                  <i class="fas fa-edit edit-icon" @click="triggerFileInput"></i>
                  <input
                    type="file"
                    ref="profileFileInput"
                    @change="handleProfilePictureChange"
                    accept="image/*"
                    style="display: none;"
                  />
                  <button
                    v-if="newProfilePicture"
                    class="btn btn-success btn-sm ms-3"
                    @click="saveProfilePicture"
                  >
                    Save
                  </button>
                </div>
              </div>
              <hr>
              <div class="mb-3 d-flex align-items-center">
                <strong class="me-2">Description:</strong>
                <span>{{ userProfile.description || 'No description available' }}</span>
                <i class="fas fa-edit edit-icon ms-auto" @click="editDescription"></i>
              </div>
              <hr>
              <div class="mb-3 d-flex align-items-center">
                <strong class="me-2">Location:</strong>
                <span>{{ userProfile.location || 'Location not available' }}</span>
                <i class="fas fa-edit edit-icon ms-auto" @click="editLocation"></i>
              </div>
              <hr>
              <div class="mb-3 d-flex align-items-center">
                <strong class="me-2">Status:</strong>
                <span>{{ userProfile.status || 'Status not available' }}</span>
                <i class="fas fa-edit edit-icon ms-auto" @click="editStatus"></i>
              </div>
              <hr>
              <div class="mb-3 d-flex align-items-center">
                <strong class="me-2">Profession:</strong>
                <span>{{ userProfile.profession || 'Profession not available' }}</span>
                <i class="fas fa-edit edit-icon ms-auto" @click="editProfession"></i>
              </div>
              <hr>
              <div class="mb-3 d-flex align-items-center">
                <strong class="me-2">Hobby:</strong>
                <span>{{ userProfile.hobby || 'Hobby not available' }}</span>
                <i class="fas fa-edit edit-icon ms-auto" @click="editHobby"></i>
              </div>
            </div>
          </li>

          <!-- General Tab -->
          <li class="nav-item mb-2">
            <a
              class="nav-link"
              :class="{ active: activeTab === 'general' }"
              @click="toggleTab('general')"
              href="#general"
              role="tab"
              aria-expanded="activeTab === 'general'"
            >
              General
            </a>
            <div
              v-show="activeTab === 'general'"
              class="tab-content p-4 tab-border rounded shadow-sm mt-2"
            >
              <div
                v-for="item in toggleSettings"
                :key="item.key"
                class="d-flex justify-content-between align-items-center mb-3"
              >
                <span>{{ item.label }}</span>
                <div class="d-flex align-items-center">
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
                    <div class="toggle-knob" :style="getKnobStyle(item.key)"></div>
                  </div>
                  <span class="ms-3 status-text">{{ getStatusText(item.key) }}</span>
                </div>
              </div>
              <button class="btn btn-custom mt-3 w-100" @click="saveSettings">
                Save Settings
              </button>
            </div>
          </li>

          <!-- History Tab -->
          <li class="nav-item mb-2">
            <a
              class="nav-link"
              :class="{ active: activeTab === 'history' }"
              @click="toggleTab('history')"
              href="#history"
              role="tab"
              aria-expanded="activeTab === 'history'"
            >
              History
            </a>
            <div
              v-show="activeTab === 'history'"
              class="tab-content p-4 tab-border rounded shadow-sm mt-2"
            >
              <button class="btn btn-custom w-100" @click="viewMyActivity">
                View My Activity
              </button>
            </div>
          </li>

          <!-- Account Tab -->
          <li class="nav-item mb-2">
            <a
              class="nav-link"
              :class="{ active: activeTab === 'account' }"
              @click="toggleTab('account')"
              href="#account"
              role="tab"
              aria-expanded="activeTab === 'account'"
            >
              Account
            </a>
            <div
              v-show="activeTab === 'account'"
              class="tab-content p-4 tab-border rounded shadow-sm mt-2"
            >
              <button class="btn btn-custom w-100 mb-3" @click="openBlockedUsers">
                Blocked Users
              </button>
              <button class="btn btn-danger w-100" @click="logOut">Log Out</button>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'Settings',
  data() {
    return {
      activeTab: null, // No tab open initially
      userProfile: {
        username: '',
        profilePicture: 'default.jpg',
        description: '',
        location: '',
        status: '',
        profession: '',
        hobby: ''
      },
      newProfilePicture: null,
      settings: {
        darkMode: false,
        notifications: true,
        privateAccount: false,
        showOnlineStatus: true,
        twoFactorAuth: false
      }
    };
  },
  computed: {
    toggleSettings() {
      return [
        { key: 'darkMode', label: 'Dark Mode' },
        { key: 'notifications', label: 'Notifications' },
        { key: 'privateAccount', label: 'Private Account' },
        { key: 'showOnlineStatus', label: 'Show Online Status' },
        { key: 'twoFactorAuth', label: 'Two-Factor Authentication' }
      ];
    }
  },
  methods: {
    toggleTab(tab) {
      this.activeTab = this.activeTab === tab ? null : tab;
    },
    async fetchUserSettings() {
      try {
        const username = localStorage.getItem('username');
        if (!username) {
          alert('Username not found!');
          return;
        }

        const response = await fetch(`https://sports321.vercel.app/api/posts?username=${username}`);
        const data = await response.json();

        this.userProfile = {
          username: username,
          location: data.location || 'Location not available',
          status: data.status || 'Status not available',
          profession: data.profession || 'Profession not available',
          hobby: data.hobby || 'Hobby not available',
          description: data.description || 'No description available',
          profilePicture: data.profile_picture?.startsWith('data:image')
            ? data.profile_picture
            : `https://sports321.vercel.app/${data.profile_picture || 'default.jpg'}`
        };
      } catch (error) {
        console.error('Error fetching user settings:', error);
        this.userProfile = {
          username: localStorage.getItem('username') || '',
          profilePicture: 'default.jpg',
          description: 'No description available',
          location: 'Location not available',
          status: 'Status not available',
          profession: 'Profession not available',
          hobby: 'Hobby not available'
        };
      }
    },
    async updateUserProfileField(field, newValue) {
      const username = localStorage.getItem('username');
      if (!username) {
        alert('Username not found!');
        return;
      }

      try {
        const response = await fetch('https://sports123.vercel.app/api/posts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, [field]: newValue })
        });

        const data = await response.json();
        const successMessage = `${field.charAt(0).toUpperCase() + field.slice(1)} updated successfully`;

        if (data.message === successMessage) {
          alert(`Your ${field} has been updated!`);
          this.userProfile[field] = newValue;
        } else {
          alert(`Failed to update ${field}`);
        }
      } catch (error) {
        console.error(`Error updating ${field}:`, error);
        alert(`Failed to update ${field}`);
      }
    },
    changeUsername() {
      const newUsername = prompt('Enter your new username:', this.userProfile.username);
      if (newUsername?.trim()) {
        this.updateUserProfileField('username', newUsername.trim());
      }
    },
    editDescription() {
      const newDescription = prompt('Enter your new description:', this.userProfile.description);
      if (newDescription?.trim()) {
        this.updateUserProfileField('description', newDescription.trim());
      }
    },
    editLocation() {
      const newLocation = prompt('Enter your new location:', this.userProfile.location);
      if (newLocation?.trim()) {
        this.updateUserProfileField('location', newLocation.trim());
      }
    },
    editStatus() {
      const newStatus = prompt('Enter your new status:', this.userProfile.status);
      if (newStatus?.trim()) {
        this.updateUserProfileField('status', newStatus.trim());
      }
    },
    editProfession() {
      const newProfession = prompt('Enter your new profession:', this.userProfile.profession);
      if (newProfession?.trim()) {
        this.updateUserProfileField('profession', newProfession.trim());
      }
    },
    editHobby() {
      const newHobby = prompt('Enter your new hobby:', this.userProfile.hobby);
      if (newHobby?.trim()) {
        this.updateUserProfileField('hobby', newHobby.trim());
      }
    },
    triggerFileInput() {
      this.$refs.profileFileInput.click();
    },
    handleProfilePictureChange(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.newProfilePicture = e.target.result;
          this.userProfile.profilePicture = e.target.result;
        };
        reader.readAsDataURL(file);
      }
    },
    async saveProfilePicture() {
      if (!this.newProfilePicture) return;

      try {
        const username = localStorage.getItem('username');
        if (!username) {
          alert('Username not found!');
          return;
        }

        const response = await fetch('https://sports123.vercel.app/api/posts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, profilePicture: this.newProfilePicture })
        });

        const data = await response.json();

        if (data.message === 'Profile picture updated successfully') {
          alert('Profile picture updated!');
          this.newProfilePicture = null;
        } else {
          alert('Failed to update profile picture');
        }
      } catch (error) {
        console.error('Error updating profile picture:', error);
        alert('Failed to update profile picture');
      }
    },
    toggleSetting(key) {
      this.settings[key] = !this.settings[key];
      if (key === 'darkMode') {
        this.toggleDarkMode();
      }
    },
    toggleDarkMode() {
      document.documentElement.classList.toggle('dark-mode', this.settings.darkMode);
      localStorage.setItem('darkMode', this.settings.darkMode);
    },
    getStatusText(key) {
      switch (key) {
        case 'darkMode': return this.settings.darkMode ? 'On' : 'Off';
        case 'notifications': return this.settings.notifications ? 'On' : 'Off';
        case 'privateAccount': return this.settings.privateAccount ? 'On' : 'Off';
        case 'showOnlineStatus': return this.settings.showOnlineStatus ? 'Visible' : 'Hidden';
        case 'twoFactorAuth': return this.settings.twoFactorAuth ? 'Enabled' : 'Disabled';
        default: return '';
      }
    },
    getToggleStyle(key) {
      return {
        width: '50px',
        height: '26px',
        borderRadius: '13px',
        background: this.settings[key]
          ? 'linear-gradient(135deg, #34c759, #28a745)'
          : 'linear-gradient(135deg, #e0e0e0, #b0b0b0)',
        position: 'relative',
        cursor: 'pointer',
        transition: 'background 0.3s ease',
        boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.1)'
      };
    },
    getKnobStyle(key) {
      return {
        height: '22px',
        width: '22px',
        background: 'linear-gradient(135deg, #ffffff, #f0f0f0)',
        borderRadius: '50%',
        position: 'absolute',
        top: '2px',
        left: this.settings[key] ? '26px' : '2px',
        transition: 'left 0.3s ease, transform 0.2s ease',
        boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
        transform: this.settings[key] ? 'scale(1.05)' : 'scale(1)'
      };
    },
    saveSettings() {
      console.log('Settings saved:', this.settings);
      alert('Settings saved successfully!');
    },
    openBlockedUsers() {
      alert('Navigating to Blocked Users...');
    },
    viewMyActivity() {
      alert('Navigating to My Activity...');
    },
    logOut() {
      alert('Logging out...');
    }
  },
  mounted() {
    this.fetchUserSettings();
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    this.settings.darkMode = savedDarkMode;
    if (savedDarkMode) {
      document.documentElement.classList.add('dark-mode');
    }
  }
};
</script>


<style scoped>
.nav-pills .nav-link {
  background-color: #000;
  color: #fff;
  border-radius: 12px;
  transition: all 0.3s ease;
  padding: 12px 18px;
  position: relative;
  overflow: hidden;
  border:none;
  margin:10px;
  border-bottom: 2px solid #e64a3c;
}
.tab-content {
  background-color: #1f1f1f;
  border-radius: 12px;
  border: 2px solid transparent;
  background-image: linear-gradient(#1f1f1f, #1f1f1f),
  linear-gradient(45deg, #34c759, #e64a3c);
  background-clip: padding-box, border-box;
  background-origin: padding-box, border-box;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}
.btn-custom {
  background: linear-gradient(90deg, #28a745, #34c759);
  border: none;
  border-radius: 8px;
}
.btn-custom:hover {
  background: linear-gradient(90deg, #218838, #28a745);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
.btn-danger {
  background: linear-gradient(90deg, #dc3545, #e4606d);
  border: none;
  border-radius: 8px;
  padding: 0.5rem 1rem;
  transition: all 0.3s ease;
}
.edit-icon {
  cursor: pointer;
  color: #ccc;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}
.edit-icon:hover {
  color: #34c759;
  transform: scale(1.2);
}
hr {
  border-top: 1px solid #444;
  margin: 0.75rem 0;
}
.toggle-switch {
  width: 40px;
  height: 20px;
  border-radius: 10px;
  position: relative;
  cursor: pointer;
  transition: background-color 0.3s ease;
  border: 1px solid #34c759;
}
.toggle-knob {
  width: 16px;
  height: 16px;
  background-color: white;
  border-radius: 50%;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: transform 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
.dark-mode,
.dark-mode header,
.dark-mode nav,
.dark-mode .tab-content,
.dark-mode .nav-pills .nav-link,
.dark-mode .settings-section input,
.dark-mode .chat-section input,
.dark-mode .post-card .comment-input,
.dark-mode .user-section .search-dropdown input,
.dark-mode .btn-custom,
.dark-mode .btn-danger,
.dark-mode .edit-icon,
.dark-mode hr {
  background: linear-gradient(to bottom right, #111827, #581c87);
  color: #f3f4f6;
}
</style>
