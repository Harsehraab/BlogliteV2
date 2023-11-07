<template>
  <div>
    <h2>Export Blogs as CSV</h2>
    <button @click="exportBlogs">Export</button>
    <button @click="dailymail">Sample Daily Mail</button>
    <button @click="monthlymail">Sample Monthly Mail</button>
  </div>
</template>

<script>
import axios from "axios";

/* eslint-disable */
export default {
  methods: {
    exportBlogs() {
      axios
        .post("http://127.0.0.1:5000/export/csv")
        .then((response) => {
          alert(
            "Export job has been triggered. You will receive an email when the job is complete."
          );
        })
        .catch((error) => {
          console.log(error);
        });
    },
    dailymail() {
      axios
        .post("http://127.0.0.1:5000/dailymail")
        .then((response) => {
          alert(
            "You will receive a daily email when the job is complete."
          );
        })
        .catch((error) => {
          console.log(error);
        });
    },
    monthlymail() {
      axios
        .post("http://127.0.0.1:5000/monthlymail")
        .then((response) => {
          alert(
            "You will receive a monthlymail email when the job is complete."
          );
        })
        .catch((error) => {
          console.log(error);
        });
    },
  },
};
</script>
