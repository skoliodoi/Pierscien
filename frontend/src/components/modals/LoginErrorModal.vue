<script setup>
import { onUpdated, ref } from "vue";
import axios from "redaxios";
import config from "../../config";
const props = defineProps(["errorMsg", "showAccessBtn", "requesterLogin"]);
const emit = defineEmits(["hideError"]);
const accessOptions = [
  {
    access: "wysylacz",
    opis: "Chcę mieć możliwość dodawania list płac na moim projekcie!",
  },
  {
    access: "zatwierdzacz",
    opis: "Chcę mieć możliwość zatwierdzania wysłanych list płac, bo jestem grubą szychą!",
  },
  {
    access: "luximed",
    opis: "Chcę mieć możliwość dodawania benefitów takich jak Luxmed i Multisport!",
  },
  {
    access: "podsumowanie",
    opis: "Chcę mieć możliwość pobierania list płac do Optimy/Innych narzędzi",
  }
];
const requestSent = ref(false);
const requestSentSuccesfully = ref(false);
const selectedAccess = ref("");
const sendingRequest = ref(false);
const showAccessSelect = ref(false);
const cancelRequest = () => {
  showAccessSelect.value = false;
  selectedAccess.value = "";
  emit("hideError");
};
const sendRequest = async () => {
  sendingRequest.value = true;
  await axios
    .post(
      `${config.baseUrl}/api/request_access`,
      {
        login: props.requesterLogin,
        access: selectedAccess.value
      },
      { 
        timeout: 5000,
        headers: {
          Accept: "application/json",
        },
      }
    )
    .then(() => {
      requestSent.value = true;
      requestSentSuccesfully.value = true;
      // const dbZatwierdzenia = JSON.parse(res.data);
      // this.liczbaZatwierdzen = dbZatwierdzenia.length;
      // this.daneZatwierdzen = dbZatwierdzenia;
    })
    .catch(() => {
      requestSent.value = true;
      requestSentSuccesfully.value = false;
    });
};
onUpdated(() => {
  $("#access-select").dropdown();
});
</script>

<template>
  <div class="ui icon error message" v-if="errorMsg && !requestSent">
    <i class="notched circle loading icon" v-if="sendingRequest"></i>
    <div class="content">
      <div class="header"><strong>（￣□￣；）</strong></div>
      <p v-if="!sendingRequest">
        <strong>{{ errorMsg }} </strong>
      </p>
      <p v-else>
        <strong>Poczekaj, wysyłam prośbę o dostęp...</strong>
      </p>
      <button
        v-if="showAccessBtn && !showAccessSelect"
        class="ui facebook button"
        @click="showAccessSelect = true"
      >
        Poproszę dostęp!
      </button>
      <div class="ui form" v-if="showAccessSelect && !sendingRequest">
        <div class="two fields" style="display: flex; align-items: flex-end">
          <div class="field" style="flex: 3">
            <select
              name="access-select"
              id="access-select"
              v-model="selectedAccess"
            >
              <option value="">Wybierz swój preferowany dostęp</option>
              <option :value="option.access" v-for="option in accessOptions">
                {{ option.opis }}
              </option>
            </select>
          </div>
          <div class="field" style="flex: 1">
            <button
              class="ui facebook button"
              :class="{ disabled: !selectedAccess }"
              @click="sendRequest"
            >
              Wyślij prośbę!
            </button>
            <button class="ui facebook button" @click="cancelRequest">
              A, nieważne
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div
    class="ui icon center aligned message"
    v-else
    :class="{ success: requestSentSuccesfully, error: !requestSentSuccesfully }"
  >
    <div class="content" v-if="requestSentSuccesfully">
      <div class="header"><strong>╰(▔∀▔)╯</strong></div>
      <p>
        <strong
          >Prośba o dodanie do Pierścienia została wysłana! Ktoś powinien się do
          ciebie odezwać w tej kwestii!</strong
        >
      </p>
    </div>
    <div class="content" v-else>
      <div class="header"><strong>(ㆆ _ ㆆ)</strong></div>
      <p>
        <strong
          >Nie rozumiem... coś poszło nie tak i twoja prośba nie została wysłana. Spróbuj jeszcze raz, albo skontaktuj się bezpośrednio z kimś odpowiedzialnym za Pierścień.</strong
        >
      </p>
    </div>
  </div>
</template>
<style scoped>
.ui.success.message {
  position: absolute;
  top: 0;
  width: 100%;
  text-align: center;
}
</style>
