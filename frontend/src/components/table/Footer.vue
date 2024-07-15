<template>
  <!-- <SuccessModal /> -->
  <ConfirmationModal />
  <RejectionModal @rejection-reason="rejectData" />
  <div class="ui horizontal segments main-header">
    <div class="ui container control-buttons">
      <button
        v-if="!czyZatwierdzacz"
        class="ui button lotr"
        @click="showConfirmation(this, 'Wyślij')"
      >
        Wyślij do zatwierdzenia
      </button>
      <button v-else class="ui button lotr" @click="showConfirmation(this, 'Zatwierdź')">
        Zatwierdź
      </button>
      <button
        v-if="czyZatwierdzacz"
        class="ui button lotr"
        @click="showRejection"
      >
        Odrzuć
      </button>
      <button class="ui button lotr" @click="returnToMain">
        Wróć do podsumowania
      </button>
      <button
        class="ui button lotr"
        @click="
          store.$state = { showResults: false, showUpload: true, view: 'main' }
        "
      >
        Anuluj
      </button>
    </div>
  </div>
</template>

<script>
import { useRatesStore } from "@/stores/ratesStore";
import { useUsersStore } from "@/stores/usersStore";
import PierscienIcon from "../icons/PierscienIcon.vue";
// import SuccessModal from "../modals/SuccessModal.vue";
import ConfirmationModal from "../modals/ConfirmationModal.vue";
import RejectionModal from "../modals/RejectionModal.vue";
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
    // SuccessModal,
    ConfirmationModal,
    RejectionModal
  },
  emits: ["hideTable", "commitAction"],
  props: ["code", "time_period"],
  computed: {
    czyZatwierdzacz() {
      return this.usersStore.loggedUserAccess == "zatwierdzacz" ? true : false;
    },
  },
  methods: {
    showConfirmation(val, action) {
      $("#confirmationModal")
        .modal({
          closeable: false,
          class: "mini inverted",
          onApprove() {
            val.sendData(action);
          },
        })
        .modal("show");
    },
    showRejection() {
      $("#rejectionModal").modal({
        closable: false
      }).modal('show')
    },    
    rejectData(reason) {
      this.store.spin = true;
      this.store.spinMessage = "odrzucanie"
      this.store.rejectRates(reason, this.code, this.time_period)
    },
    async sendData(action) {
      this.$emit("commitAction", action);
    },
    returnToMain() {
      this.$emit("hideTable");
    },
  },
};
</script>

<style scoped>
.main-header {
  margin: 0 !important;
  border-radius: 0 !important;
  height: 75px;
  border: none !important;
  background-color: var(--lotr-darkGreen) !important;
}
.control-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* .ui.segment {
  background-color: var(--lotr-darkGreen);
  color: var(--lotr-lightGold);
  font-weight: bold;
} */
</style>
