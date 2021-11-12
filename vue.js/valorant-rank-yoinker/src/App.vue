<template>
  <ul>
    <li>
      <router-link to="/">Home</router-link>
      <router-link to="/about">About</router-link>
    </li>
  </ul>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap">

  <match-loadouts/>

</template>

<script>
import MatchLoadouts from './components/MatchLoadouts.vue'

export default {
  name: 'App',
  components: { MatchLoadouts }
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
  /* margin: 0, auto; */
  width: 30%;
  /* height: 100%; */
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
  top: -30px;
  width: 30vmin;
  margin: 0, 0, 100px;
}

ul {
  list-style-type: none;
  margin: 0;
  padding: 0;
  overflow: hidden;
  background-color: #333;
}

li {
  float: left;
}

li a {
  display: block;
  color: white;
  text-align: center;
  padding: 14px 16px;
  text-decoration: none;
}

li a:hover {
  background-color: #111;
}


</style>
