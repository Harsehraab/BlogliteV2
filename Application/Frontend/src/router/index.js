import Vue from "vue";
import VueRouter from "vue-router";
import HomeView from "../views/HomeView.vue";
import LoginForm from "../views/LoginForm.vue";
import UploadPost from "../views/UploadPost";
import MyFeed from "../views/MyFeed";
import SignUp from "../views/SignUp";
import AccountList from "../views/AccountList";
import ProfileView from "../views/ProfileView";
import MyPosts from "../views/MyPosts";
import AboutView from "../views/AboutView";
import ExportCSV from "../views/ExportCSV";
import LogOut from "../views/LogOut";
import ProfileOther from "../views/ProfileOther";

Vue.use(VueRouter);

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    {
      path: "/profile",
      name: "profile",
      component: ProfileView,
    },
    {
      path: "/profileother/:postid",
      name: "profileother",
      component: ProfileOther,
    },
    {
      path: "/feed",
      name: "post-list",
      component: MyFeed,
    },
    {
      path: "/myposts",
      name: "myposts",
      component: MyPosts,
    },
    {
      path: "/search",
      name: "search",
      component: AccountList,
    },
    {
      path: "/post",
      name: "post-create",
      component: UploadPost,
    },
    {
      path: "/signup",
      name: "signup",
      component: SignUp,
    },
    {
      path: "/login",
      name: "login",
      component: LoginForm,
    },
    {
      path: "/about",
      name: "about",
      component: AboutView,
    },
    {
      path: "/export",
      name: "export",
      component: ExportCSV,
    },
    {
      path: "/logout",
      name: "logout",
      component: LogOut,
    },
  ],
});

export default router;
