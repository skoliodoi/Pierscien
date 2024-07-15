<script setup>
import { onMounted } from "vue";
import { onUpdated } from "vue";
import { computed } from "vue";
import { ref } from "vue";
import axios from "redaxios";
import config from "../../config";
import { useRatesStore } from "../../stores/ratesStore";
import PierscienIcon from "../icons/PierscienIcon.vue";
import FinalSummaryTable from "./FinalSummaryTable.vue";
import FinalSummaryTableDetails from "./FinalSummaryTableDetails.vue";
import ErrorModal from "../modals/ErrorModal.vue";
import * as XLSX from "xlsx";
const props = defineProps(["modelValue"]);
const emit = defineEmits(["update:modelValue"]);
let showDetails = ref(false);
let selectedDate = "";

const zatwierdzoneDetails = ref([]);
const errorMsg = ref("");
const store = useRatesStore();
onMounted(() => {
  $("#daty").dropdown();

  // Get today's date
  const today = new Date();

  // Subtract one month
  today.setMonth(today.getMonth() - 1);

  // Get the year and month in YYYY-MM format
  const previousMonth = today.toISOString().slice(0, 7);
  store.datesToSelect = [previousMonth];
  selectedDate = previousMonth;
  getProjectSummary(previousMonth);
});
onUpdated(() => {
  $("#daty").dropdown();
});
const getProjectSummary = (date) => {
  store.getProjects(date);
  store.getDates();
};
const showDetailsHandler = (val) => {
  showDetails.value = true;
  zatwierdzoneDetails.value = val;
};

const getSummaryWithCo = (val) => {
  getSummary(val);
};

const getSummary = (co) => {
  store.showSummary = false;
  store.spin = true;
  store.getDates();
  axios
    .get(`${config.baseUrl}/api/get_summary/${selectedDate}/${co}`, {
      headers: {
        Accept: "application/json",
      },
    })
    .then((response) => {
      let fileName;
      if (co == "all") {
        fileName = `optima_VCC_podsumowanie_plac_za_${selectedDate}_all.xlsx`;
      } else {
        fileName = `optima_VCC_podsumowanie_plac_za_${selectedDate}_${co}.xlsx`;
      }
      // var fileURL = window.URL.createObjectURL(new Blob([response.data]));
      // // create "a" HTML element with href to file & click
      // var fileLink = document.createElement("a");
      // fileLink.href = fileURL;
      // fileLink.setAttribute("download", fileName);
      // document.body.appendChild(fileLink);
      // fileLink.click();
      const excelData = JSON.parse(response.data);
      const worksheet = XLSX.utils.json_to_sheet(excelData);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, worksheet, "Podsumowanie");
      XLSX.writeFile(wb, fileName);
      store.showSummary = true;
      store.spin = false;
    })
    .catch((err) => {
      errorMsg.value = err.data.message;
      $("#summary-error-modal")
        .modal({
          onDeny(){
            store.showSummary = true;
            store.spin = false;
          }
        })
        .modal("show");
    });
};
</script>

