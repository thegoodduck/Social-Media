<template>
  <section class="chat-section" style="background: linear-gradient(to bottom right, #111827, #581c87); border:none;">
    <div class="tabs">
      <button
        :class="{ active: activeSection === 'users-section' }"
        @click="switchSection('users-section')"
      >
        Conversation
      </button>
      <button
        :class="{ active: activeSection === 'World Chat' }"
        @click="switchSection('World Chat')"
      >
        World Chat
      </button>
    </div>
    <div class="sections">
      <div v-show="activeSection === 'users-section'" class="section active">
        <div id="loading" class="loading" v-if="loading">
          <div class="spinner"></div>
        </div>
        <div id="load-more-trigger"></div>
     <div class="users-container" >

          <div
            v-for="user in users"
            :key="user.username"
            class="user-card"
            @click="handleUserClick(user)"
          >
            <div class="profile-picture">
              <img :src="user.profile_picture || 'default-pfp.jpg'" :alt="user.username + ' profile'" />
            </div>
            <div class="username"><strong>{{ user.username }}</strong></div>
          </div>
        </div>
      </div>
      <div v-show="activeSection === 'World Chat'" class="section">
        <div id="chat-container">
          <div id="messages">
            <div
              v-for="message in messages"
              :key="message.id"
              class="message"
            >
              <div class="bubble">
                <div class="text-row">
                  <div
                    class="username"
                    :style="getUsernameStyle(message.username)"
                  >
                    {{ message.username || 'Unknown' }}
                  </div>
                  <span class="message-text">{{ message.text || '[Empty Message]' }}</span>
                </div>
              </div>
            </div>
          </div>
          <div id="input-container">
            <input
              v-model="inputMessage"
              id="input-message"
              type="text"
              placeholder="Type a message..."
              @keyup.enter="sendMessage"
            />
            <button id="send-button" @click="sendMessage">Send</button>
          </div>
          <div id="warning-message">{{ warningMessage }}</div>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import * as Ably from 'ably';
import * as nacl from 'tweetnacl';
import * as naclUtil from 'tweetnacl-util';

