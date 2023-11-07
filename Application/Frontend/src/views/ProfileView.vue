<template>
  <div>
    <nav>
      <router-link to="/feed">Feed</router-link>|
      <router-link to="/search">Search</router-link>|
      <router-link to="/myposts">MyPosts</router-link>|
      <router-link to="/profile">Profile</router-link>|
      <router-link to="/post">Create post</router-link>
    </nav>
    <h1>{{ user.username }}</h1>
    <img alt="Vue logo" src="../assets/logo.png" width="80" height="80" />
    <div>
      <div>
        <div>Posts</div>
        <div>{{ user.numPosts }}</div>

        <div>Followers</div>
        <div>{{ user.numFollowers }}</div>

        <div>Following</div>
        <div>{{ user.numFollowing }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      user: [],
    };
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      axios
        .get("http://127.0.0.1:5000/fetchdata")
        .then((response) => {
          this.user = response.data;
        })
        .catch((error) => {
          console.log(error);
        });
    },
  },
};
</script>

<style>
/* Profile page styles */
</style>
