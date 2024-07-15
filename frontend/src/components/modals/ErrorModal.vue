<script setup>
import PierscienIcon from "../icons/PierscienIcon.vue";
const props = defineProps({
  message: String,
});
</script>

<template>
  <div class="ui modal" id="summary-error-modal">
    <div class="center aligned header lotr-modal-header" style="height: 100px">
      <PierscienIcon />
      <div class="sub header">{{ headerData }}</div>
    </div>
    <div class="center aligned content lotr-modal-body">
      <p>{{ message }}</p>
    </div>
    <div class="centered actions lotr-modal-actions">
      <div class="ui deny button lotr">Rozumiem</div>
    </div>
  </div>
</template>

<script>
export default {
  computed: {
    headerData() {
        return "Coś poszło nie tak!"
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
