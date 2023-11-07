<template>
  <div id="app">
    <nav>
      <router-link to="/">Home</router-link> |
      <router-link to="/about">About</router-link> |
      <router-link to="signup">Create account</router-link>
      <button v-if="isMobileDevice" @click="addToHomeScreen">
        Add to Home Screen
      </button>
    </nav>
    <router-view />
  </div>
</template>

<script>
export default {
  mounted: {
    isMobile() {
      // eslint-disable-next-line
      const isMobileDevice =
        /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
          navigator.userAgent
        );
    },
  },
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem("token");
    },
  },
  methods: {
    logout() {
      localStorage.removeItem("token");
      this.$router.push("/");
    },
    addToHomeScreen() {
      const promptEvent = window.addEventListener(
        "beforeinstallprompt",
        (event) => {
          event.preventDefault();
          const installPrompt = event;
          // Show the "Add to Home Screen" prompt
          installPrompt.prompt();
          // Wait for the user to respond to the prompt
          installPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === "accepted") {
              console.log("User accepted the A2HS prompt");
            } else {
              console.log("User dismissed the A2HS prompt");
            }
            // Clean up the event listener
            window.removeEventListener("beforeinstallprompt", promptEvent);
          });
        }
      );
    },
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
}

nav a.router-link-exact-active {
  color: #42b983;
}
</style>
