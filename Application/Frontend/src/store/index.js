import Vue from "vue";
import Vuex from "vuex";
import axios from "axios";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    user: null,
    id: null,
  },
  mutations: {
    setUser(state, user) {
      state.user = user;
    },
    setID(state, id) {
      state.id = id;
    },
    setAccountId(state, id) {
      state.accountId = id;
    },
    setAccounts(state, accounts) {
      state.accounts = accounts;
    },
    followAccount(state, accountId) {
      let account = state.accounts.find((a) => a.id === accountId);
      if (account) {
        account.followed = true;
      }
    },
    unfollowAccount(state, accountId) {
      let account = state.accounts.find((a) => a.id === accountId);
      if (account) {
        account.followed = false;
      }
    },
  },
  actions: {
    async fetchUser({ commit }) {
      try {
        const response = await axios.get("/api/user");
        const user = response.data.user;
        commit("setUser", user);
      } catch (error) {
        console.error(error);
      }
    },
    async logout({ commit }) {
      try {
        await axios.post("/api/logout");
        commit("setUser", null);
      } catch (error) {
        console.error(error);
      }
    },
    fetchid({ commit }) {
      axios.get("/getid").then((response) => {
        commit("setId", response.id);
      });
    },
    fetchAccounts({ commit }) {
      axios.get("/accounts").then((response) => {
        commit("setAccounts", response.data);
      });
    },
    followAccount({ commit }, accountId) {
      axios.post(`/accounts/${accountId}/follow`).then(() => {
        commit("followAccount", accountId);
      });
    },
    unfollowAccount({ commit }, accountId) {
      axios.post(`/accounts/${accountId}/unfollow`).then(() => {
        commit("unfollowAccount", accountId);
      });
    },
  },
  modules: {
    // ...
  },
});
