<template>
  <div :class="{ box: visible,
                'box-invisible': !visible,
                'flex-2': flex2,
                'flex-1': !flex2 }"
                :id="weaponName">
      <img v-if="imgPath!==null" :src="imgPath" :alt="weaponName" :class="{sprayIMG: isSpray, 'weaponIMG': !isSpray}">
      <div v-if="imgPath!==null" class="placeholderDiv">
        <span class="placeholderText">{{skinDisplayName}}</span>
      </div>
      <img v-if="buddyIMG!==null" :src="buddyIMG" alt="skin_buddy" class="buddyIMG">
  </div>
</template>

<script>
export default {
    props: ["PlayerLoadout", "flex2", "visible", "weaponName"],
    mounted() {
        for (let i = 0; i < Object.keys(this.PlayerLoadout.Weapons).length; i++) {
            let weaponID = Object.keys(this.PlayerLoadout.Weapons)[i]
            let skinArray = this.PlayerLoadout.Weapons[weaponID]
            if (skinArray["weapon"] == this.weaponName) {
                this.imgPath = skinArray.skinDisplayIcon
                this.skinDisplayName = skinArray.skinDisplayName
                if (skinArray.buddy_displayIcon) {
                    this.buddyIMG = skinArray.buddy_displayIcon
                }
                this.buddyIMG
            }
        }
        if (this.weaponName.startsWith("Spray")) {
            let index = Object.keys(this.PlayerLoadout.Sprays)[(this.weaponName.substring(5, 6)) - 1]
            this.imgPath = this.PlayerLoadout.Sprays[index].displayIcon
            this.isSpray = true
            this.skinDisplayName = this.PlayerLoadout.Sprays[index].displayName

        } 
    },
    data() {
        return {
            imgPath: null,
            isSpray: false,
            skinDisplayName: null,
            buddyIMG: null,
        }
    }
}
</script>

<style>
    .box {
        /* display: flex; */
        box-sizing: border-box;
        position: relative;
        width: 100px;
        height: 130px;
        background-color: var(--inventory-slot);
        border: 1px solid rgb(134, 134, 134);
        border-radius: 5px;
        margin: 0 7px;
        transition-duration: 0.1s;
        cursor: pointer;
    }

    .box:hover {
        padding: 5px;
        background-color: var(--inventory-slot-hover);
    }

    .box:hover .placeholderDiv{
        padding: 0 5px;
        left: -5px;
        margin: 111px 0;
    }

    .box-invisible {
        width: 100px;
        height: 130px;
        border-radius: 5px;
        margin: 0 8px;
    }

    .flexbox {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-around;
    }
    
    .flexbox-column {
        height: 780px;
        flex-direction: column;

    }
    .flex-1 {
        flex: 1;
    }

    .flex-2 {
        flex: 2;
    }

    .weaponIMG {
        position: absolute;
        width: 100%;
        /* height: 100%; */
        /* object-fit: cover; */
        top: 0;
        bottom: 0;
        margin: auto;
        left: 0;
        box-sizing: border-box;
        padding: 3px;
    }

    .sprayIMG {
        position: absolute;
        width: 75%;
        top: 0;
        bottom: 0;
        left: 0;
        right: 0;
        margin: auto;
        box-sizing: border-box;
        
        border-radius: 10px;
        /* border: 1px solid black; */
    }
    
    .placeholderDiv {
        position: relative;
        background-color: var(--placeholder-div);
        z-index: 2;
        width: 100%;
        height: 10%;
        margin: 115px 0;
        left: 0;
        transition-duration: 0.1s;
    }

    .placeholderText {
        position: absolute;
        font-size: 0.8em;
        font-weight: bold;
        left: 0;
        right: 0;
        margin: auto;
        top: -1px;
        color: var(--placeholder-text);
        transition-duration: 0.1s;
    }

    .box:hover .placeholderText {
        top: -2px;
    }

    .buddyIMG {
        z-index: 3;
        position: absolute;
        bottom: 2%;
        left: 0;
        width: 18%;
    }


</style>