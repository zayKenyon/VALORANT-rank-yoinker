<template>
  <div class="match">
    <div class="match__team match__attacking-team">
      <PlayerCard :team="attackingTeam" />
    </div>
    <div class="match__divider">
      <template v-if="timeStamp">
        <p class="match__vs">vs</p>
        <p class="match__time">
          {{ new Date(timeStamp * 1000).toLocaleDateString() }}
        </p>
      </template>
      <template v-else>
        <p class="match__not-found"></p>
      </template>
    </div>
    <div class="match__team match__defending-team">
      <PlayerCard :team="defendingTeam" />
    </div>
  </div>
</template>

<script>
const PRIMARY_WEAPONS = ["Sheriff", "Phantom", "Vandal", "Melee"];
import PlayerCard from "@/components/PlayerCard.vue";
export default {
  components: { PlayerCard },
  mounted() {
    let connection = new WebSocket("ws://localhost:1100/");

    connection.onmessage = this.onMessage;

    connection.onerror = () => {
      this.timeStamp = null;
    };
  },
  data() {
    return {
      attackingTeam: [],
      defendingTeam: [],
      timeStamp: new Date().getTime() / 1000,
    };
  },
  methods: {
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

      console.log(this.defendingTeam);
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
.match {
  height: 100vh;
  padding: 1rem;

  display: grid;
  grid-template-columns: 1fr 50px 1fr;
  gap: 0.5rem;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    grid-template-rows: 1fr 50px 1fr;
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
  }

  &__defending-team {
    & > .player-card {
      border-right: 10px solid #61cba4;

      flex-direction: row-reverse;

      .player-card__agent-name {
        text-align: right;
      }
    }
  }
}
</style>
