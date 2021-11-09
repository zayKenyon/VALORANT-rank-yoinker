<template>
  <!-- <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto"> -->
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap">

  <img alt="vRY Logo" src="./assets/logo.png" class="logo">
  <img src="./assets/PhoenixArtwork.png" alt="Phoenix" class="img phoenix">
  <img src="./assets/KilljoyArtwork.png" alt="Killjoy" class="img killjoy">
  <img alt="vRY Logo" src="./assets/logo.png" class="logo">
  <player-component v-for="Player in loadoutJSON"
  :key=Player.name :PlayerLoadout="Player" @openModal="openModal"/>

  <player-modal v-if="showModal" :PlayerLoadout="modalArguments" @closeModal="closeModal"/>

</template>

<script>
// import loadoutJSON from './data/loadoutData.json'
import PlayerComponent from './components/PlayerComponent.vue'
import PlayerModal from './components/PlayerModal.vue'

export default {
  name: 'App',
  components: { PlayerComponent, PlayerModal },
  data() {
    return {
      loadoutJSON: null,
      showModal: false,
      modalArguments: null
    }
  },
  methods: {
    openModal(PlayerLoadout){
      this.showModal = true
      this.modalArguments = PlayerLoadout
    },
    closeModal(){
      console.log('closeModal')
      this.showModal = false,
      this.modalArguments = null
    },    
  },
  mounted() {
    console.log("Starting connection to WebSocket Server")
    let self = this
    this.connection = new WebSocket("ws://localhost:1100/")

    this.connection.onmessage = function(event) {
      // console.log(event);
      console.log(JSON.parse(event.data));
      self.loadoutJSON = JSON.parse(event.data)
    }

    this.connection.onopen = function() {
      // console.log(event)
      console.log("Successfully connected to websocket server...")
    }
  }
}
</script>

<style>
#app {
  font-family: "Inter";
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #151418;
  margin-top: 60px;
}

body {
  position: relative;
  margin: 0;
  padding: 0;
  background-color: var(--background);
  /* background-image: url('./assets/PhoenixArtwork.png'); */
  /* background-repeat: no-repeat; */
  /* background-attachment: fixed; */
  /* background-position: left; */
  
}

.img {
  position: fixed;
  top: 0;
  bottom: 0;
  margin-top: auto;
  margin-bottom: auto;
  /* margin: 0, auto; */
  width: 30%;
  /* height: 100%; */
  z-index: -1;
  opacity: 0.5;
}

.phoenix {
  left: 50px;
  /* background-color: red; */
}

.killjoy {
  right: 50px;
  /* background-color: red; */
}


.logo {
  position: relative;
  top: -30px;
  width: 30vmin;
  margin: 0, 0, 100px;
}
</style>
