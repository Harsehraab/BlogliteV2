<template>
  <div>
    <nav>
      <router-link to="/feed">Feed</router-link>|
      <router-link to="/search">Search</router-link>|
      <router-link to="/myposts">MyPosts</router-link>|
      <router-link to="/profile">Profile</router-link>|
      <router-link to="/post">Create post</router-link>|
      <router-link to="/export">Export</router-link>|
      <router-link to="http://127.0.0.1:5000/logout">Logout</router-link>
    </nav>
    <h2>Feed</h2>

    <div v-if="posts.length === 0">No more posts found.</div>
    <ul>
      <li v-for="(data, id) in posts" :key="id">
        <h3>{{ id }}</h3>
        <button @click="visit(id)">Visit</button>
        <ul>
          <li v-for="(caption, url) in data" :key="url">
            <h3>{{ url }}</h3>
            <img
              :src="url"
              alt="photo"
              style="max-width: 80%; max-height: 80%"
            />
            <h3>{{ caption }}</h3>
            <div v-html="sanitizedContent">Caption : {{ caption }}</div>
          </li>
        </ul>
      </li>
    </ul>
  </div>
</template>

<script>
import axios from "axios";
import DOMPurify from "dompurify";

export default {
  data() {
    return {
      photoUrl: "",
      posts: [],
    };
  },
  mounted() {
    this.getPosts();
  },
  computed: {
    sanitizedContent() {
      return DOMPurify.sanitize(this.content, {
        ALLOWED_TAGS: [
          "a",
          "abbr",
          "acronym",
          "b",
          "blockquote",
          "code",
          "em",
          "i",
          "li",
          "ol",
          "pre",
          "strong",
          "ul",
          "h1",
          "h2",
          "h3",
          "h4",
          "h5",
          "h6",
          "p",
        ],
      });
    },
  },
  methods: {
    getPosts() {
      const apiUrl = process.env.API_URL || "http://127.0.0.1:5000";
      const path = `${apiUrl}/getposts`;
      axios
        .get(path)
        .then((response) => {
          this.posts = response.data;
        })
        .catch((error) => {
          console.log(error);
        });
    },
    visit(id) {
      this.$router.push(`/profileother/${id}`);
    },
    getImagePath(url) {
      return require(`${url}`);
    },
  },
};
</script>
