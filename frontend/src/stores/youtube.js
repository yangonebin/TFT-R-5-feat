import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

export const useYoutubeStore = defineStore('youtube', () => {
  const videos = ref([]) 
  const selectedVideo = ref(null)


  const API_KEY = import.meta.env.VITE_YOUTUBE_API_KEY
  const API_URL = 'https://www.googleapis.com/youtube/v3/search'

  const searchVideos = function (keyword) {
    axios({
      method: 'get',
      url: API_URL,
      params: {
        key: API_KEY,
        part: 'snippet',
        q: keyword + ' 주식', 
        type: 'video',
        maxResults: 12,
      }
    })
      .then((res) => {
        videos.value = res.data.items
      })
      .catch((err) => {
        console.error(err)
      })
  }


  const clickVideo = function (video) {
    selectedVideo.value = video
  }

  return { videos, selectedVideo, searchVideos, clickVideo }
})