<template>
  <div>
    <nav>
      <router-link to="/feed">Feed</router-link>|
      <router-link to="/search">Search</router-link>|
      <router-link to="/myposts">MyPosts</router-link>|
      <router-link to="/profile">Profile</router-link>|
      <router-link to="/post">Create post</router-link>
    </nav>
    <h2>My Posts</h2>

    <ul>
      <li v-for="(data, id) in posts" :key="id">
        <h3>{{ id }}</h3>
        <ul>
          <li v-for="(caption, url) in data" :key="url">
            <h3>Post url{{ url }}</h3>
            <img
              :src="url"
              alt="picture"
              style="max-width: 80%; max-height: 80%"
            />
            <h3>Caption : {{ caption }}</h3>
            <button @click="deletepost">Delete</button>
            <label v-if="deleting" for="delete-field"
              >Are you sure you want to delete this post? Enter Post ID:</label
            >
            <input v-if="deleting" id="delete-field" v-model="postid" />
            <button v-if="deleting" @click="confirm">Confirm</button>

            <button @click="edit">Edit</button>
            <label v-if="editing" for="id-field">Post ID:</label>
            <input v-if="editing" id="id-field" v-model="postid" />
            <label v-if="editing" for="caption-field">New Caption:</label>
            <input v-if="editing" id="caption-field" v-model="newCaption" />

            <button v-if="editing" @click="save">Save</button>

            <button @click="exports">Export</button>
            <label v-if="exporting" for="export-field"
              >Are you sure you want to export this post? Enter Post ID:</label
            >
            <input v-if="exporting" id="export-field" v-model="postid" />
            <button v-if="exporting" @click="exported">Confirm</button>

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
      postid: "",
      editing: false,
      newCaption: "",
      response: "",
      deleting: false,
      exporting: false,
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
      const path = `${apiUrl}/getmyposts`;
      axios
        .get(path)
        .then((response) => {
          this.posts = response.data;
        })
        .catch((error) => {
          console.log(error);
        });
    },
    exports() {
      this.exporting = true;
    },
    exported() {
      this.exporting = false;
      const apiUrl = process.env.API_URL || "http://127.0.0.1:5000";
      const path = `${apiUrl}/exportpost`;
      axios
        .post(path, {
          id: this.postid,
        })
        .then((response) => {
          const blob = new Blob([response.data], { type: "text/csv" });
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = url;
          link.download = "export.csv";
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
        })
        .catch((error) => {
          this.error = error.message || "Something went wrong.";
          console.error(error);
        });
    },
    deletepost() {
      this.deleting = true;
    },
    confirm() {
      alert("The post has been deleted!");
      this.deleting = false;
      const apiUrl = process.env.API_URL || "http://127.0.0.1:5000";
      const path = `${apiUrl}/deletepost`;
      axios
        .post(path, {
          id: this.postid,
        })
        .then((response) => {
          this.response = response.data;
          this.$router.push("/myposts");
        })
        .catch((error) => {
          this.error = error.message || "Something went wrong.";
          console.error(error);
        });
    },
    edit() {
      this.editing = true;
      this.newCaption = "";
    },
    save() {
      this.editing = false;
      const apiUrl = process.env.API_URL || "http://127.0.0.1:5000";
      const path = `${apiUrl}/editcaption`;

      axios
        .post(path, {
          id: this.postid,
          caption: this.newCaption,
        })
        .then((response) => {
          this.response = response.data;
          this.$router.push("/myposts");
        })
        .catch((error) => {
          this.error = error.message || "Something went wrong.";
          console.error(error);
        });
    },
  },
};
</script>
