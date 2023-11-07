<template>
  <div class="home">
    <nav>
      <router-link to="/login">Login</router-link>
    </nav>
    <div>
      <img alt="Vue logo" src="../assets/logo.png" width="80" height="80" />
      <HelloWorld msg="Welcome to Bloglite App" />
    </div>
  </div>
</template>

<script>
// @ is an alias to /src
import HelloWorld from "@/components/HelloWorld.vue";

export default {
  name: "HomeView",
  components: {
    HelloWorld,
  },
};
</script>
