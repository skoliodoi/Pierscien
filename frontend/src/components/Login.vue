<script setup>
import { ref } from "vue";
import { useUsersStore } from "@/stores/usersStore";
import { useRatesStore } from "@/stores/ratesStore";
import PierscienIcon from "./icons/PierscienIcon.vue";
import LoginErrorModal from "./modals/LoginErrorModal.vue";

const usersStore = useUsersStore();
const ratesStore = useRatesStore();
const userLogin = ref("");
const userPass = ref("");
const errorMsg = ref("");
const askForAccess = ref(false);
const isLoggingIn = ref(false);

const cancelError = () => {
  errorMsg.value = "";
  userLogin.value = "";
  userPass.value = "";
}

const login = async () => {
  isLoggingIn.value = true;
  const result = await usersStore.checkUser(userLogin.value, userPass.value);
  if (result.error) {
    if (result.errStat == 401) {
      askForAccess.value = true;
    } else {
      askForAccess.value = false;
    }
    errorMsg.value = result.errMsg;
    isLoggingIn.value = false;
    return;
  }
  userLogin.value = "";
  userPass.value = "";
  ratesStore.$state = {
    view: "main",
  };
  isLoggingIn.value = false;
};
</script>
<template>
  <LoginErrorModal :requester-login="userLogin" :error-msg="errorMsg" :show-access-btn="askForAccess" @hide-error="cancelError" v-if="errorMsg"/>
  <div id="login-container">
    <div style="display: flex;" id="input-container">
      <div>
        <PierscienIcon :class="{ spinning: isLoggingIn }" />
      </div>
      
      <div class="ui form error">
        <div class="field">
          <label style="color: var(--lotr-lightGold)">Login użytkownika:</label>
          <input type="text" v-model="userLogin" />
        </div>
        <div class="field">
          <label style="color: var(--lotr-lightGold)">Hasło użytkownika:</label>
          <input type="password" v-model="userPass" />
        </div>
        
        <div style="text-align: center">
          <div class="ui button lotr" @click="login">Zaloguj się</div>
        </div>
      </div>
    </div>
    <div>
    </div>
   
  </div>
</template>

<style>
.ui.error.message {
  position: absolute;
  top: 0;
  width: 100%;
  text-align: center;
}



#login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
}
</style>
