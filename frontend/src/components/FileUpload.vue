<template>
  <button
    class="ui button lotr-inverted"
    style="margin: 10px 0 0 10px"
    @click="store.$state = { view: store.returnView }"
  >
    Wróć
  </button>
  <FileUploadModal :code="errors.errorCode" :message="errors.errorModalMsg" />
  <div class="main-page-container" :class="{ 'error-bg': errors.status }">
    <div class="ui container file-upload-container">
      <h1 class="ui huge header" v-if="errors.status">{{ errors.errMsg }}</h1>
      <div class="upload-box">
        <ScaryBilbo v-if="errors.status" />
        <PierscienIcon :class="{ spinning: isUploading }" v-else />
      </div>
      <div id="input" v-if="!isUploading">
        <div class="input-container">
          <div class="input-container-corset">
            <div></div>
            <div class="ui file action input">
              <label for="pierscienFileInput" class="ui button lotr">
                <i class="file alternate icon"></i>
                Godziny
              </label>
              <button
                for="pierscienFileInput"
                class="ui button lotr"
                @click="cancelAdding('base')"
                v-if="file"
              >
                <i class="times alternate icon"></i>
                Usuń
              </button>
              <input
                id="pierscienFileInput"
                type="file"
                @change="handleFile('base', $event)"
              />
            </div>
            <div class="ui file action input" v-if="addBonus">
              <input
                id="pierscienBonusInput"
                type="file"
                @change="handleFile('bonus', $event)"
              />
              <button
                for="pierscienBonusInput"
                class="ui button lotr"
                @click="cancelAdding('bonus')"
                v-if="bonusFile"
              >
                <i class="times alternate icon"></i>
                Usuń
              </button>
              <label for="pierscienBonusInput" class="ui button lotr">
                <i class="file alternate icon"></i>
                Dodatki
              </label>
            </div>

            <div>
              <button
                type="submit"
                class="ui button lotr"
                :class="{ disabled: blockButton }"
                style="width: 100%"
                @click="sendFile(this, false)"
              >
                <i class="cloud upload alternate icon"></i>
                Załaduj plik
              </button>
            </div>
            <div class="ui checkbox">
              <input type="checkbox" name="example" @change="handleBonus" />
              <label style="color: var(--lotr-gold)">Chcę wysłać dodatki</label>
            </div>
          </div>
        </div>
        <!-- <div v-else class="ui message lotr">
          <div class="header">Witaj w systemie "Pierścień"</div>
          <div v-if="usersStore.liczbaZatwierdzen == 0">
            <p>W obecnej chwili nie ma żadnych list płac do zatwierdzenia.</p>
          </div>
          <div v-else>
            {{ usersStore.liczbaZatwierdzen }} list płac do zatwierdzenia.
          </div>
          <div style="margin-top: 10px;">
            <button class="ui button lotr" @click="pobierzListy('preapproved')">
              Zobacz listy płac do zatwierdzenia
            </button>
            <button class="ui button lotr" @click="pobierzDaneDoZatwierdzenia">
              Zobacz zatwierdzone listy płac
            </button>
          </div>
        </div> -->
      </div>
      <div id="loader" v-else>
        <div
          class="ui indicating progress"
          :data-percent="loadingVal"
          id="file-loader"
        >
          <div class="bar">
            <div class="progress" style="color: var(--lotr-gold)"></div>
          </div>
          <div class="label" style="color: var(--lotr-gold)">Ładuję plik</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "redaxios";
import config from "../config.js";
import PierscienIcon from "./icons/PierscienIcon.vue";
import ScaryBilbo from "./icons/ScaryBilbo.vue";
import FileUploadModal from "./modals/FileUploadModal.vue";
import { useRatesStore } from "@/stores/ratesStore";
import { useUsersStore } from "@/stores/usersStore";

