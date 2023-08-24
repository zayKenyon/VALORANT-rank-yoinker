<template>
  <div>
    <InventoryModal
      :open="showInventory"
      :inventory="inventory"
      @close="handleCloseInventory"
    />
    <div class="nav-icons">
      <img
        class="nav-icons__icon"
        src="/favicon.ico"
        @click="openPage('vry')"
      />
      <img
        class="nav-icons__icon"
        src="/images/discord-logo.png"
        @click="openPage('discord')"
      />
      <img
        class="nav-icons__icon"
        src="/images/github.svg"
        @click="openPage('github')"
      />
    </div>
    <div class="match">
      <div class="match__team match__attacking-team">
        <PlayerCard
          :team="attackingTeam"
          @openInventory="handleShowInventory"
        />
      </div>
      <div class="match__divider">
        <p class="match__vs">vs</p>
        <p class="match__time" v-if="timeStamp">
          {{ momentAt(new Date(timeStamp * 1000)) }}
        </p>
      </div>
      <div class="match__team match__defending-team">
        <PlayerCard
          :team="defendingTeam"
          @openInventory="handleShowInventory"
        />
      </div>
    </div>
  </div>
</template>

<script>
import PlayerCard from "@/components/PlayerCard.vue";

import rawJson from "@/assets/json/match.json";

import InventoryModal from "@/components/InventoryModal.vue";

import { PRIMARY_WEAPONS } from "../utils/weapons";

import moment from "moment";

export default {
  components: { PlayerCard, InventoryModal },
  mounted() {
    let connection = new WebSocket("ws://localhost:1100/");

    connection.onmessage = this.onMessage;

    connection.onerror = () => {
      this.timeStamp = null;
    };

    if (this.attackingTeam.length == 0 && this.defendingTeam.length == 0) {
      this.onMessage({ data: JSON.stringify(rawJson) });
    }
  },
  data() {
    return {
      attackingTeam: [],
      defendingTeam: [],
      timeStamp: new Date().getTime() / 1000,
      showInventory: false,
      inventory: {},
      pages: {
        vry: "https://github.com/zayKenyon/VALORANT-rank-yoinker",
        github: "https://github.com/thurdev",
        discord: "https://discord.gg/kSCjdWKZfq",
      },
    };
  },
  methods: {
    openPage(type) {
      window.open(this.pages[type], "_blank");
    },
    momentAt(date) {
      return moment(date).fromNow();
    },
    handleShowInventory(player) {
      this.showInventory = true;
      this.inventory = player;
    },
    handleCloseInventory() {
      this.showInventory = false;
      this.inventory = {};
    },
    onMessage(event) {
      const { Players, time } = JSON.parse(event.data);

      this.timeStamp = time;

      this.attackingTeam = Object.values(Players)
        .filter((p) => p.Team == "Red")
        .map((p) => {
          return {
            ...p,
            primaryWeapons: this.filterWeapons(p.Weapons),
          };
        });
      this.defendingTeam = Object.values(Players)
        .filter((p) => p.Team == "Blue")
        .map((p) => {
          return {
            ...p,
            primaryWeapons: this.filterWeapons(p.Weapons),
          };
        });
    },
    filterWeapons(weapons) {
      return Object.values(weapons).filter((w) =>
        PRIMARY_WEAPONS.includes(w.weapon)
      );
    },
  },
};
</script>

<style lang="scss">
.nav-icons {
  position: absolute;
  top: 1%;
  right: 1%;

  display: flex;
  gap: 1rem;

  &__icon {
    width: 40px;
    filter: drop-shadow(1px 1px 5px #3131317c);
    cursor: pointer;

    transition: all 0.2s ease-in-out;

    &:hover {
      transform: scale(1.1);
    }
  }

  @media (max-width: 850px) {
    display: none;
  }
}
.match {
  height: 100vh;
  padding: 1rem;

  display: grid;
  grid-template-columns: 1fr 128px 1fr;
  gap: 0.5rem;

  @media (max-width: 1100px) {
    grid-template-columns: 1fr;
    grid-template-rows: 1fr 50px 1fr;

    row-gap: 2rem;

    height: 100%;
  }

  &__divider {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }

  &__vs {
    font-size: 50px;
    color: white;
    margin: 0;
  }

  &__time {
    color: #61cba4;
  }

  &__not-found {
    color: #ff5d57;
  }

  &__team {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    row-gap: 1rem;
  }

  &__attacking-team {
    & > .player-card {
      border-left: 10px solid #ff5d57;
    }

    .player-card__player-level {
      border: 2px solid #f3a7a4;
      border-top-color: #ff5d57;
      background-color: #572321;
      border-bottom-color: #ff5d57;
    }
  }

  &__defending-team {
    & > .player-card {
      border-right: 10px solid #61cba4;

      flex-direction: row-reverse;

      .player-card__agent-name {
        text-align: right;
      }

      .player-card__account {
        flex-direction: row-reverse;
      }

      .player-card__player-level {
        border: 2px solid #b4ffe3;
        border-top-color: #5ecca4;
        background-color: #1a3f32;
        border-bottom-color: #61cba4;
      }
    }
  }
}
</style>
