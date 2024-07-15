<script setup>
import Login from "./Login.vue";
import IntroScreen from "@/components/IntroScreen.vue";
import FileHandler from "@/components/FileHandler.vue";
import ListOfLists from "@/components/ListOfLists.vue";
import Benefits from "@/components/Benefits.vue";
import FinalSummary from "@/components/final-step-components/FinalSummaryMainView.vue";
import VccLogo from "./icons/VccLogo.vue";
import { useRatesStore } from "@/stores/ratesStore";
import { useUsersStore } from "@/stores/usersStore";
import { onMounted } from "vue";
const rates = useRatesStore();
const users = useUsersStore();
onMounted(()=>{
  users.getUserData();
})
</script>

<template>
  <Login v-if="!users.loggedUser" />
  <div v-else>
    <IntroScreen v-if="rates.view == 'main'" />
    <FileHandler v-if="rates.view == 'file-handler'" />
    <ListOfLists v-if="rates.view == 'lists'" />
    <Benefits v-if="rates.view == 'benefits'" />
    <FinalSummary v-if="rates.view == 'rates-summary'" />
  </div>
  <div style="display: flex; justify-content: center;" v-if="rates.view == 'main' || !users.loggedUser">
    <div id="logo-container">
      <VccLogo></VccLogo>
    </div>
  </div>
</template>
