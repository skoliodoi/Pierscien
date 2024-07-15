<script setup>
import PierscienIcon from "../icons/PierscienIcon.vue";
const props = defineProps(["message"]);
</script>

<template>
  <div
    class="ui modal"
    id="rejectionModal"
    style="background-color: transparent"
  >
    <div class="center aligned header lotr-modal-header" style="height: 100px">
      <PierscienIcon />
      <div class="sub header">Lista płac zostanie odrzucona</div>
    </div>
    <div class="content lotr-modal-body">
      <div class="ui left corner labeled input" style="width: 100%">
        <div class="ui left corner label">
          <i class="asterisk icon"></i>
        </div>
        <textarea
          v-model="rejectionReason"
          rows="5"
          placeholder="Podaj powód"
          style="width: 100%; resize: none"
        ></textarea>
      </div>
    </div>
    <div class="centered actions lotr-modal-actions">
      <div
        class="ui approve button lotr"
        :class="{ disabled: !rejectionReason }"
        @click="rejectionHandler"
      >
        Odrzuć
      </div>
      <div class="ui deny button lotr">Anuluj</div>
    </div>
  </div>
</template>
<script>
import { useRatesStore } from "@/stores/ratesStore";
import { useUsersStore } from "@/stores/usersStore";
export default {
  setup() {
    const store = useRatesStore();
    const usersStore = useUsersStore();
    return {
      store,
      usersStore,
    };
  },
  emits: ["rejectionReason"],
  data() {
    return {
      rejectionReason: "",
    };
  },
  methods: {
    rejectionHandler() {
      this.$emit('rejectionReason', this.rejectionReason);
      this.rejectionReason = "";
    }
  }
};
</script>
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