export default {
  name: 'Chat',
  data() {
    return {
      activeSection: 'users-section',
      users: [],
      loading: false,
      loggedInUsername: localStorage.getItem('username')?.trim() || null,
      inputMessage: '',
      messages: [],
      warningMessage: '',
      sentMessages: new Set(),
      username: localStorage.getItem('username')?.trim() || 'Unknown',
      userColors: {},
      ably: null,
      channel: null,
      keyPair: null,
      publicKeyBase64: '',
      privateKeyBase64: '',
      peerPublicKeys: {} // username: publicKeyBase64
    };
  },
  methods: {
    switchSection(section) {
      this.activeSection = section;
    },
    async fetchUsers() {
      this.loading = true;
      try {
        const response = await fetch('https://1999-theta.vercel.app/api/UserListChat', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        const users = await response.json();
        const addedUsernames = new Set();
        this.users = users.filter(user => {
          if (addedUsernames.has(user.username)) return false;
          addedUsernames.add(user.username);
          return true;
        });
      } catch (error) {
        console.error('Error fetching users:', error);
      } finally {
        this.loading = false;
      }
    },
    handleUserClick(user) {
      if (user.username !== this.loggedInUsername) {
        localStorage.setItem('chatWith', user.username);
        localStorage.setItem('chatWithId', user.id);
        localStorage.setItem('profileImage', user.profile_picture || 'default-pfp.jpg');
        window.location.href = `https://latestnewsandaffairs.site/public/react.html`;
      }
    },
    getColorForUsername(name) {
      if (!this.userColors[name]) {
        const colors = [
          '#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231',
          '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe',
          '#008080', '#e6beff', '#9a6324', '#800000'
        ];
        this.userColors[name] = colors[Math.floor(Math.random() * colors.length)];
      }
      return this.userColors[name];
    },
    getUsernameStyle(username) {
      if (username === 'USERNAME99') {
        return {
          backgroundColor: '#000',
          color: '#fff',
          fontSize: '23px',
          marginRight: '8px',
          whiteSpace: 'nowrap',
          padding: '4px 8px',
          borderRadius: '4px'
        };
      }
      return {
        fontWeight: 'bold',
        color: this.getColorForUsername(username)
      };
    },
    async fetchPeerPublicKey(username) {
      // TODO: fetch peer's public key from backend
      // For demo, just return localStorage.getItem('publicKey')
      return localStorage.getItem('publicKey');
    },
    async sendMessage() {
      const message = this.inputMessage.trim();
      this.warningMessage = '';
      if (!this.username || this.username === 'Unknown') {
        this.warningMessage = 'Please sign up before sending a message.';
        return;
      }
      if (message) {
        // --- ENCRYPT MESSAGE ---
        const peerUsername = 'recipient'; // TODO: set real recipient
        const peerPublicKeyBase64 = await this.fetchPeerPublicKey(peerUsername);
        const nonce = nacl.randomBytes(nacl.box.nonceLength);
        const messageUint8 = naclUtil.decodeUTF8(message);
        const peerPublicKey = naclUtil.decodeBase64(peerPublicKeyBase64);
        const myPrivateKey = naclUtil.decodeBase64(this.privateKeyBase64);
        const encrypted = nacl.box(messageUint8, nonce, peerPublicKey, myPrivateKey);
        const encryptedBase64 = naclUtil.encodeBase64(encrypted);
        const nonceBase64 = naclUtil.encodeBase64(nonce);
        // Send encrypted message
        const messageId = Date.now() + Math.random();
        this.appendMessage('[encrypted]', this.username, messageId);
        if (this.channel) {
          this.channel.publish('new-message', {
            text: encryptedBase64,
            id: messageId,
            username: this.username,
            nonce: nonceBase64,
            senderPublicKey: this.publicKeyBase64
          });
        }
        this.inputMessage = '';
      }
    },
    appendMessage(text, username, id, nonce, senderPublicKey) {
      // Try to decrypt if encrypted
      if (text && nonce && senderPublicKey) {
        try {
          const nonceUint8 = naclUtil.decodeBase64(nonce);
          const encryptedUint8 = naclUtil.decodeBase64(text);
          const senderPubKeyUint8 = naclUtil.decodeBase64(senderPublicKey);
          const myPrivKeyUint8 = naclUtil.decodeBase64(this.privateKeyBase64);
          const decrypted = nacl.box.open(encryptedUint8, nonceUint8, senderPubKeyUint8, myPrivKeyUint8);
          if (decrypted) {
            text = naclUtil.encodeUTF8(decrypted);
          } else {
            text = '[decryption failed]';
          }
        } catch (e) {
          text = '[decryption error]';
        }
      }
      if (this.sentMessages.has(id)) return;
      this.messages.push({ text, username, id });
      this.sentMessages.add(id);
      this.$nextTick(() => {
        const messagesContainer = this.$el.querySelector('#messages');
        if (messagesContainer) messagesContainer.scrollTop = messagesContainer.scrollHeight;
      });
    }
  },
  mounted() {
    this.fetchUsers();
    // --- E2E ENCRYPTION KEY GENERATION ---
    let priv = localStorage.getItem('privateKey');
    let pub = localStorage.getItem('publicKey');
    if (!priv || !pub) {
      const keyPair = nacl.box.keyPair();
      priv = naclUtil.encodeBase64(keyPair.secretKey);
      pub = naclUtil.encodeBase64(keyPair.publicKey);
      localStorage.setItem('privateKey', priv);
      localStorage.setItem('publicKey', pub);
    }
    this.privateKeyBase64 = priv;
    this.publicKeyBase64 = pub;
    // TODO: send publicKeyBase64 to backend for user profile
    // Initialize Ably
    this.ably = new Ably.Realtime('9frHeA.Si13Zw:KVzVyovw6hCu4RRuy6P11Tyl0h7MJIzv2Q_n4YgbNnE'); // Replace with your Ably API key
    this.ably.connection.on('connected', () => {
      console.log('Connected to Ably');
      this.channel = this.ably.channels.get('chat-room');
      this.channel.subscribe('new-message', (msg) => {
        const { text, id, username, nonce, senderPublicKey } = msg.data;
        if (!this.sentMessages.has(id)) {
          this.appendMessage(text, username, id, nonce, senderPublicKey);
        }
      });
    });
    this.ably.connection.on('failed', () => {
      console.error('Failed to connect to Ably');
      this.warningMessage = 'Failed to connect to chat service.';
    });
  },
  beforeUnmount() {
    if (this.channel) {
      this.channel.unsubscribe('new-message');
    }
    if (this.ably) {
      this.ably.close();
    }
  }
};
</script> 
<style>
.chat-section {
    padding: 20px;
    min-height: 650px;
    height: 100vh;        /* Fill the full viewport height */
    width: 100%;          /* Ensure full width */
    box-sizing: border-box; /* Ensure padding doesn't increase height */
}
.user-card {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  margin: 20px 0;
  background: linear-gradient(to bottom right, #111827, #581c87);
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.3s;
  border-bottom: 2px solid #581c87;
  gap: 20px;
}
.profile-picture img {
  width: 30px;
  height: 30px;
  border-radius: 30%;
  margin-right: 20px;
  object-fit: cover;
}
.username {
  font-size: 1.1rem;
  font-weight: 700;
  color: #fff;
}
@media (max-width: 768px) {
    .user-card {
    padding: 9px 12px;
  }
  .profile-picture img {
    width: 40px;
    height: 40px;
  }
  .username {
    font-size: 0.9rem;
  }
}
#messages {
        padding: 10px; /* Reduced from 20px */
        overflow-y: auto;
        scrollbar-width: thin;
        scrollbar-color: #888 #f0f0f0;
    }

#messages::-webkit-scrollbar {
    width: 3px; /* Reduced from 6px */
}

