<template>
    <img alt="vRY Logo" src="../assets/logo.png" class="logo">
  <img src="../assets/PhoenixArtwork.png" alt="Phoenix" class="img phoenix">
  <img src="../assets/KilljoyArtwork.png" alt="Killjoy" class="img killjoy">
  <div class="lastUpdateDiv">
    <span class="lastUpdate">Last updated: </span>
    <span class="lastUpdateValue">{{ lastUpdateString }}</span>
  </div>
  <player-component :max="loadoutJSON.length" v-for="Player in loadoutJSON"
  :key=Player.name :PlayerLoadout="Player" @openModal="openModal"/>

  <player-modal v-if="showModal" :PlayerLoadout="modalArguments" @closeModal="closeModal"/>
</template>

<script>
import PlayerComponent from './PlayerComponent.vue'
import PlayerModal from './PlayerModal.vue'


export default {
    name: 'MatchLoadouts',
    components: { PlayerComponent, PlayerModal },
     data() {
        return {
            loadoutJSON: null,
            showModal: false,
            modalArguments: null,
            lastUpdate: null,
            lastUpdateString: ""
        }
    },

    methods: {
        openModal(PlayerLoadout) {
            this.showModal = true
            this.modalArguments = PlayerLoadout
        },
        closeModal() {
            this.showModal = false,
            this.modalArguments = null
        },   

        lastUpdatedLoop() {
            setInterval(() => {
                this.lastUpdateString = Math.round((+new Date - this.lastUpdate) / 1000) + " seconds ago"
                // console.log(+new Date)
                console.log(this.lastUpdateString)
                // .format('MMMM Do YYYY, h:mm:ss a')
                //  = new Date().toLocaleString()
                // this.lastUpdate = this.lastUpdateString
            }, 1000)
        }
    },

    mounted() {
        let self = this
        self.lastUpdate = +new Date

        self.lastUpdatedLoop()

        if (localStorage.getItem('loadoutJSON') !== null) {
             self.loadoutJSON = JSON.parse(localStorage.getItem('loadoutJSON'))
        }
        console.log(self.loadoutJSON)

        if (localStorage.getItem('lastUpdated') !== null) {
            self.lastUpdate = localStorage.getItem('lastUpdated')
        }




        console.log("Starting connection to WebSocket Server")
        let connection = new WebSocket("ws://localhost:1100/")
        
        connection.onmessage = function(event) {
            console.log(JSON.parse(event.data));
            self.loadoutJSON = JSON.parse(event.data)
            localStorage.clear()
            localStorage.setItem("loadoutJSON", JSON.stringify(self.loadoutJSON))
            self.lastUpdate = +new Date
            localStorage.setItem("lastUpdated", +new Date)
        }

        connection.onopen = function() {
            console.log("Successfully connected to websocket server...")
        }

    }

}
</script>

<style>
    .lastUpdate {
        font-size: 1.5em;
        color: white;
    }

    .lastUpdateDiv {
        text-align: center;
        margin-bottom: 1em;
    }

    .lastUpdateValue {
        color: green;
        font-size: 1.5em;
        font-weight: bold;
    }

</style>