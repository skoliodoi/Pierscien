<template>
  <button
    class="ui button lotr-inverted"
    style="margin: 10px 0 0 10px"
    @click="store.$state = { view: 'main' }"
  >
    Wróć
  </button>
  <FileUploadModal :code="errors.errorCode" :message="errors.errorModalMsg" />
  <SuccessModal />
  <div class="main-page-container" :class="{ 'error-bg': errors.status }">
    <div class="ui container file-upload-container">
      <h1 class="ui huge header" v-if="errors.status">{{ errors.errMsg }}</h1>
      <div class="upload-box">
        <PierscienIcon :class="{ spinning: isUploading }" />
      </div>
      <div id="input" v-if="!isUploading">
        <div class="input-container">
          <div class="input-container-corset">
            <div></div>
            <div class="ui file action input">
              <label for="benefityInput" class="ui button lotr">
                <i class="file alternate icon"></i>
                Benefity
              </label>
              <button
                for="benefityInput"
                class="ui button lotr"
                @click="cancelAdding()"
                v-if="file"
              >
                <i class="times alternate icon"></i>
                Usuń
              </button>
              <input
                id="benefityInput"
                type="file"
                @change="handleFile($event)"
              />
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
          </div>
        </div>
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
import PierscienIcon from "./icons/PierscienIcon.vue";
import FileUploadModal from "./modals/FileUploadModal.vue";
import SuccessModal from "./modals/SuccessModal.vue";
import axios from "redaxios";
import config from "../config.js";
import { useRatesStore } from "@/stores/ratesStore";
import { useUsersStore } from "@/stores/usersStore";
export default {
  setup() {
    const store = useRatesStore();
    const users = useUsersStore();
    return {
      store,
      users,
    };
  },
  components: {
    PierscienIcon,
    FileUploadModal,
    SuccessModal,
  },
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
    handleFile(event) {
      this.file = event.target.files[0];
    },
    cancelAdding() {
      const inputVal = document.getElementById("benefityInput");
      this.file = "";
      inputVal.value = "";
    },

    async sendFile(val, bool) {
      this.uploadingFile = true;
      this.loadingVal = 10;
      this.errors.status = false;
      this.errors.errMsg = "";
      let formData = new FormData();
      formData.append("file", this.file);
      formData.append("correction", bool);
      formData.append("login", this.users.loggedUser);
      let loaderGoal = 15;
      const loaderInterval = setInterval(function () {
        let addPercentage = Math.floor(Math.random() * 3);
        if (loaderGoal <= 95) {
          $("#file-loader").progress({
            percent: loaderGoal,
          });
        }
        loaderGoal += addPercentage;
      }, 2000);
      axios
        .post(`${config.baseUrl}/api/upload_benefits`, formData, {
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
            this.uploadingFile = false;
            $("#fileUpload")
              .modal({
                closable: false,
                onApprove() {
                  val.sendFile(val, true);
                },
                onDeny() {
                  val.uploadingFile = false;
                  val.file = null;
                  const inputVal = document.getElementById("benefityInput");
                  inputVal.value = "";
                },
              })
              .modal("show");
          } else {
            this.store.$state = {
              messages: {
                responseMsg: res.data,
              },
            };
            clearInterval(loaderInterval);
            this.loadingVal = 100;
            this.uploadingFile = false;
            $("#successModal")
              .modal({
                closable: false,
                class: "mini inverted",
                onApprove() {
                  val.store.$state.messages.responseMsg = "";
                },
              })
              .modal("show");
            formData = new FormData();
            this.file = null;
            const inputVal = document.getElementById("benefityInput");
            inputVal.value = "";
          }
        })
        .catch((err) => {
          if (err.status == 406 || err.status == 422) {
            this.errors.errorCode = err.status;
            this.errors.errorModalMsg =
              err.status == 406 ? err.data : err.data.message;
            clearInterval(loaderInterval);
            this.loadingVal = 100;
            $("#fileUpload")
              .modal({
                closable: false,
                onDeny() {
                  val.uploadingFile = false;
                  val.file = "";
                  const inputVal = document.getElementById("benefityInput");
                  if (inputVal) {
                    inputVal.value = "";
                  }
                },
              })
              .modal("show");
          }
        });
    },
  },
};
</script>
<style scoped></style>
