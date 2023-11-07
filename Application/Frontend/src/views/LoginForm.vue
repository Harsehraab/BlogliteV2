<template>
  <div>
    <h2>Login</h2>
    <form @submit.prevent="submit">
      <div>
        <label for="name">Username :</label>
        <input type="text" id="email" v-model="name" required />
      </div>
      <div>
        <label for="password">Password:</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <button type="submit">Login</button>
    </form>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      name: "",
      password: "",
      error: "",
    };
  },
  mounted() {
    this.getid();
  },
  methods: {
    submit() {
      const apiUrl = process.env.API_URL || "http://127.0.0.1:5000";
      const path = `${apiUrl}/login`;

      axios
        .post(path, {
          name: this.name,
          password: this.password,
        })
        .then((response) => {
          console.log(response);
          localStorage.setItem("user_id", response.id);
          localStorage.setItem("token", response.token);
          this.$router.push("/feed");
        })
        .catch((error) => {
          this.error = error.message || "Something went wrong.";
          console.error(error);
        });
    },
  },
};
</script>
