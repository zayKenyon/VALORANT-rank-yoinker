<template>
  <!-- <div id="nav">
    <router-link to="/">Home</router-link>
    <router-link to="/matchLoadouts">Match Loadouts</router-link>
    <a @click="redirectToGithub" class="github">GitHub</a>
    <a @click="redirectToDiscord" class="github">Discord</a>
  </div> -->
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

<style>
body {
  background-color: #222222;
}
</style>
