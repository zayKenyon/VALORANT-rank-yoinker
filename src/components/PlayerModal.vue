<template>
  <div class="modal-backdrop" @click.self="$emit('closeModal')">
      <div class="modal">
            <div class="flexbox flexbox-column">
                <div class="ModalDiv">
                    <span class="ModalText">{{ this.PlayerLoadout.AgentArtworkName.substring(0, this.PlayerLoadout.AgentArtworkName.length - 7) }}</span>
                </div>
                <div class="flexbox">
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="false" :visible="false" weaponName="none"/>
                    <!-- <div class="box flex-1"></div> -->
                    <div class="box flex-1 player-card">
                        <div class="levelDiv">
                            <span class="levelText">{{ this.PlayerLoadout.Level }}</span>
                        </div>



                        <div class="nameDiv">
                            <span class="nameText">{{ this.PlayerLoadout.AgentArtworkName.substring(0, this.PlayerLoadout.AgentArtworkName.length - 7) }}</span>
                        </div>


                        <div class="titleDiv">
                            <span class="titleText">{{ this.PlayerLoadout.Title }}</span>
                        </div>
                        <img v-if="PlayerCardIMG!==null" :src="PlayerCardIMG" alt="PlayerCard" class="PlayerCard">
                    </div>

                    <img :src="AgentArtworkPath" :alt="this.PlayerLoadout.AgentArtworkName" class="img-agent">

                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="false" :visible="true" weaponName="Classic"/>
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="true" :visible="true" weaponName="Stinger"/>
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="true" :visible="true" weaponName="Bulldog"/>
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="true" :visible="true" weaponName="Marshal"/>
                </div>
                <div class="flexbox">
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="false" :visible="false" weaponName="none"/>
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="false" :visible="true" weaponName="Shorty"/>
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="true" :visible="true" weaponName="Spectre"/>
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="true" :visible="true" weaponName="Guardian"/>
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="true" :visible="true" weaponName="Operator"/>
    
                </div>
                <div class="flexbox">
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="false" :visible="true" weaponName="Spray1"/>
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="false" :visible="true" weaponName="Frenzy"/>
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="true" :visible="true" weaponName="Bucky"/>
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="true" :visible="true" weaponName="Phantom"/>
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="true" :visible="true" weaponName="Ares"/>
    

                </div>
                <div class="flexbox">
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="false" :visible="true" weaponName="Spray2"/>
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="false" :visible="true" weaponName="Ghost"/>
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="true" :visible="true" weaponName="Judge"/>
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="true" :visible="true" weaponName="Vandal"/>
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="true" :visible="true" weaponName="Odin"/>
                </div>
                <div class="flexbox">
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="false" :visible="true" weaponName="Spray3"/>
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="false" :visible="true" weaponName="Sheriff"/>
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="true" :visible="false" weaponName="none"/>
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="true" :visible="false" weaponName="none"/>
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="true" :visible="true" weaponName="Melee"/>
                </div>

            </div>
          
          <!-- <p v-for="spray in PlayerLoadout.Sprays" :key="spray.displayName"> -->
              <!-- <img :src="spray.displayIcon" :alt="spray.displayName"> -->
          <!-- </p> -->
          <!-- <p>{{ PlayerLoadout }}</p> -->
      </div>
  </div>
</template>

<script>
import WeaponBox from './WeaponBox.vue'

export default {
    props: ["PlayerLoadout"],
    components: { WeaponBox },
    data() {
        return {
            PlayerCardIMG: null
        }
    },
    methods: {
        // attach images from Loadouts to flexboxes using theyre ID's
        attachImagesByID() {
        }
    },
    mounted() {
        this.PlayerCardIMG = this.PlayerLoadout.PlayerCard
        this.AgentArtworkPath = `../${this.PlayerLoadout.AgentArtworkName}.png`

    },
}
</script>

<style>
    p {
        font-size: 1.5em;
        font-weight: bold;
        text-align: center;
        color: black;
    }

    .modal {
        position: relative;
        width: 1400px;
        height: 800px;
        padding: 20px 20px 0;
        margin: 90px auto 10px;
        background-color: var(--inventory-background);
        border-radius: 10px;
        border: 2px solid black;
    }

    .modal-backdrop {
        padding: 0;
        margin: 0;
        top: 0;
        position: fixed;
        background: rgba(0, 0, 0, 0.2);
        width: 100%;
        height: 100%;
    }

    .player-card {
        z-index: 1;
        position: absolute;
        width: 165px;
        left: 20px;
        height: 286px;
    }
    .ModalDiv {
        position: absolute;
        top: -2.5%;
        left: 0;
        right: 0;
        margin: 0 auto;
        border-radius: 50px;
        width: 20%;
        height: 5%;
        background-color: var(--modal-text);
        border: 1px solid white;
        z-index: 1;
        box-sizing: border-box;
    }

    .ModalText {
        position: absolute;
        z-index: 2;
        font-size: 1em;
        font-weight: bold;
        left: 0;
        right: 0;
        top: 8px;
        bottom: 0;
        margin: auto;
        color: white;
    }

    .img-agent {
        position: fixed;
        top: 0;
        bottom: -10%;
        margin-top: auto;
        margin-bottom: auto;
        /* margin: 0, auto; */
        /* width: 30%; */
        height: 90%;
        /* height: 100%; */
        z-index: 0;
        opacity: 0.3;
    }
    
    .PlayerCard {
        width: 100%;
        height: 100%;
        object-fit: cover;
        padding: 0px;
        border-radius: 10px;
        box-sizing: border-box;
    }

    .levelDiv {
        position: absolute;
        width: 50%;
        height: 10%;
        top: -5%;
        left: 0;
        right: 0;
        left: 0;

        margin: 0 auto;
        background-color: var(--background-color);
        border-radius: 50px;
        border: 2px solid black;
        box-sizing: border-box;
    }

    .levelText {
        position: absolute;
        z-index: 2;
        font-size: 1.5em;
        color: white;
        font-weight: bold;
        top: 50%;
        left: 50%;
        transform: translate(-50% , -50%);
        -webkit-transform: translate(-50%, -50%);
    }

    .titleDiv {
        position: absolute;
        width: 100%;
        height: 5%;
        bottom: 28%;
        left: 0;
        right: 0;
        left: 0;

        margin: 0 auto;
        background-color: var(--placeholder-div);
        box-sizing: border-box;
    }

    .titleText {
        position: absolute;
        z-index: 2;
        font-size: 0.8em;
        color: var(--placeholder-text);
        font-weight: bold;
        top: 50%;
        left: 50%;
        transform: translate(-50% , -50%);
        -webkit-transform: translate(-50%, -50%);
    }

    .nameDiv {
        position: absolute;
        width: 100%;
        height: 5%;
        bottom: 33%;
        left: 0;
        right: 0;
        left: 0;

        margin: 0 auto;
        background-color: var(--name-div-color);
        box-sizing: border-box;
    }

    .nameText {
        position: absolute;
        z-index: 2;
        font-size: 0.8em;
        color: var(--placeholder-text);
        font-weight: bold;
        top: 50%;
        left: 50%;
        transform: translate(-50% , -50%);
        -webkit-transform: translate(-50%, -50%);
    }

</style>
