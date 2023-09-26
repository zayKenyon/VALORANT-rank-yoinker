<template>
    <img alt="vRY Logo" src="../assets/logo.png" class="logo">
  <img src="../assets/PhoenixArtwork.png" alt="Phoenix" class="img phoenix">
  <img src="../assets/KilljoyArtwork.png" alt="Killjoy" class="img killjoy">
  <div class="lastUpdateDiv">
    <span class="lastUpdate">Last updated: </span>
    <span v-if="showTime" class="lastUpdateValue">{{ lastUpdateString }}</span>
    <div v-else class="noMatch">
        <span class="lastUpdateValue red">Couldn't fetch match or no match found in cache! Refresh the website or download vRY below</span>
        <button @click="hrefToDownload" class="btn vry-button btn--vry">
            <span class="btn__inner">
                <span class="btn__slide"></span>
                <span class="btn__content">Download vRY {{version}}</span>
            </span>
        </button>
    </div>
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
            Players: null,
            showTime: false,
            version: "0.00"
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

                if (this.lastUpdateSeconds < 0) {
                    this.showTime = false
                }
                else {
                    this.showTime = true
                }

            }, 1000)
        },
        getVersion() {
            fetch('https://api.github.com/repos/isaacKenyon/VALORANT-rank-yoinker/releases')
            .then(response => response.json())
            .then(data => {
                this.version = data[0].tag_name
                this.vryhref = data[0].assets[0].browser_download_url

                // console.log(this.version)
            })
        },

        hrefToDownload() {
            window.location.href = this.vryhref
        },
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
            let json = JSON.parse(event.data)
            // if json.type exists and is matchLoadout
            if (json.type == undefined || json.type == "matchLoadout" ) {
                self.loadoutJSON = json
                localStorage.clear()
                localStorage.setItem("loadoutJSON", JSON.stringify(self.loadoutJSON))
                self.Players = self.loadoutJSON.Players
                // self.lastUpdate = +new Date
                self.lastUpdate = self.loadoutJSON.time
                // console.log(+new Date)
                localStorage.setItem("lastUpdated", +new Date)
            }
        }

        connection.onopen = function() {
            console.log("Successfully connected to websocket server...")
        }

    },
    created() {
        this.getVersion()
    }

}
</script>

<style>
    .noMatch {
        display: flex;
        flex-direction: column;
    }
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

    .red {
        color: red;
    }

    #app {
        font-family: Avenir, Helvetica, Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-align: center;
        color: #2c3e50;
    }   

    .vry-button {
        margin-top: 4%;
    }

    .btn--vry {
        --button-background-color: var(--background-color);
        --button-text-color: var(--highlight-color);
        --button-inner-border-color: var(--highlight-color);
        --button-text-color-hover: #ece8e1;
        --button-bits-color-hover: #ece8e1;
    }
</style>