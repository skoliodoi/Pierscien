<script setup>
import { useUsersStore } from "@/stores/usersStore";
import { useRatesStore } from "@/stores/ratesStore";
import PierscienIcon from "./icons/PierscienIcon.vue";

// import { onMounted } from "vue";
// onMounted(() => {
//   $("#example1").progress();
// });
// access the `store` variable anywhere in the component ✨
const users = useUsersStore();
const rates = useRatesStore();

const goTo = (location, user, conductAction = false) => {
  if (conductAction == "getLists") {
    rates.getLists();
  }


  // users.$state = {
  //   loggedUserAccess: user,
  //   loggedUser: `${user}test`,
  // };
  rates.$state = {
    view: location,
  };
};

const logout = () => {
  sessionStorage.clear();
  users.loggedUser = "";
  users.loggedUserAccess = "";
  users.loggedUserName = "";
};
</script>
<template>
  <div style="position: absolute; margin: 10px" @click="logout">
    <button class="ui button lotr-inverted">Wyloguj się</button>
  </div>
  <div class="ui container screen-container">
    <div
    class="ui card"
    style="background-color: transparent; box-shadow: none"
    >
    <strong style="text-align: center; color:var(--lotr-gold)">Cześć, {{ users.loggedUserName }}!</strong>
    <div class="content" style="text-align: center">
      <div class="header" style="color: var(--lotr-gold)">
          <PierscienIcon />
        </div>
      </div>
      <div class="content button-content" style="">
        <button
          v-if="users.lowerAccess"
          class="ui button lotr"
          @click="goTo('file-handler', 'wysylacz')"
        >
          Wyślij dane
        </button>
        <button
          v-if="users.higherAccess"
          class="ui button lotr"
          @click="goTo('lists', 'zatwierdzacz', 'getLists')"
        >
          Sprawdź/zatwierdź dane
        </button>
        <button
          v-if="users.multisportAccess"
          class="ui button lotr"
          @click="goTo('benefits', 'zatwierdzacz')"
        >
          Multisporty i inne pierdoły
        </button>
        <button
          v-if="users.summaryAccess || users.higherAccess"
          class="ui button lotr"
          @click="goTo('rates-summary', 'podsumowanie', 'getDates')"
        >
          Pobieram dane
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.screen-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
}
.button-content {
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  height: 15rem;
}
</style>
