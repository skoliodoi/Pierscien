<template>
  <SuccessModal />
  <div class="rejecting-box" v-if="store.spin">
    <PierscienIcon style="height: 50%; width: auto" class="spinning" />
    <h1>Trwa {{store.spinMessage}}...</h1>
  </div>
  <div v-else>
    <Navbar @hideTable="returnToMain" />
    <div class="detail-container">
      <div
        class="ui segment lotr-segment"
        v-for="each in store.presentUsers.details"
        style="color: black"
      >
        <div class="ui equal width grid">
          <div class="column">
            <strong>Imię i nazwisko:</strong>
            <div>{{ each.imie_i_nazwisko }}</div>
          </div>
          <div class="column">
            <strong>Mocarz ID:</strong>
            <div>{{ each.mocarz_id }}</div>
          </div>
          <div class="center aligned column">
            <strong>PESEL:</strong>
            <div>{{ each.pesel ? each.pesel : "Brak" }}</div>
          </div>
          <div class="three wide center aligned column">
            <strong>Suma godzin w miesiącu:</strong>
            <div>{{ each.suma_godzin_w_miesiacu }}</div>
          </div>
          <div class="center aligned column">
            <strong>Wypłata:</strong>
            <div>{{ Number(each.total_salary).toLocaleString("pl") }}zł</div>
          </div>
          <div class="center aligned column">
            <strong>Koszt pracodawcy:</strong>
            <div>{{ Number(each.suma_kosztow).toLocaleString("pl") }}zł</div>
          </div>
          <div class="center aligned column">
            <strong>Bonusy:</strong>
            <div>{{ Number(each.suma_bonusow).toLocaleString("pl") }}zł</div>
          </div>
          <div class="center aligned column">
            <strong>Łącznie:</strong>
            <div>
              {{
                Number(each.complete_salary).toLocaleString("pl")
              }}zł
            </div>
          </div>
        </div>
        <div style="text-align: center; margin-bottom: 5px;">
          <div class="ui accordion">
            <button class="title ui button lotr" style="width: 100%">Detale</button>
            <div class="content" style="overflow-x: auto">
              <RatesTableRow :rowData="each" />
            </div>
          </div>
        </div>
        <div style="text-align: center" v-if="each.suma_bonusow > 0">
          <div class="ui accordion">
            <button class="title ui button lotr" style="width: 100%">
              Pokaż informacje o bonusach
            </button>
            <div class="content" style="overflow-x: auto">
              <BonusTableRow :rowData="each.bonusy" />
              <!-- <div v-for="bonus in each.bonusy">
              <div >
                <div>Kwota:</div>
                {{ bonus.kwota }}zł
                <div>Kategoria:</div>
                {{ bonus.kategoria }}
                <div>Komentarz:</div>
                {{ bonus.komentarz ? bonus.komentarz : "Brak" }}
              </div>
            </div> -->
            </div>
          </div>
        </div>
      </div>
    </div>
    <Footer
      :code="store.presentUsers.code"
      :time_period="store.presentUsers.time_period"
      @hideTable="returnToMain"
      @commitAction="getEmitVal"
    />
  </div>
</template>

<script>
import { TEST_DATA } from "../../assets/test_data";
import PierscienIcon from "../icons/PierscienIcon.vue";
import RatesTableRow from "./RatesTableRow.vue";
import BonusTableRow from "./BonusTableRow.vue";
import SuccessModal from "../modals/SuccessModal.vue";
import Navbar from "../Navbar.vue";
import Footer from "./Footer.vue";
import { useRatesStore } from "@/stores/ratesStore";
import _default from "redaxios";

export default {
  setup() {
    const store = useRatesStore();
    return {
      store,
    };
  },
  components: {
    SuccessModal,
    PierscienIcon,
    RatesTableRow,
    BonusTableRow,
    Navbar,
    Footer,
  },
  props: ["ratesData"],
  emits: ["returnToMain"],
  data() {
    return {
      testData: TEST_DATA,
    };
  },
  mounted() {
    $(".ui.accordion").accordion();
  },
  methods: {
    returnToMain() {
      this.$emit("returnToMain");
    },
    getEmitVal(val) {
      this.commitFooterAction(val, this)
    },
    async commitFooterAction(action, val) {
      await this.store.uploadData(action);
      console.log('shoMwodal')
      $("#successModal")
        .modal({
          class: "mini inverted",
          onApprove() {
            val.store.$state = {
              showResults: false,
              showUpload: true,
              spin: false,
              spinMessage: "",
              view: "main",
            };
          },
        })
        .modal("show");
    },
  },
  computed: {
    tableHeaderDates() {
      return this.store.presentUsers.details[0].dane;
    },
    currencyFormat(val) {
      return Number(val).toLocaleString("pl");
    },
  },
};
</script>

<style scoped>
.detail-container {
  height: calc(100vh - 173px);
  overflow-x: auto;
}

.lotr-segment {
  background-color: var(--lotr-lightGold) !important;
  color: var(--lotr-green) !important;
  font-weight: bold;
}

.ui.button.lotr:hover {
  border: 1px solid var(--lotr-darkerGreen) !important;
}

th {
  text-align: center !important;
  position: sticky;
  top: 0;
}
#table-wrapper {
  width: 100%;
  height: calc(100vh - 173px);
  overflow-x: scroll;
  overflow-y: auto;
}
table thead th:first-child {
  position: sticky;
  left: 0;
  z-index: 2;
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
</style>
