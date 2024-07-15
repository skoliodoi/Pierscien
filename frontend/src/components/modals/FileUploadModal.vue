<script setup>
import PierscienIcon from "../icons/PierscienIcon.vue";
const props = defineProps({
  code: Number,
  message: String,
});
</script>

<template>
  <div class="ui modal" id="fileUpload">
    <div class="center aligned header lotr-modal-header" style="height: 100px">
      <PierscienIcon />
      <div class="sub header">{{ headerData }}</div>
    </div>
    <div class="center aligned content lotr-modal-body">
      <p>{{ message }}</p>
    </div>
    <div class="centered actions lotr-modal-actions" v-if="code == 406 || code == 422">
      <div class="ui deny button lotr">Rozumiem</div>
    </div>
    <div class="centered actions lotr-modal-actions" v-else>
      <div class="ui approve button lotr">Potwierdzam</div>
      <div class="ui deny button lotr">Anuluj</div>
    </div>
  </div>
</template>

<script>
export default {
  computed: {
    headerData() {
      if (this.code == 406 || this.code == 422) {
        return "Załadowanie pliku przerwane z powodu błędu!"
      } else {
        return "Potwierdź załadowanie pliku"
      }
    },
  },
};
</script>

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