export default {
  setup() {
    const store = useRatesStore();
    const usersStore = useUsersStore();
    return {
      store,
      usersStore,
    };
  },
  components: {
    PierscienIcon,
    ScaryBilbo,
    FileUploadModal,
  },
  emits: ["showResults"],
  data() {
    return {
      file: null,
      bonusFile: null,
      addBonus: false,
      loadingVal: 0,
      uploadingFile: false,
      errors: {
        errorModalMsg: "",
        errorCode: 0,
        status: false,
        errMsg: "",
      },
    };
  },
  updated() {
    $("#file-loader").progress({
      percent: this.loadingVal,
    });
  },
  computed: {
    blockButton() {
      if (this.file && !this.addBonus) {
        return false;
      }
      if (this.bonusFile && this.addBonus) {
        return false;
      }
      return true;
    },
    userStatus() {
      return this.usersStore.loggedUserAccess;
    },
    isUploading() {
      return this.uploadingFile;
    },
  },
  methods: {
    handleBonus() {
      this.addBonus = !this.addBonus;
      if (this.addBonus == false) {
        this.bonusFile = null;
      }
    },
    handleFile(name, event) {
      if (name == "bonus") {
        this.bonusFile = event.target.files[0];
      } else {
        this.file = event.target.files[0];
      }
    },
    cancelAdding(name) {
      const inputVal = document.getElementById("pierscienFileInput");
      const bonusVal = document.getElementById("pierscienBonusInput");
      if (inputVal) {
        this.file = null;
        inputVal.value = "";
      }      
      if (bonusVal) {
        this.bonusFile = null;
        bonusVal.value = "";
      }
      // if (name == "bonus") {
      //   this.bonusFile = "";
      //   bonusVal.value = "";
      // } else {
      //   this.file = "";
      //   inputVal.value = "";
      // }
    },
    async sendFile(val, bool) {
      this.usersStore.getUserData()
      this.uploadingFile = true;
      this.loadingVal = 10;
      this.errors.status = false;
      this.errors.errMsg = "";
      let formData = new FormData();
      formData.append("mainFile", this.file);
      formData.append("bonusFile", this.bonusFile);
      formData.append("correction", bool);
      formData.append("login", this.usersStore.loggedUser)
      let loaderGoal = 15;
      const loaderInterval = setInterval(function () {
        let addPercentage = Math.floor(Math.random() * 5);
        if (loaderGoal <= 95) {
          $("#file-loader").progress({
            percent: loaderGoal,
          });
        }
        loaderGoal += addPercentage;
      }, 750);
      axios
        .post(`${config.baseUrl}/api/return_rates_info`, formData, {
          headers: {
            Accept: "application/json",
            ContentType: "multipart/form-data",
          },
        })
        .then((res) => {
          if (res.status == 202) {
            this.errors.errorCode = res.status;
            this.errors.errorModalMsg = res.data;
            clearInterval(loaderInterval);
            this.loadingVal = 100;
            $("#fileUpload")
              .modal({
                closable: false,
                onApprove() {
                  val.sendFile(val, true);
                },
                onDeny() {
                  val.uploadingFile = false;
                  val.file = "";
                  val.cancelAdding();
                },
              })
              .modal("show");
          }
          const usersInMocarz = JSON.parse(res.data.money_data);
          const ratesNotInMocarz = JSON.parse(res.data.missing_rates);
          // const ratesNotInMocarz = [];
          const usersNotInFile = JSON.parse(res.data.missing_in_file);
          $("#file-loader").progress({
            percent: 100,
          });
          this.store.$state = {
            enteredFrom: 'upload',
            presentUsers: usersInMocarz,
            missingRates: ratesNotInMocarz,
            missingRatesId: res.data.missing_rates_id,
            missingUsers: usersNotInFile,
            showUpload: false,
            showResults: true,
          };
          this.uploadingFile = false;
          formData = new FormData();
          this.file = "";
          const inputVal = document.getElementById("pierscienFileInput");
          inputVal.value = "";
        })
        .catch((err) => {
          if (err.status == 403) {
            this.errors.status = true;
            this.errors.errMsg = err.data.message;
          }
          if (err.status == 406 || err.status == 422) {
            this.errors.errorCode = err.status;
            this.errors.errorModalMsg = err.status == 406 ? err.data : err.data.message;
            clearInterval(loaderInterval);
            this.loadingVal = 100;
            $("#fileUpload")
              .modal({
                closable: false,
                onDeny() {
                  val.uploadingFile = false;
                  val.addBonus = false;
                  val.bonusFile = "";
                  val.file = "";
                },
              })
              .modal("show");
          }
        });
    },
    pobierzListy(val) {
      this.store.getLists(val);
      this.store.$state = {
        showUpload: false,
        showLists: true,
      };
    },
    // pobierzDaneDoZatwierdzenia() {
    //   this.uploadingFile = true;
    //   let codeToCheck;
    //   let timePeriodToCheck;
    //   const storeData = this.usersStore.daneZatwierdzen;
    //   if (this.usersStore.liczbaZatwierdzen == 1) {
    //     codeToCheck = storeData[0].project_code;
    //     timePeriodToCheck = storeData[0].okres_rozliczenia;
    //   }
    //   axios
    //     .post(
    //       `${config.baseUrl}/dane_do_zatwierdzenia`,
    //       {
    //         code: codeToCheck,
    //         timePeriod: timePeriodToCheck,
    //       },
    //       {
    //         headers: {
    //           Accept: "application/json",
    //           ContentType: "multipart/form-data",
    //         },
    //       }
    //     )
    //     .then((res) => {
    //       const parsedData = JSON.parse(res.data.dane);
    //       this.store.$state = {
    //         presentUsers: parsedData,
    //         idZatwierdzenia: res.data.id,
    //         wysylacz: res.data.wysylacz,
    //         dataWyslania: res.data.data_wyslania,
    //         showLists: true,
    //         showUpload: false,
    //       };
    //       this.uploadingFile = false;
    //     })
    //     .catch((err) => {
    //       if (err.status == 403) {
    //         this.errors.status = true;
    //         this.errors.errMsg = err.data.message;
    //       }
    //     });
    // },
  },
};
</script>

<style scoped>



h1 {
  color: var(--color-text) !important;
}

.error-bg {
  background: #ca1010 !important;
}
.error-bg h1 {
  color: whitesmoke !important;
}

.ui.message.lotr {
  background-color: var(--lotr-darkerGreen);
  border: 2px solid var(--lotr-gold);
  color: var(--lotr-gold);
}


</style>
