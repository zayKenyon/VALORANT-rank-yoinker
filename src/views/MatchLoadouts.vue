<template>
    <img alt="vRY Logo" src="../assets/logo.png" class="logo">
  <img src="../assets/PhoenixArtwork.png" alt="Phoenix" class="img phoenix">
  <img src="../assets/KilljoyArtwork.png" alt="Killjoy" class="img killjoy">
  <div class="lastUpdateDiv">
    <span class="lastUpdate">Last updated: </span>
    <span class="lastUpdateValue">{{ lastUpdateString }}</span>
  </div>
  <player-component :max="Players.length" v-for="Player in Players"
  :key=Player.name :PlayerLoadout="Player" @openModal="openModal"/>

  <player-modal v-if="showModal" :PlayerLoadout="modalArguments" @closeModal="closeModal"/>
</template>

<script>
import PlayerComponent from '../components/PlayerComponent.vue'
import PlayerModal from '../components/PlayerModal.vue'


export default {
    name: 'MatchLoadouts',
    components: { PlayerComponent, PlayerModal },
     data() {
        return {
            loadoutJSON: null,
            showModal: false,
            modalArguments: null,
            lastUpdate: null,
            lastUpdateString: "",
            Players: null
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
                this.lastUpdateSeconds = Math.round(+new Date / 1000 - this.lastUpdate)
                if (this.lastUpdateString == 1) {
                    this.lastUpdateString = "1 second ago"
                } else if (this.lastUpdateSeconds < 60) {
                    this.lastUpdateString = this.lastUpdateSeconds + " seconds ago"
                } else if (Math.round(this.lastUpdateSeconds / 60) == 1) {
                    this.lastUpdateString = "1 minute ago"
                } else if (this.lastUpdateSeconds < 3600) {
                    this.lastUpdateString = Math.round(this.lastUpdateSeconds / 60) + " minutes ago"
                } else if (Math.round(this.lastUpdateSeconds / 3600) == 1) {
                    this.lastUpdateString = "1 hour ago"
                } else if (this.lastUpdateSeconds < 86400) {
                    this.lastUpdateString = Math.round(this.lastUpdateSeconds / 3600) + " hours ago"
                } else if (Math.round(this.lastUpdateSeconds / 86400) == 1) {
                    this.lastUpdateString = "1 day ago"
                } else {
                    this.lastUpdateString = Math.round(this.lastUpdateSeconds / 86400) + " days ago"
                }
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

        // if (localStorage.getItem('lastUpdated') !== null) {
            // self.lastUpdate = localStorage.getItem('lastUpdated')
        // }




        console.log("Starting connection to WebSocket Server")
        let connection = new WebSocket("ws://localhost:1100/")
        
        connection.onmessage = function(event) {
            console.log(JSON.parse(event.data));
            self.loadoutJSON = JSON.parse(event.data)
            localStorage.clear()
            localStorage.setItem("loadoutJSON", JSON.stringify(self.loadoutJSON))
            self.Players = self.loadoutJSON.Players
            // self.lastUpdate = +new Date
            self.lastUpdate = self.loadoutJSON.time
            // console.log(+new Date)
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
        /* left: 0; */
        font-size: 1.5em;
        color: white;
    }

    .lastUpdateDiv {
        width: 22%;
        text-align: center;
        left: 0;
        right: 0;
        margin: auto;
        margin-bottom: 1em;
        /* border: 1px solid black; */
    }

    .lastUpdateValue {
        color: green;
        font-size: 1.5em;
        font-weight: bold;
    }

    #app {
        font-family: Avenir, Helvetica, Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-align: center;
        color: #2c3e50;
    }   

</style>