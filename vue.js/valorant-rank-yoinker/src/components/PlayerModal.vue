<template>
  <div class="modal-backdrop" @click.self="$emit('closeModal')">
      <div class="modal">
            <div class="flexbox flexbox-column">
                <div class="flexbox">
                    <WeaponBox :PlayerLoadout="PlayerLoadout" :flex2="false" :visible="false" weaponName="none"/>
                    <!-- <div class="box flex-1"></div> -->
                    <div class="box flex-1 player-card">
                        <img src="" alt="" id="player-card">
                    </div>
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

        }
    },
    methods: {
        // attach images from Loadouts to flexboxes using theyre ID's
        attachImagesByID() {
            // for (let i = 0; i < Object.keys(this.PlayerLoadout.Weapons).length; i++) {
                // let weaponID = Object.keys(this.PlayerLoadout.Weapons)[i]
                // let skinArray = this.PlayerLoadout.Weapons[weaponID]
                // let skinElement = document.getElementById(skinArray.weapon);
                // skinElement.src = skinArray.displayIcon;                
                // let sprayID = spray.displayName.replace(/\s/g, '');
                // sprayImage.src = spray.displayIcon;
                // console.log(weapon.displayName);
            // }
        }
    },
    mounted() {
        this.attachImagesByID();
    }
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
        margin: 50px auto 10px;
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
</style>