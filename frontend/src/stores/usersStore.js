import { defineStore } from "pinia";
import axios from "redaxios";
import config from "../config.js";

export const useUsersStore = defineStore("users", {
  state: () => {
    return {
      loggedUser: "",
      loggedUserAccess: "",
      loggedUserName: "",
      liczbaZatwierdzen: 0,
      daneZatwierdzen: [],
      errors: {
        status: false,
        errMsg: "",
      },
    };
  },
  getters: {
    lowerAccess: (state) =>
      state.loggedUserAccess == "*" ||
      state.loggedUserAccess == "wysylacz" ||
      state.loggedUserAccess == "zatwierdzacz"
        ? true
        : false,
    higherAccess: (state) =>
      state.loggedUserAccess == "*" || state.loggedUserAccess == "zatwierdzacz"
        ? true
        : false,
    multisportAccess: (state) =>
      state.loggedUserAccess == "*" || state.loggedUserAccess == "multilux"
        ? true
        : false,
    summaryAccess: (state) =>
      state.loggedUserAccess == "*" || state.loggedUserAccess == "podsumowanie"
        ? true
        : false,
  },
  actions: {
    getUserData() {
      this.loggedUser = sessionStorage.getItem("login");
      this.loggedUserAccess = sessionStorage.getItem("access");
      this.loggedUserName = sessionStorage.getItem("name");
    },
    async checkUser(userName, userPass) {
      return axios
        .post(
          `${config.baseUrl}/api/check_user`,
          {
            login: userName,
            password: userPass,
          },
          {
            headers: {
              Accept: "application/json",
            },
          }
        )
        .then((res) => {
          this.loggedUser = userName;
          sessionStorage.setItem("login", userName);
          this.loggedUserAccess = res.data.access;
          sessionStorage.setItem("access", res.data.access);
          this.loggedUserName = res.data.name;
          sessionStorage.setItem("name", res.data.name);
          return res.data;
          // const dbZatwierdzenia = JSON.parse(res.data);
          // this.liczbaZatwierdzen = dbZatwierdzenia.length;
          // this.daneZatwierdzen = dbZatwierdzenia;
        })
        .catch((err) => {
          return {
            error: true,
            errMsg: err.data.message,
            errStat: err.data.status,
          };
        });
    },
  },
});
