<template>
  <div>
    <nav>
      <router-link to="/feed">Feed</router-link>|
      <router-link to="/search">Search</router-link>|
      <router-link to="/myposts">MyPosts</router-link>|
      <router-link to="/profile">Profile</router-link>|
      <router-link to="/post">Create post</router-link>
    </nav>
    <h2>Upload a Photo</h2>
    <form accept-charset="UTF-8" @submit.prevent="submitForm">
      <div>
        <label for="photo">Choose a photo:</label>
        <input type="file" id="photo" ref="photo" accept="image/*" />
      </div>
      <div>
        <label for="caption">Caption:</label>
        <textarea id="caption" v-model="caption"></textarea>
      </div>
      <button type="submit">Upload</button>
    </form>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      id: "",
      caption: "",
    };
  },
  mounted() {
    this.getid();
  },
  methods: {
    submitForm() {
      let photo = this.$refs.photo.files[0];
      let formData = new FormData();
      formData.append("image", photo);
      formData.append("caption", this.caption);
      axios
        .post(`http://127.0.0.1:5000/api/users/${this.id}/posts`, formData, {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        })
        .then((response) => {
          console.log(response);
          this.$router.push("/feed");
        })
        .catch((error) => {
          console.log(error);
        });
    },
    getid() {
      axios
        .get("http://127.0.0.1:5000/getid")
        .then((response) => {
          this.id = response.data.id;
        })
        .catch((error) => {
          console.log(error);
        });
    },
  },
};
</script>