<template>
  <div class="ui horizontal equal width segments main-header">
    <div class="ui segment left">
      <button
        class="ui button lotr-inverted"
        @click="
          store.$state = {
            view: 'main',
            projectSummary: [],
            totalSalary: null,
            showSummary: false,
          }
        "
      >
        Wróć
      </button>
      <div class="segment-date-selection">
        <label for="daty" style="color: var(--lotr-gold)">Wybierz datę</label>
        <select
          class="ui selection dropdown"
          id="daty"
          v-model="selectedDate"
          @change="getProjectSummary(selectedDate)"
        >
          <option value="" id="first"></option>
          <option v-for="date in store.datesToSelect" :value="date">
            {{ date }}
          </option>
        </select>
      </div>
    </div>
    <div class="ui segment icon">
      <PierscienIcon :class="{ spinning: store.spin }" />
    </div>
    <div class="ui segment right">
      <button
        @click="getSummary('all')"
        style="width: 100%"
        v-if="store.projectSummary.length > 0"
        class="ui button lotr"
      >
        Wyeksportuj dane ze wszystkich lokalizacji
      </button>
    </div>
  </div>

  <div id="main-container">
    <ErrorModal id="summary-error-modal" :message="errorMsg" />
    <div id="icon-container" v-if="!store.showSummary">
      <h1
        class="ui massive header"
        v-if="store.spin"
        style="text-align: center; color: var(--lotr-lightGold)"
      >
        ᕕ(⌐■_■)ᕗ ♪♬
      </h1>
      <h2
        v-if="store.spin"
        style="text-align: center; color: var(--lotr-lightGold)"
      >
        Pobieram dane...
      </h2>
    </div>
    <div class="table-holder" v-else>
      <div v-if="store.projectSummary.length > 0">
  
      <FinalSummaryTable
        :projects="store.projectSummary"
        @details="showDetailsHandler"
        @co="getSummaryWithCo"
        v-if="!showDetails"
      />
      <FinalSummaryTableDetails
        v-else
        :details="zatwierdzoneDetails"
        @back-to-summary="showDetails = false"
      />
      </div>
      <div v-else id="missing-data">
        <h1 class="ui massive header">¯\_(⊙_ʖ⊙)_/¯ </h1>
        <span class="ui large text" id="missing-msg">Nie znaleziono żadnych zatwierdzonych danych za {{ selectedDate }}. Może sprawdź inną datę?</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      selectedPeriod: "",
      datesToSelect: [],
    };
  },
};
</script>

<style scoped>
.main-header {
  margin: 0 !important;
  border-radius: 0 !important;
  height: 7rem;
  border: none !important;
  background-color: var(--lotr-green) !important;
}

.ui.segment {
  background-color: var(--lotr-darkGreen);
  color: var(--lotr-lightGold);
  font-weight: bold;
}

#main-container {
  height: calc(100vh - 98px) !important;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow-x: auto;
}

.table-holder {
  width: 90%;
}

.selection-container {
  justify-content: center;
}

.lokalizacje-container {
  justify-content: space-evenly;
}

.lokalizacje-container,
.selection-container {
  flex: 2 !important;
  display: flex;
  flex-direction: column;
  align-items: center;
}

#right-container {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 2;
}

#icon-container {
  height: 80%;
  width: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.op-segment,
#summary-segment {
  color: var(--lotr-lightGold) !important;
  width: 100%;
  background-color: transparent;
  border: 1px solid var(--lotr-lightGold);
  display: flex;
  justify-content: space-around;
}

.op-segment > span:first-child {
  flex: 1;
}

.op-segment > span:last-child {
  flex: 1.5;
}

.middle-span {
  flex: 1;
}

.ui.default.dropdown:not(.button) > .text,
.ui.dropdown:not(.button) > .default.text {
  background-color: red !important;
}
.four.wide.middle.aligned.column {
  border-right: 1px solid var(--lotr-lightGold) !important;
}
.ui.fluid.card {
  box-shadow: none;
}
.four.wide.middle.aligned.column:last-of-type {
  border-right: none !important;
}

.ui.segment.left {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.segment-date-selection {
  display: flex;
  width: 75%;
  justify-content: space-evenly;
  align-items: center;
}

.ui.segment.middle {
  display: flex;
  justify-content: center;
}

.ui.segment.middle > div {
  display: flex;
  align-items: center;
  justify-content: space-around;
  width: 75%;
}

.ui.segment.right {
  display: flex;
  align-items: center;
  justify-content: flex-end !important;
}

.ui.segment.right > button {
  width: 50% !important;
}

.main-header {
  margin: 0 !important;
  border-radius: 0 !important;
  height: 7rem;
  border: none !important;
  background-color: var(--lotr-green) !important;
}

#missing-data {
  text-align: center;
  color: var(--lotr-lightGold) !important;
}

#missing-data > h1 {
  color: var(--lotr-lightGold);
}

#missing-data > span {
  font-weight: bold;
}
</style>
