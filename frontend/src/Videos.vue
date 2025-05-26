<template>
  <section class="videos-section">
    <div v-for="video in filteredVideos" :key="video.id" class="video-card hover-scale" @click="openVideoModal(video)">
      <img :src="video.thumbnail" alt="Video Thumbnail">
      <div class="content">
        <h3>{{ video.title }}</h3>
        <p>{{ video.description }}</p>
      </div>
    </div>
    <transition name="fade">
      <div v-if="showVideoModal" class="video-modal">
        <div class="modal-content">
          <h2>{{ selectedVideo.title }}</h2>
          <video controls>
            <source :src="selectedVideo.url" type="video/mp4">
          </video>
          <button @click="showVideoModal = false">Close</button>
        </div>
      </div>
    </transition>
  </section>
</template>

<script>
export default {
  props: ['searchQuery'],
  data() {
    return {
      videos: [
        {
          id: 1,
          title: 'Cool Video',
          description: 'A cool video description',
          thumbnail: 'https://via.placeholder.com/300x200',
          url: 'https://www.w3schools.com/html/mov_bbb.mp4'
        }
      ],
      showVideoModal: false,
      selectedVideo: {}
    };
  },
  computed: {
    filteredVideos() {
      return this.videos.filter(video =>
        video.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
        video.description.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    }
  },
  methods: {
    openVideoModal(video) {
      this.selectedVideo = video;
      this.showVideoModal = true;
    }
  }
};
</script>
