<script setup>
import PierscienIcon from "../icons/PierscienIcon.vue";
import { useRatesStore } from "@/stores/ratesStore";

// access the `store` variable anywhere in the component ✨
const store = useRatesStore();
</script>

<template>
  <div class="ui modal" id="successModal">
    <div class="center aligned header lotr-modal-header" style="height: 100px">
      <PierscienIcon />
    </div>
    <div class="center aligned content lotr-modal-body">
      <!-- <p>
        Twój plik został załadowany do bazy danych i oczekuje na zatwierdzenie.
      </p> -->
      <p v-for="sentence in store.splitMsg">
        <strong>{{ sentence }}</strong>
      </p>
      <!-- <p>W razie problemów na pewno się o tym dowiesz.</p> -->
    </div>
    <div class="centered actions lotr-modal-actions">
      <div class="ui approve button lotr">OK</div>
    </div>
  </div>
</template>
<style scoped>
.lotr-modal-header,
.lotr-modal-body,
.lotr-modal-actions {
  background-color: var(--lotr-darkerGreen) !important;
  color: var(--lotr-lightGold) !important;
}

.lotr-modal-actions {
  border-top: 1px solid var(--lotr-lightGold) !important;
}
</style>
