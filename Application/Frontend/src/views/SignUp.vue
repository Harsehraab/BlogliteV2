<template>
  <div>
    <h2>Sign Up</h2>
    <form @submit.prevent="submit">
      <div>
        <label for="name">Name:</label>
        <input type="text" id="name" v-model="name" required />
      </div>
      <div>
        <label for="email">Email:</label>
        <input type="email" id="email" v-model="email" required />
      </div>
      <div>
        <label for="password">Password:</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <button type="submit">Sign Up</button>
    </form>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      name: "",
      email: "",
      password: "",
      error: "",
    };
  },
  methods: {
    submit() {
      const apiUrl = process.env.API_URL || "http://127.0.0.1:5000";
      const path = `${apiUrl}/signup`;

      axios
        .post(path, {
          name: this.name,
          email: this.email,
          password: this.password,
        })
        .then((response) => {
          console.log(response);
          this.$router.push("/login");
        })
        .catch((error) => {
          this.error = error.message || "Something went wrong.";
          console.error(error);
        });
    },
  },
};
</script>
