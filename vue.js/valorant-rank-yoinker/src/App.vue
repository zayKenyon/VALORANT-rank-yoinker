<template>
  <!-- <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto"> -->
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap">

  <img alt="vRY Logo" src="./assets/logo.png" class="logo">
  <player-component v-for="Player in loadoutJSON"
  :key=Player.name :PlayerLoadout="Player" @openModal="openModal"/>

  <player-modal v-if="showModal" :PlayerLoadout="modalArguments" @closeModal="closeModal"/>

</template>

<script>
import loadoutJSON from './data/loadoutData.json'
import PlayerComponent from './components/PlayerComponent.vue'
import PlayerModal from './components/PlayerModal.vue'

export default {
  name: 'App',
  components: { PlayerComponent, PlayerModal },
  data() {
    return {
      loadoutJSON: loadoutJSON,
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
    }
    
  },
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
  margin: 0;
  padding: 0;
  background-color: var(--background);
}

.logo {
  width: 30vmin;
}
</style>
