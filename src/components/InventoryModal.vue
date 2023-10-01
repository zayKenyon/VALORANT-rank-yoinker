<template>
  <div>
    <transition name="modal">
      <div class="inventory" v-if="showModal">
        <button class="inventory__close" @click="showModal = false">
          <span>X</span>
        </button>
        <div class="inventory__weapons-wrapper">
          <div class="inventory__sidearms">
            <h2>SIDEARMS</h2>
            <div
              class="inventory__weapon-card"
              v-for="sidearm in formattedInventory.sideArms"
              :key="sidearm.skin"
            >
              <img
                class="inventory__weapon-image"
                :src="sidearm.skinDisplayIcon"
              />
              <p class="inventory__weapon-name">
                {{ sidearm.skinDisplayName }}
              </p>
            </div>
          </div>
        </div>

        <div class="inventory__weapons-wrapper">
          <div class="inventory__smgs">
            <h2>SMGS</h2>
            <div
              class="inventory__weapon-card"
              v-for="smg in formattedInventory.smgs"
              :key="smg.skin"
            >
              <img class="inventory__weapon-image" :src="smg.skinDisplayIcon" />
              <p class="inventory__weapon-name">
                {{ smg.skinDisplayName }}
              </p>
            </div>
          </div>
          <div class="inventory__shotguns">
            <h2>SHOTGUNS</h2>
            <div
              class="inventory__weapon-card"
              v-for="shotgun in formattedInventory.shotguns"
              :key="shotgun.skin"
            >
              <img
                class="inventory__weapon-image"
                :src="shotgun.skinDisplayIcon"
              />
              <p class="inventory__weapon-name">
                {{ shotgun.skinDisplayName }}
              </p>
            </div>
          </div>
        </div>

        <div class="inventory__weapons-wrapper">
          <div class="inventory__rifles">
            <h2>RIFLES</h2>
            <div
              class="inventory__weapon-card"
              v-for="rifle in formattedInventory.rifles"
              :key="rifle.skin"
            >
              <img
                class="inventory__weapon-image"
                :src="rifle.skinDisplayIcon"
              />
              <p class="inventory__weapon-name">
                {{ rifle.skinDisplayName }}
              </p>
            </div>
          </div>
          <div class="inventory__melee">
            <h2>MELEE</h2>
            <div
              class="inventory__weapon-card"
              v-for="melee in formattedInventory.melee"
              :key="melee.skin"
            >
              <img
                class="inventory__weapon-image"
                :src="melee.skinDisplayIcon"
              />
              <p class="inventory__weapon-name">
                {{ melee.skinDisplayName }}
              </p>
            </div>
          </div>
        </div>

        <div class="inventory__weapons-wrapper">
          <div class="inventory__snipers-rifles">
            <h2>SNIPER RIFLES</h2>
            <div
              class="inventory__weapon-card"
              v-for="sniper in formattedInventory.snipers"
              :key="sniper.skin"
            >
              <img
                class="inventory__weapon-image"
                :src="sniper.skinDisplayIcon"
              />
              <p class="inventory__weapon-name">
                {{ sniper.skinDisplayName }}
              </p>
            </div>
          </div>

          <div class="inventory__machine-guns">
            <h2>MACHINE GUNS</h2>
            <div
              class="inventory__weapon-card"
              v-for="machineGun in formattedInventory.machineGuns"
              :key="machineGun.skin"
            >
              <img
                class="inventory__weapon-image"
                :src="machineGun.skinDisplayIcon"
              />
              <p class="inventory__weapon-name">
                {{ machineGun.skinDisplayName }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import {
  SIDEARMS_WEAPONS,
  SMGS,
  SHOTGUNS,
  RIFLES,
  MELEE,
  SNIPERS,
  MACHINE_GUNS,
  filterWeapons,
} from "@/utils/weapons";

export default {
  mounted() {
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        this.showModal = false;
      }
    });
  },
  props: {
    open: {
      type: Boolean,
      required: true,
    },
    inventory: {
      type: Object,
      required: true,
    },
  },
  methods: {},
  computed: {
    showModal: {
      get() {
        return this.open;
      },
      set(val) {
        this.$emit("close", val);
      },
    },
    formattedInventory() {
      return {
        sideArms: filterWeapons(this.inventory.Weapons, SIDEARMS_WEAPONS),
        smgs: filterWeapons(this.inventory.Weapons, SMGS),
        shotguns: filterWeapons(this.inventory.Weapons, SHOTGUNS),
        rifles: filterWeapons(this.inventory.Weapons, RIFLES),
        melee: filterWeapons(this.inventory.Weapons, MELEE),
        snipers: filterWeapons(this.inventory.Weapons, SNIPERS),
        machineGuns: filterWeapons(this.inventory.Weapons, MACHINE_GUNS),
      };
    },
  },
};
</script>

