<script setup>
import PierscienIcon from "../icons/PierscienIcon.vue";
const props = defineProps(['message'])
</script>

<template>
  <div class="ui modal" id="confirmationModal">
    <div class="center aligned header lotr-modal-header" style="height: 100px">
      <PierscienIcon />
      <div class="sub header">Na pewno?</div>
    </div>
    <div class="center aligned content lotr-modal-body">
      <p v-if="message ==''">Tej akcji nie da się cofnąć!</p>
      <p v-else>{{ message }}</p>
    </div>
    <div class="centered actions lotr-modal-actions">
      <div class="ui approve button lotr">Potwierdzam</div>
      <div class="ui deny button lotr">Anuluj</div>
    </div>
  </div>
</template>
<style scoped>
#confirmationModal {
  background-color: transparent;
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
</style>
