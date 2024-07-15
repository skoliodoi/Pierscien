<template>
  <FileUpload
    v-if="showUpload"
    @showResults="store.$state = { showResults: true }"
  />
  <Results v-if="showResults" />
  <ListOfLists v-if="showLists" />
</template>

<script>
import { useRatesStore } from "@/stores/ratesStore";
import { useUsersStore } from "@/stores/usersStore";
import FileUpload from "./FileUpload.vue";
import Results from "./Results.vue";
import ListOfLists from "./ListOfLists.vue"
export default {
  components: {
    FileUpload,
    Results,
    ListOfLists
  },
  setup() {
    const store = useRatesStore();
    const usersStore = useUsersStore();
    return {
      store,
      usersStore,
    };
  },
  // mounted() {
  //   this.usersStore.checkUsers();
  // },
  // updated() {
  //   this.usersStore.checkUsers();
  // },
  computed: {
    showUpload() {
      return this.store.showUpload;
    },
    showResults() {
      return this.store.showResults;
    },
    showLists() {
      return this.store.showLists;
    },
  },
};
</script>

<style></style>
