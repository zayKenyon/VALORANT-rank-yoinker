<template>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap">


  <div id="nav">
    <router-link to="/">Home</router-link>
    <router-link to="/matchLoadouts">Match Loadouts</router-link>
    <a @click="redirectToGithub" class="github">GitHub</a>
    <a @click="redirectToDiscord" class="github">Discord</a>
    <!-- <a @click="console.log('test')/> -->
  </div>
  <router-view/>
</template>


<script>
export default {
  name: 'App',
  methods: {
    redirectToGithub() {
      window.open('https://github.com/isaacKenyon/VALORANT-rank-yoinker')
    },
    redirectToDiscord() {
      window.open('https://discord.gg/HeTKed64Ka')
    },
  }
}
</script>



<style>
#app {
  font-family: "Inter";
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #151418;
  margin-top: 60px;
}
body {
  position: relative;
  margin: 0;
  padding: 0;
  background-color: var(--background);
  /* background-image: url('./assets/PhoenixArtwork.png'); */
  /* background-repeat: no-repeat; */
  /* background-attachment: fixed; */
  /* background-position: left; */
  
}
.img {
  position: fixed;
  top: 0;
  bottom: 0;
  margin-top: auto;
  margin-bottom: auto;
  width: 30%;
  z-index: -1;
  opacity: 0.5;
}
.phoenix {
  left: 50px;
  /* background-color: red; */
}
.killjoy {
  right: 50px;
  /* background-color: red; */
}
.logo {
  position: relative;
  top: 0;
  margin-bottom: 25px;
  width: 30vmin;
  margin: 0, 0, 100px;
}

#nav {
  position: fixed;
  top: 0;
  z-index: 2;
  height: 5%;
  /* padding: 100px; */
  /* list-style-type: none; */
  margin: 0;
  padding: 0;
  width: 100%;
  text-align: left;
  /* overflow: hidden; */
  background-color: #111111;
  /* box-sizing: border-box; */
}

#nav a {
  position: relative;
  top: 30%;
  /* bottom: 0; */
  /* margin: auto; */
  /* vertical-align: middle; */
  padding: 1%;
  font-weight: bold;
  color: #2c3e50;
  /* display: block; */
  color: white;
  /* text-align: center; */
  /* padding: 14px 16px; */
  text-decoration: none;
  /* border-bottom: 2px solid #111111; */
}

#nav a.router-link-exact-active {
  border-bottom: 1px solid #ff4655;
}

#nav a:hover {
  /* background-color: #ff4655; */
  border-bottom: 1px solid #ff4655;
  /* -webkit-box-shadow:inset 0px 0px 0px 1px #ff4655; */
  /* -moz-box-shadow:inset 0px 0px 0px 1px #ff4655; */
  /* box-shadow:inset 0px -10px 1px 0px #ff4655; */
}

.github {
  cursor: pointer;
}
</style>
