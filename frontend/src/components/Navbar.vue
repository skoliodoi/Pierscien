<template>
  <div class="ui horizontal segments main-header">
    <div class="ui segment left">
      <div class="dane-container">
        <div
          style="
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;
          "
        >
          <span>
            <div class="ui horizontal label lotr-label">Nazwa projektu</div>
            {{ store.presentUsers.project_name }}</span
          >
          <span
            ><div class="ui horizontal label lotr-label">Kod projektu</div>
            {{ store.presentUsers.code }}</span
          >
        </div>
        <div
          style="
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;
          "
        >
          <span>
            <div class="ui horizontal label lotr-label">Data</div>
            {{ store.presentUsers.time_period }}</span
          >
          <span
            ><div class="ui horizontal label lotr-label">Liczba kt</div>
            {{ store.presentUsers.total_kts }}</span
          >
        </div>
      </div>
    </div>
    <div class="ui segment" style="flex: 0.5; text-align: center; display: flex; align-items: center;">
      <!-- <PierscienIcon /> -->
      <span
            ><div class="ui horizontal label lotr-label">RAZEM</div>
            {{ Number(store.presentUsers.complete_total).toLocaleString("pl") }}zł</span
          >
    </div>
    <div class="ui segment right">
      <div class="dane-container">
        <div
          style="display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;
          "
        >
          <span>
            <div class="ui horizontal label lotr-label">Suma godzin</div>
            {{ store.presentUsers.monthly_hours }}</span
          >
          <span
            ><div class="ui horizontal label lotr-label">RBH/pracownik</div>
            {{ store.presentUsers.avg_rbh }}</span
          >
        </div>
        <div
          style="display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;
          "
        >
          <span>
            <div class="ui horizontal label lotr-label">Łączna wypłata</div>
            {{ Number(store.presentUsers.total_project_salary).toLocaleString("pl") }}zł</span
          >
          <span
            ><div class="ui horizontal label lotr-label">Średnia wypłata</div>
            {{ Number(store.presentUsers.avg_salary).toLocaleString("pl") }}zł</span
          >
        </div>
        <div
          style="display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;
          "
        >
          <span>
            <div class="ui horizontal label lotr-label">Łączne koszty</div>
            {{ Number(store.presentUsers.total_cost).toLocaleString("pl") }}zł</span
          >
          <span>
            <div class="ui horizontal label lotr-label">Łączne bonusy</div>
            {{ Number(store.presentUsers.total_bonus).toLocaleString("pl") }}zł</span
          >

        </div>
      </div>
    </div>
  </div>
</template>

<script>
import PierscienIcon from "./icons/PierscienIcon.vue";
import { useRatesStore } from "@/stores/ratesStore";
export default {
  setup() {
    const store = useRatesStore();
    return {
      store,
    };
  },
  emits: ["hideTable"],
  components: {
    PierscienIcon,
  },
  methods: {
    sendData(func) {
      $("#successModal")
        .modal({
          class: "mini inverted",
          onApprove: func,
        })
        .modal("show");
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
  height: 7rem;
  border: none !important;
  background-color: var(--lotr-green) !important;
}

.ui.segment {
  background-color: var(--lotr-darkGreen);
  color: var(--lotr-lightGold);
  font-weight: bold;
}

.ui.horizontal.label {
  width: 132px;
  text-align: center;
  margin: 5px;
}

.ui.segment.left {
  justify-content: start;
}
.ui.segment.right {
  justify-content: flex-end;
}

.ui.segment.left,
.ui.segment.right {
  display: flex !important;
  align-items: center !important;
  flex: 2 !important;
  border-radius: 0 !important;
}

.dane-container {
  width: 100%;
  display: flex;
  justify-content: space-around;
}
.lotr-modal-header,
.lotr-modal-body,
.lotr-modal-actions {
  background-color: var(--lotr-darkerGreen) !important;
  color: var(--lotr-lightGold) !important;
}

.lotr-modal-actions {
  border-top: 1px solid var(--lotr-lightGold) !important;
}

.lotr-label {
  background-color: var(--lotr-darkerGreen) !important;
  border: 1px solid var(--lotr-lightGold);
  color: var(--lotr-lightGold)
}
</style>