#messages::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 2px; /* Reduced from 3px */
}
.message {
    display: flex;
    margin-bottom: 5px; /* Reduced from 10px */
     font-size: 15px; /* Reduced from 18px */
   border: none;
}
#input-container {
    padding: 16px; /* Reduced from 15px */
    background: rgba(245, 245, 245, 0.9);
    border-top: 1px solid rgba(0, 0, 0, 0.05);
}
#input-message {
    width: 80%; /* Reduced from 70% */
    padding: 6px 8px; /* Reduced from 12px 15px */
    border: none;
    border-radius: 25px; /* Reduced from 25px */
    background: #fff;
    box-shadow: 0 2px 3px rgba(0, 0, 0, 0.1); /* Reduced from 5px */
    font-size: 14px; /* Reduced from 14px */
    outline: none;
    margin-right: 5px; /* Reduced from 10px */
}

#input-message:focus {
    box-shadow: 0 2px 4px rgba(0, 123, 255, 0.2); /* Reduced from 8px */
}
#send-button {
    padding: 6px 12px; /* Reduced from 12px 25px */
    background: linear-gradient(45deg, #007bff, #00b4ff);
    color: white;
    border: none;
    border-radius: 19px; /* Reduced from 25px */
    cursor: pointer;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px; /* Reduced from 1px */
    transition: transform 0.2s, box-shadow 0.2s;
}

#send-button:hover {
    transform: translateY(-1px); /* Reduced from -2px */
    box-shadow: 0 2px 8px rgba(0, 123, 255, 0.3); /* Reduced from 15px */
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); } /* Reduced from 10px */
  to { opacity: 1; transform: translateY(0); }
}
     .bubble {
    background-color: #f9f9f9;
    margin-bottom: 8px;
    max-width: 80%;
    border: none;
  }

  .text-row {
    display: flex;
    align-items: center;
    gap: 10px; /* Space between username and message */
  }
  .message-text {
    color: #000;
    word-break: break-word;
    flex: 1;
     border: none;
  }
</style>
