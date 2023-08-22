<template>
  <div class="match">
    <div class="match__team match__attacking-team">
      <div
        class="player-card"
        v-for="(player, playerIndex) in attackingTeam"
        :key="`attacking-team-${playerIndex}`"
      >
        <div
          class="player-card__avatar"
          :style="{
            backgroundImage: `url(${player.avatar})`,
          }"
        ></div>
      </div>
    </div>
    <div class="match__divider">
      <p>vs</p>
    </div>
    <div class="match__team match__defending-team">
      <div
        class="player-card"
        v-for="(player, playerIndex) in defendingTeam"
        :key="`defending-team-${playerIndex}`"
      >
        <div
          class="player-card__avatar"
          :style="{
            backgroundImage: `url(${player.avatar})`,
          }"
        ></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      attackingTeam: [
        {
          avatar: "/RazeArtwork.png",
        },
        {
          avatar: "/CypherArtwork.png",
        },
        {
          avatar: "/JettArtwork.png",
        },
        {
          avatar: "/OmenArtwork.png",
        },
        {
          avatar: "/SovaArtwork.png",
        },
      ],
      defendingTeam: [
        {
          avatar: "/RazeArtwork.png",
        },
        {
          avatar: "/CypherArtwork.png",
        },
        {
          avatar: "/JettArtwork.png",
        },
        {
          avatar: "/OmenArtwork.png",
        },
        {
          avatar: "/SovaArtwork.png",
        },
      ],
    };
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

    align-items: center;
    justify-content: center;

    font-size: 50px;
    color: white;
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
      border-left: 3px solid #ff5d57;
    }
  }

  &__defending-team {
    & > .player-card {
      border-right: 3px solid #61cba4;

      flex-direction: row-reverse;
    }
  }
}
.player-card {
  width: 100%;
  max-width: 500px;
  min-width: 300px;
  height: 150px;

  background-color: #171717;

  display: flex;

  &__avatar {
    width: 150px;
    height: 100%;

    display: flex;
    align-items: center;
    justify-content: center;

    background-size: cover;
    background-position: -150px -25px;
    background-repeat: no-repeat;
    background-size: 300%;
  }
}
</style>
