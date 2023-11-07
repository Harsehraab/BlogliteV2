<template>
  <div>
    <nav>
      <router-link to="/feed">Feed</router-link>|
      <router-link to="/search">Search</router-link>|
      <router-link to="/myposts">MyPosts</router-link>|
      <router-link to="/profile">Profile</router-link>|
      <router-link to="/post">Create post</router-link>
    </nav>
    <h2>Account List</h2>
    <label for="id-field">Search Here:</label>
    <input id="id-field" v-model="searchstr" />
    <button @click="searchAccounts">Search</button>
    <ul>
      <li v-for="account in accounts" :key="account.id">
        {{ account.name }}
        <button @click="follow(account.id)">Follow</button>
        <button @click="unfollow(account.id)">Unfollow</button>
      </li>
    </ul>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      accounts: [],
      searchstr: "",
    };
  },
  mounted() {
    this.fetchAccounts();
  },
  methods: {
    searchAccounts() {
      const apiUrl = process.env.API_URL || "http://127.0.0.1:5000";
      const path = `${apiUrl}/searchaccounts`;
      axios
        .post(path, {
          searchStr: this.searchstr,
        })
        .then((response) => {
          this.accounts = response.data;
        })
        .catch((error) => {
          this.error = error.message || "Something went wrong.";
          console.error(error);
        });
    },
    fetchAccounts() {
      axios
        .get("http://127.0.0.1:5000/api/accounts")
        .then((response) => {
          this.accounts = response.data;
        })
        .catch((error) => {
          console.log(error);
        });
    },
    follow(id) {
      axios
        .post(`http://127.0.0.1:5000/accounts/${id}/follow`)
        .then(() => {
          this.fetchAccounts();
        })
        .catch((error) => {
          console.log(error);
        });
    },
    unfollow(id) {
      axios
        .post(`http://127.0.0.1:5000/accounts/${id}/unfollow`)
        .then(() => {
          this.fetchAccounts();
        })
        .catch((error) => {
          console.log(error);
        });
    },
  },
};
</script>