<style lang="scss">
.inventory {
  width: 100%;
  height: auto;
  padding-bottom: 2rem;

  @media (min-width: 1045px) and (max-width: 1100px) {
    height: 100%;
  }

  @media (min-width: 1101px) {
    height: 100dvh;
  }

  position: fixed;
  z-index: 1;
  top: 0;
  left: 0;

  color: white;

  transition: opacity 0.3s ease;

  display: flex;
  justify-content: center;

  gap: 3rem;

  background-color: rgba(0, 0, 0, 0.98);
  backdrop-filter: blur(15px);

  @media (max-width: 1400px) {
    flex-wrap: wrap;
  }

  &__close {
    display: flex;
    align-items: center;
    justify-content: center;

    position: absolute;
    left: 2%;
    top: 2%;

    border: none;
    border-radius: 50%;

    background-color: rgba(0, 0, 0, 0.3);
    color: white;

    font-size: 2rem;

    cursor: pointer;
  }

  &__weapons-wrapper {
    display: flex;
    flex-direction: column;

    gap: 1rem;

    & div {
      display: flex;
      flex-direction: column;

      text-align: center;

      h2 {
        padding: 0;
        margin: 1.5rem 0 0 0;
        user-select: none;
      }

      gap: 1rem;
    }
  }

  &__weapon-card {
    width: 305px;
    height: 130px;

    display: flex;
    align-items: center;
    justify-content: center;

    border: 3px solid rgba(255, 255, 255, 0.3);
    background-color: rgba(255, 255, 255, 0.2);

    transition: border 0.2s ease-in-out;

    overflow: clip;

    position: relative;

    &::before {
      content: "";
      position: absolute;

      transform: rotate(45deg);
      background-color: rgba(255, 255, 255, 0.2);

      top: -25px;
      left: -25px;

      width: 50px;
      height: 50px;

      transition: background 0.15s ease-in;
    }

    &:hover {
      border: 3px solid #61cba4;
      background: linear-gradient(
        180deg,
        rgba(255, 255, 255, 0.2) 65%,
        #61cba48a 100%
      );

      &::before {
        background-color: #61cba4;
      }

      .inventory__weapon-image {
        -webkit-filter: drop-shadow(0px 8px 0px #222);
        filter: drop-shadow(0px 8px 0px #222);
      }

      .inventory__weapon-name {
        color: white;
      }
    }
  }

  &__melee {
    .inventory__weapon-image {
      width: 100px;
    }
  }

  &__rifles,
  &__snipers-rifles,
  &__machine-guns,
  &__shotguns,
  &__smgs {
    .inventory__weapon-image {
      width: 250px;
    }
  }

  &__weapon-image {
    width: 150px;

    transition: all 0.2s ease-in-out;
  }

  &__weapon-name {
    position: absolute;
    left: 6px;
    bottom: -10px;
    color: rgba(194, 194, 194, 0.8);

    user-select: none;
  }
}

.modal-enter {
  opacity: 0;
}

.modal-leave-active {
  opacity: 0;
}

.modal-enter .modal-container,
.modal-leave-active .modal-container {
  -webkit-transform: scale(1.1);
  transform: scale(1.1);
}
</style>
