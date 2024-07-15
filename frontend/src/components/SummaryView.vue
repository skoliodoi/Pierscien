<template>
  <MissingRatesModal id="missing-rates" :missingRates="store.missingRates" />
  <MissingUsersModal id="missing-users" :missingUsers="store.missingUsers" />
  <RejectionModal @rejection-reason="rejectData" />
  <SuccessModal />
  <ConfirmationModal />
  <div class="rejecting-box" v-if="rejecting">
    <PierscienIcon style="height: 50%; width: auto;" class="spinning"/>
    <h1>Trwa odrzucanie...</h1>
  </div>
  <div class="ui container summary-box" v-else>
    <div v-if="showLoader" class="loading-box">
      <PierscienIcon style="height: 75%; width: auto;" class="spinning"/>
      <div>
        <div
          class="ui indicating progress"
          :data-percent="loadingVal"
          id="zatwierdzenie-loader"
        >
          <div class="bar">
            <div class="progress" style="color: var(--lotr-gold)"></div>
          </div>
          <div class="label" style="color: var(--lotr-gold)">
            Poczekaj, ładuję dane...
          </div>
        </div>
      </div>
    </div>
    <div class="ui fluid card" id="summary-card" v-else>
      <div class="content" id="header-content">
        <div>
          <div class="ui button lotr" v-if="store.enteredFrom == 'summary'" @click="store.$state = {
                showResults: false,
                showUpload: true,
                view: 'lists',
              }
            ">
            Wróć
          </div>
        </div>
        <div class="center aligned header" style="color: var(--lotr-gold)">
          Import pliku "{{ summaryData.file_name }}" zakończony.
        </div>
      </div>
      <div class="content" style="padding: 0; border: none; background-color: whitesmoke">
        <!-- <div>Nazwa projektu: {{ summaryData.project_name }}</div>
        <div>Klient: {{ summaryData.client }}</div>
        <div>Kod projektu: {{ summaryData.code }}</div>
        <div>Okres: {{ summaryData.time_period }}</div>
        <div>
          Łączna liczba pracowników na projekcie: {{ summaryData.total_kts }}
        </div>
        <div>Łączna wypłata: {{ summaryData.total_project_salary }}zł</div>
        <div>Suma godzin: {{ summaryData.monthly_hours }}</div>
        <div>Średnia liczba rbh na pracownika: {{ summaryData.avg_rbh }}</div>
        <div>Średnia wypłata: {{ summaryData.avg_salary }}zł</div>
        <div>Łączne bonusy: {{ summaryData.total_bonus }}zł</div>
        <div>CAŁOŚĆ: {{ summaryData.total_with_bonus }}zł</div> -->
        <table
          class="ui selectable table" style="border: none;"
        >
          <tbody>
            <tr class="lotr-row">
              <td>Klient</td>
              <td class="centered">
                <strong>{{ summaryData.client }}</strong>
              </td>
            </tr>
            <tr class="lotr-row">
              <td>Kod projektu</td>
              <td class="centered">
                <strong>{{ summaryData.code }}</strong>
              </td>
            </tr>
            <tr class="lotr-row">
              <td>Lokalizacja</td>
              <td class="centered">
                <strong>{{ summaryData.lokalizacja }}</strong>
              </td>
            </tr>
            <tr class="lotr-row">
              <td>Data</td>
              <td class="centered">
                <strong>{{ summaryData.time_period }}</strong>
              </td>
            </tr>
            <tr class="lotr-row">
              <td>Łączna liczba konsultantów na projekcie</td>
              <td class="centered">
                <strong>{{ summaryData.total_kts }}</strong>
              </td>
            </tr>
            <tr class="lotr-row">
              <td>Suma godzin</td>
              <td class="centered">
                <strong>{{ summaryData.monthly_hours }}</strong>
              </td>
            </tr>
            <tr class="lotr-row">
              <td>Średnia liczba rbh na konsultanta</td>
              <td class="centered">
                <strong>{{ summaryData.avg_rbh }}</strong>
              </td>
            </tr>
            <tr class="lotr-row">
              <td>Średnia wypłata</td>
              <td class="centered">
                <strong>{{ Number(summaryData.avg_salary).toLocaleString("pl") }}zł</strong>
              </td>
            </tr>
            <tr class="lotr-row">
              <td>Łączna wypłata</td>
              <td class="centered">
                <strong>{{ Number(summaryData.total_project_salary).toLocaleString("pl") }}zł</strong>
              </td>
            </tr>
            <tr class="lotr-row">
              <td>Łączne koszty pracodawcy</td>
              <td class="centered">
                <strong>{{ Number(summaryData.total_cost).toLocaleString("pl") }}zł</strong>
              </td>
            </tr>
            <tr class="lotr-row">
              <td>Łączne bonusy</td>
              <td class="centered">
                <strong>{{ Number(summaryData.total_bonus).toLocaleString("pl") }}zł</strong>
              </td>
            </tr>
            <tr class="lotr-row">
              <td class="centered">RAZEM</td>
              <td class="centered">
                <strong>{{ Number(summaryData.complete_total).toLocaleString("pl") }}zł</strong>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="additional-content" id="button-row" style="">
        <div class="ui bottom attached four buttons">
          <div class="ui button lotr" @click="showConfirmation(this)">
            {{ accessLevel }}
          </div>
          <div
            class="ui button lotr"
            v-if="store.enteredFrom == 'summary'"
            @click="showRejection"
          >
            Odrzuć
          </div>
          <div class="ui button lotr" @click="$emit('showDetails')">
            Zobacz szczegóły
          </div>
          <div
            class="ui button lotr"
            @click="
              store.$state = {
                showResults: false,
                showUpload: true,
                view: 'main',
              }
            "
          >
            Anuluj
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { useRatesStore } from "@/stores/ratesStore";
import { useUsersStore } from "@/stores/usersStore";
import PierscienIcon from "./icons/PierscienIcon.vue";
import MissingUsersModal from "./modals/MissingUsersModal.vue";
import MissingRatesModal from "./modals/MissingRatesModal.vue";
import RejectionModal from "./modals/RejectionModal.vue";
import SuccessModal from "./modals/SuccessModal.vue";
import ConfirmationModal from "./modals/ConfirmationModal.vue";
export default {
  emits: ["showDetails"],
  components: {
    PierscienIcon,
    MissingUsersModal,
    MissingRatesModal,
    SuccessModal,
    ConfirmationModal,
    RejectionModal,
  },
  setup() {
    const store = useRatesStore();
    const usersStore = useUsersStore();
    return {
      store,
      usersStore,
    };
  },
  data() {
    return {
      showLoader: false,
      rejecting: false,
      loadingVal: 0,
      anulujObj: {
        showResults: false,
        showUpload: true,
        view: "main",
      },
    };
  },
  mounted() {
    this.checkForMissingData(this);
  },
  updated() {
    $("#zatwierdzenie-loader").progress({
      percent: this.loadingVal,
    });
  },
  computed: {
    summaryData() {
      return this.store.presentUsers;
    },
    accessLevel() {
      return this.usersStore.loggedUserAccess == "zatwierdzacz" || this.store.enteredFrom == 'summary'
        ? "Zatwierdź"
        : "Wyślij do akceptacji";
    },
  },
  methods: {
    showConfirmation(val) {
      $("#confirmationModal")
        .modal({
          closeable: false,
          class: "mini inverted",
          onApprove() {
            val.sendData(val);
          },
        })
        .modal("show");
    },
    showRejection() {
      $("#rejectionModal")
        .modal({
          closable: false,
        })
        .modal("show");
    },
    async rejectData(reason) {
      this.rejecting = true;
      await this.store.rejectRates(
        reason,
        this.summaryData.code,
        this.summaryData.time_period
      );
      this.showLoader = false;
    },
    async sendData(val) {
      this.showLoader = true;
      let loaderGoal = 15;
      const loaderInterval = setInterval(function () {
        let addPercentage = Math.floor(Math.random() * 8);
        if (loaderGoal <= 95) {
          $("#zatwierdzenie-loader").progress({
            percent: loaderGoal,
          });
        }
        loaderGoal += addPercentage;
      }, 750);
      await this.store.uploadData(this.accessLevel);
      clearInterval(loaderInterval);
      this.loadingVal = 100;
      $("#successModal")
        .modal({
          class: "mini inverted",
          onApprove() {
            val.showLoader = false;
            val.store.$state = val.anulujObj;
          },
        })
        .modal("show");
    },
    cleanUpMissingData() {
      this.store.missingRates = [];
      this.store.missingUsers = [];
    },
    checkForMissingData(val) {
      const missingRates = this.store.missingRates;
      if (missingRates.length > 0) {
        $("#missing-rates")
          .modal({
            class: "inverted colorful",
            closable: false,
            onApprove() {
              val.cleanUpMissingData();
              val.checkForMissingUsers(val);
            },
            onDeny() {
              val.cleanUpMissingData();
              val.store.$state = val.anulujObj;
            },
          })
          .modal("show");
      } else {
        val.checkForMissingUsers(val);
      }
    },
    checkForMissingUsers(val) {
      const missingUsers = this.store.missingUsers;
      // const missingUsers = [];
      if (missingUsers.length > 0) {
        $("#missing-users")
          .modal({
            class: "inverted colorful",
            closable: false,
            onApprove() {
              val.cleanUpMissingData()
            },
            onDeny() { 
              val.cleanUpMissingData();
              val.store.$state = val.anulujObj;
            },
          })
          .modal("show");
      }
    },
  },
};
</script>
<style scoped>
.summary-box {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
#summary-card {
  background-color: transparent;
  width: 75%;
  /* background-color: var(--lotr-lightGold); */
  box-shadow: none;
}
#header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--lotr-green);
}
#header-content > div {
  color: var(--lotr-lightGold) !important;
}
#button-row {
  border: 1px solid transparent;
  border-bottom: 1px solid var(--lotr-green);
  background-color: var(--lotr-darkerGreen);
}

.rejecting-box {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}

.rejecting-box > h1 {
  color: var(--lotr-lightGold)
}

.loading-box {
  height: 50% !important;
  width: 50%;
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  align-items: stretch;
}

.ui.table > tbody > tr > td,
.ui.table > tr > td {
  padding: 5px 5px;
}

.lotr-row {
  background-color: var(--lotr-lightGold) !important;
  color: var(--lotr-green);
  font-weight: bold;
}

.centered {
  text-align: center !important;
}

.ui.button.lotr:hover {
  border: 1px solid var(--lotr-darkerGreen) !important;
}
</style>
