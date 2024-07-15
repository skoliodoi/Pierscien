<template>
  <ConfirmationModal
    :message="'Zatwierdzona lista płac zostanie usunięta i trzeba będzie ją na nowo zatwierdzić!'"
  />
  <div class="ui container list-container">
    <div
      class="ui fluid card"
      style="box-shadow: none; background-color: transparent"
    >
      <div class="content" id="header-row">
        <div class="ui grid">
          <div class="two wide middle aligned column">
            <button
              class="ui button lotr"
              @click="
                store.$state = {
                  showLists: false,
                  showUpload: true,
                  view: 'main',
                }
              "
            >
              Wróć
            </button>
          </div>
          <div
            class="six wide middle aligned column"
            style="text-align: center"
          >
            <h1 class="ui header">Listy płac</h1>
          </div>
          <div
            class="four wide column"
            style="display: flex; align-items: center"
          >
            <select
              class="ui selection dropdown"
              id="date-picker"
              v-model="selectedDate"
            >
              <option value="*">Wszystkie</option>
              <option v-for="date in store.datesInListOfListsToSelect" :value="date">{{date}}</option>
            </select>
          </div>
          <div class="four wide middle aligned column" style="display: flex; flex-direction: row; align-items: center;">
            <div class="ui search">
              <div class="ui icon input" >
                <input
                  class="prompt"
                  :class="{shrink: searchFilter}"
                  v-model="searchFilter"
                  type="text"
                  placeholder="Znajdź listę płac"
                />
                <i class="search icon"></i>
                <!-- <i
                  class="times icon"
                  style="cursor: pointer"
                  @click="clearSearchFilter"
                ></i> -->
              </div>
            </div>
            <div v-if="searchFilter">
              <button @click="clearSearchFilter" class="ui tiny circular icon button" ><i class="ui times icon"></i></button>
            </div>
          </div>
        </div>
      </div>
      <div class="content row-content">
        <div v-for="list in listDisplay" v-if="listDisplay.length > 0">
          <div class="ui equal width stackable grid">
            <div
              class="ui row"
              style="
                border-bottom: 1px solid var(--lotr-gold);
                margin-bottom: 14px;
              "
            >
              <div class="column">
                <div>Nazwa projektu:</div>
                {{ list.project_name }}
              </div>
              <div class="column">
                <div>Kod:</div>
                {{ list.project_code }}
              </div>
              <div class="column">
                <div>Data:</div>
                {{ list.okres_rozliczenia }}
              </div>
              <!-- <div class="middle aligned column">
                <button
                  v-if="selected == 'doZatwierdzenia'"
                  class="ui button lotr-inverted"
                  @click="
                    pobierzDaneDoZatwierdzenia(
                      list.project_code,
                      list.okres_rozliczenia
                    )
                  "
                >
                  Zobacz szczegóły
                </button>
              </div> -->
              <div class="middle aligned column">
                <button
                  v-if="selected == 'doZatwierdzenia'"
                  class="ui button lotr-inverted"
                  @click="
                    pobierzDaneDoZatwierdzenia(
                      list.project_code,
                      list.okres_rozliczenia
                    )
                  "
                >
                  Zobacz szczegóły
                </button>
                <button
                  v-else
                  class="ui button lotr-inverted"
                  @click="
                    showModal('anulujZatwierdzenie', this, {
                      code: list.project_code,
                      date: list.okres_rozliczenia,
                      login: usersStore.loggedUser,
                    })
                  "
                >
                  Anuluj zatwierdzenie
                </button>
              </div>
            </div>
          </div>
        </div>
        <div v-else id="no-list">
          <div style="text-align: center">
            <h1>°\_(-_-)_/°</h1>
            <h2>Nie znaleźliśmy wymaganych list płac.</h2>
            <h3>Przepraszamy!</h3>
          </div>
        </div>
      </div>
      <div class="additional-content" v-if="usersStore.higherAccess">
        <div class="ui bottom attached two buttons">
          <button
            class="ui button lotr"
            :class="{ active: selected == 'doZatwierdzenia' }"
            @click="selected = 'doZatwierdzenia'"
          >
            Do zatwierdzenia
          </button>
          <button
            class="ui button lotr"
            :class="{ active: selected == 'zatwierdzone' }"
            @click="selected = 'zatwierdzone'"
          >
            Zatwierdzone
          </button>
          <!-- <button
            class="ui button lotr"
            :class="{ active: selected == 'odrzucone' }"
            @click="selected = 'odrzucone'"
          >
            Odrzucone
          </button> -->
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import axios from "redaxios";
import config from "../config.js";
import { useRatesStore } from "@/stores/ratesStore";
import { useUsersStore } from "@/stores/usersStore";
import ConfirmationModal from "./modals/ConfirmationModal.vue";
import PierscienIcon from "./icons/PierscienIcon.vue";
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
    ConfirmationModal,
    PierscienIcon
  },
  data() {
    return {
      selected: "doZatwierdzenia",
      searchFilter: "",
      selectedDate: "*",
    };
  },
  mounted() {
    $("#date-picker").dropdown();
  },
  computed: {
    listDisplay() {
      let listOfLists = this.store.listaDoZatwierdzenia;
      if (this.selected == "zatwierdzone") {
        listOfLists = this.store.listaZatwierdzona;
      }

      const filterList = (list) => {
        return list.filter(
          (el) =>
            el.project_code
              .toLowerCase()
              .includes(this.searchFilter.toLowerCase()) ||
            el.project_name
              .toLowerCase()
              .includes(this.searchFilter.toLowerCase()) ||
            el.okres_rozliczenia
              .toLowerCase()
              .includes(this.searchFilter.toLowerCase())
        );
      };

      let returnList;
      if (!this.searchFilter && this.selectedDate == "*") {
        returnList = listOfLists;
      } else if (this.selectedDate && this.selectedDate != "*") {
        const filteredByDate = listOfLists.filter(
          (el) => el.okres_rozliczenia == this.selectedDate
        );
        if (!this.searchFilter) {
          returnList = filteredByDate;
        } else {
          returnList = filterList(filteredByDate);
        }
      } else {
        returnList = filterList(listOfLists);
      }
      return returnList;
    },
  },
  methods: {
    clearSearchFilter() {
      this.searchFilter = "";
    },
    async anulujZatwierdzenie(data) {
      await axios.post(`${config.baseUrl}/api/anuluj_zatwierdzenie`, data, {
        headers: {
          Accept: "application/json",
        },
      });
      this.store.getLists();
    },
    showModal(func, val, data) {
      $("#confirmationModal")
        .modal({
          closable: false,
          onApprove() {
            if (func == "anulujZatwierdzenie") {
              val.anulujZatwierdzenie(data);
            }
          },
        })
        .modal("show");
    },
    pobierzDaneDoZatwierdzenia(code, period) {
      const codeToCheck = code;
      const timePeriodToCheck = period;
      // const storeData = this.usersStore.daneZatwierdzen;
      // if (this.usersStore.liczbaZatwierdzen == 1) {
      //   codeToCheck = storeData[0].project_code;
      //   timePeriodToCheck = storeData[0].okres_rozliczenia;
      // }
      axios
        .post(
          `${config.baseUrl}/api/dane_do_zatwierdzenia`,
          {
            code: codeToCheck,
            timePeriod: timePeriodToCheck,
          },
          {
            headers: {
              Accept: "application/json",
              ContentType: "multipart/form-data",
            },
          }
        )
        .then((res) => {
          const parsedData = JSON.parse(res.data.dane);
          this.store.$state = {
            enteredFrom: "summary",
            presentUsers: parsedData,
            idZatwierdzenia: res.data.id,
            wysylacz: res.data.wysylacz,
            dataWyslania: res.data.data_wyslania,
            view: "file-handler",
            showLists: false,
            showResults: true,
            showUpload: false,
          };
        })
        .catch((err) => {
          if (err.status == 403) {
            this.errors.status = true;
            this.errors.errMsg = err.data.message;
          }
        });
    },
  },
};
</script>
<style scoped>
.list-container {
  /* height: 100vh;
  overflow-y: auto; */
  color: var(--lotr-lightGold) !important;
}

#date-picker {
  border: 1px solid green;
}

.row-content {
  height: calc(100vh - 108px) !important;
  overflow-y: auto;
}

#no-list {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

#header-row {
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: var(--lotr-green);
}

.ui.grid > .column > h1 {
  color: var(--lotr-lightGold);
}

.shrink {
  padding-right: 0% !important;
  margin-right: 5px !important;
}
/* #header-row {
  display: flex;
}
#header-row > div:first-of-type {
  border: 1px solid red;
  display: flex;
  align-items: center !important;
  justify-content: center;
}
#header-row > div:last-of-type {
  border: 1px solid red;
  flex: 2;
  display: flex;
  align-items: center;
} */
</style>
