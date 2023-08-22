<template>
  <div
    class="player-card"
    v-for="(player, playerIndex) in team"
    :key="`attacking-team-${playerIndex}`"
  >
    <div
      class="player-card__avatar"
      :style="{
        backgroundImage: `url(${player.Agent})`,
      }"
    ></div>
    <div class="player-card__info">
      <h1 class="player-card__agent-name">{{ player.Name }}</h1>
      <div class="player-card__weapons">
        <div
          v-for="(weapon, weaponIndex) in player.primaryWeapons"
          :key="`weapon-${weaponIndex}`"
          class="player-card__weapon"
        >
          <span :tooltip="weapon.skinDisplayName"
            ><img
              class="player-card__weapon-icon"
              :src="weapon.skinDisplayIcon"
          /></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    team: {
      type: Array,
      required: true,
    },
  },
};
</script>

<style lang="scss">
.player-card {
  width: 100%;
  max-width: 500px;
  min-width: 300px;
  height: 150px;

  background-color: #171717;
  color: white;

  display: flex;

  gap: 1rem;

  transition: all 0.2s ease-in-out;

  &:hover {
    cursor: pointer;
    transform: scale(1.05);
  }

  &__avatar {
    width: 150px;
    min-width: 150px;
    height: 100%;

    display: flex;
    align-items: center;
    justify-content: center;

    background-size: cover;
    background-position: top;
    background-repeat: no-repeat;
  }

  &__info {
    width: 100%;
  }

  &__weapons {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    width: 100%;

    color: #888;

    gap: 0.5rem;
  }

  &__weapon-icon {
    width: 65px;
    height: 65px;
    object-fit: contain;
  }
}
</style>
