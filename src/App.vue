<template>
  <router-view />
</template>

<script>
export default {
  name: "App",
  methods: {
    redirectToGithub() {
      window.open("https://github.com/isaacKenyon/VALORANT-rank-yoinker");
    },
    redirectToDiscord() {
      window.open("https://discord.gg/HeTKed64Ka");
    },
  },
};
</script>

<style lang="scss">
body {
  background: url("https://progioco.com/wp-content/uploads/2023/03/Confermata-la-versione-beta-globale-di-Valorant-Premier-nuova-modalita.jpg");
  background-size: cover;
  background-repeat: no-repeat;
  background-position: center;
  background-attachment: fixed;

  backdrop-filter: blur(15px);

  overflow: hidden;

  @media (max-width: 1100px) {
    overflow: unset;
    overflow-x: hidden;
  }
}

@import "@/assets/styles/tooltip.scss";
</style>
