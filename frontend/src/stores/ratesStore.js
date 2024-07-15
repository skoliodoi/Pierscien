import { defineStore } from "pinia";
import { useUsersStore } from "./usersStore.js";
import axios from "redaxios";
import config from "../config.js";
import * as XLSX from "xlsx";

export const useRatesStore = defineStore("rates", {
  state: () => {
    return {
      enteredFrom: "",
      view: "main",
      spin: false,
      spinMessage: "",
      returnView: "main",
      ratesView: "upload",
      showUpload: true,
      showResults: false,
      showLists: false,
      showSummary: false,
      messages: {
        responseMsg: "",
      },
      usersStore: useUsersStore(),
      datesToSelect: [],
      datesInListOfListsToSelect: [],
      projectSummary: [],
      totalSalary: null,
      listaDoZatwierdzenia: [],
      listaZatwierdzona: [],
      presentUsers: {},
      missingUsers: [],
      missingRates: [],
      missingRatesId: "",
      missingRatesDetails: [],
      dataWyslania: "",
      wysylacz: "",
      idZatwierdzenia: "",
    };
  },
  getters: {
    splitMsg(state) {
      return state.messages.responseMsg.split("|");
    },
  },
  actions: {
    rejectRates(reason, code, date) {
      this.usersStore.getUserData();
      axios
        .post(
          `${config.baseUrl}/api/reject_rates`,
          {
            code,
            date,
            reason,
            rejector: this.usersStore.loggedUser,
          },
          {
            headers: {
              accept: "application/json",
            },
          }
        )
        .then(() => {
          this.getLists();
          this.view = "lists";
          this.spin = false;
          this.spinMessage = "";
          this.showResults = false;
          $("body").toast({
            title: "Lista płac została odrzucona!",
            displayTime: 3000,
            class: "center aligned success",
            className: {
              title: "lotr-toast-header",
              toast: "lotr-toast",
            },
          });
        });
    },
    getProjects(date) {
      this.spin = true;
      axios
        .get(`${config.baseUrl}/api/get_projects/${date}`, {
          headers: {
            accept: "application/json",
          },
        })
        .then((res) => {
          const parsedData = JSON.parse(res.data);
          this.projectSummary = parsedData.projects;
          this.totalSalary = parsedData.combined;
          this.showSummary = true;
          this.spin = false;
        });
    },
    getDates() {
      axios
        .get(`${config.baseUrl}/api/get_dates`, {
          headers: {
            accept: "application/json",
          },
        })
        .then((res) => {
          const datesFromServer = JSON.parse(res.data);
          this.datesToSelect =
            datesFromServer.length > 0 ? datesFromServer : [];
          // if (datesFromServer.length > 0) {
          //   this.datesToSelect = datesFromServer;
          // }
        });
    },
    getLists() {
      this.usersStore.getUserData()
      axios
        .get(`${config.baseUrl}/api/find_lists/${this.usersStore.loggedUser}`, {
          headers: {
            Accept: "application/json",
          },
        })
        .then((res) => {
          this.listaDoZatwierdzenia = JSON.parse(res.data.do_zatwierdzenia);
          this.listaZatwierdzona = JSON.parse(res.data.zatwierdzone);
          let datyDoZatwierdzenia = [
            ...new Set(
              this.listaDoZatwierdzenia.map((a) => a.okres_rozliczenia)
            ),
          ];
          let datyZatwierdzone = [
            ...new Set(this.listaZatwierdzona.map((a) => a.okres_rozliczenia)),
          ];
          this.datesInListOfListsToSelect = [
            ...new Set(datyDoZatwierdzenia.concat(datyZatwierdzone)),
          ];
        })
        .catch((err) => {
          if (err.status == 403) {
            this.errors.status = true;
            this.errors.errMsg = err.data.message;
          }
        });
    },

    async wysylaczAction() {
      this.usersStore.getUserData();
      const payload = {
        dane: JSON.stringify(this.presentUsers),
        code: this.presentUsers.code,
        projectName: this.presentUsers.project_name,
        location: this.presentUsers.lokalizacja,
        timePeriod: this.presentUsers.time_period,
        sender: this.usersStore.loggedUser,
      };
      return axios
        .post(`${config.baseUrl}/api/upload_data`, payload, {
          headers: {
            Accept: "application/json",
          },
        })
        .then((res) => {
          this.messages.responseMsg = res.data;
          this.missingUsers = [];
          this.spin = false;
          this.spinMessage = "";
        })
        .catch((err) => {
          if (err.status == 403) {
            this.errors.status = true;
            this.errors.errMsg = err.data.message;
          }
        });
    },
    async zatwierdzaczAction() {
      this.usersStore.getUserData();
      const payload = {
        dane: JSON.stringify(this.presentUsers),
        zatwierdzenieId: this.idZatwierdzenia,
        osobaWysylajaca: this.wysylacz,
        osobaZatwierdzajaca: this.usersStore.loggedUser,
        dataWyslania: this.dataWyslania,
      };
      return axios
        .post(`${config.baseUrl}/api/zatwierdz_lp`, payload, {
          headers: {
            Accept: "application/json",
          },
        })
        .then((res) => {
          this.messages.responseMsg = res.data;
          this.spin = false;
          this.spinMessage = "";
        })
        .catch((err) => {
          if (err.status == 403) {
            this.errors.status = true;
            this.errors.errMsg = err.data.message;
          }
        });
    },
    async uploadData(val) {
      this.spin = true;
      if (val == "Zatwierdź") {
        this.spinMessage = "zatwierdzanie danych"
        return this.zatwierdzaczAction();
      } else {
        this.spinMessage = "wysyłanie danych do zatwierdzenia"
        return this.wysylaczAction();
      }
    },
    async getMissingFromMocarzDetails() {
      this.missingRatesDetails = [];
      return axios
        .post(
          `${config.baseUrl}/api/missing_ids_details`,
          {
            id: this.missingRatesId,
          },
          {
            headers: {
              Accept: "application/json",
            },
          }
        )
        .then((response) => {
          this.missingRatesDetails = JSON.parse(response.data);
        });
    },
    async getExcel() {
      this.missingRatesDetails = [];
      await this.getMissingFromMocarzDetails();
      const worksheet = XLSX.utils.json_to_sheet(this.missingRatesDetails);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, worksheet, "Szczegóły");
      const fileName = `Pierścień_brakujące_Mocarz_ID__${new Date().getTime()}.xlsx`;
      XLSX.writeFile(wb, fileName);
    },
  },
});
