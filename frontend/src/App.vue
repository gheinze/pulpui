<script setup>

import Distributions from './components/Distributions.vue'

</script>

<template>
  <h1>Pulp UI</h1>
  <!-- <img alt="Vue logo" src="./assets/logo.png" /> -->
  <Distributions/>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  margin-top: 60px;
}

  body {
      margin: 0;
      height: 100%;
      overflow-x: hidden;
      overflow-y: auto;
      background-color: var(--surface-a);
      font-family: var(--font-family);
      color: var(--text-color);
   }
   
</style>
