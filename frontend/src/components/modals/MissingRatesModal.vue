<script setup>
import { useRatesStore } from "../../stores/ratesStore";
const props = defineProps(["missingRates"])
const store = useRatesStore();
const downloadExcel = async () => {
  store.getExcel();
}
</script>

<template>
  <div class="ui inverted modal">
    <div class="centered header">
      <h2 class="ui header">
        Uwaga!
        <div class="sub header">
          Mocarz ID poniższych konsultantów nie mają przypisanych stawek w Mocarzu - czy na pewno są poprawne?
        </div>
        <div class="sub header">
          W związku z tym ich wypłaty nie mogą zostać poprawnie naliczone.
        </div>
        <div class="sub header">
          Upewnij się, że pliki źródłowe zawierają poprawne dane, lub skonsultuj się z działem HR w celu uzupełnienia stawek.
        </div>
      </h2>
    </div>

    <div class="centered scrolling content">
      <p v-for="user in missingRates" :key="user.mocarz_id">{{ user.name }} (<strong>{{ user.mocarz_id }}</strong>)</p>
    </div>
    <div class="center aligned actions">
      <div
        class="ui left labeled icon button lotr"
        @click="downloadExcel"
      > 
        Pobierz szczegóły 
        <i class="checkmark icon"></i>
      </div>
      <div
        class="ui negative right labeled icon button"
      >
        W takim razie anuluj
        <i class="times icon"></i>
      </div>
    </div>
  </div>
</template>
<!-- <script>
// export default {
//   props: ["missingRates"],
// };
</script> -->
<style scoped>
#missing-users,
.centered.header {
  background-color: var(--lotr-darkerGreen) !important;
  color: var(--lotr-lightGold) !important;
}

.header {
  color: var(--lotr-lightGold) !important;

}

.centered.scrolling.content {
  color: var(--lotr-lightGold) !important;
  background-color: var(--lotr-green) !important;
}

.actions {
  background-color: var(--lotr-darkerGreen) !important;
}

/* .ui.negative.right.labeled.icon.button {
  background-color: greenyellow !important;
} */
</style>
