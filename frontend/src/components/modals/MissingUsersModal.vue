<template>
  <div class="ui inverted modal">
    <div class="centered header">
      <h2 class="ui header">
        Uwaga!
        <div class="sub header">
          Poniżsi konsultanci są zaznaczeni jako "aktywni" w Mocarzu.
        </div>
        <div class="sub header">
          Nie pojawiają się jednak w przesłanym pliku. Czy na pewno plik jest
          kompletny?
        </div>
        <div class="sub header">
          Zaznaczenie checkboxów przy użytkownikach oznacza potwierdzenie.
        </div>
      </h2>
    </div>

    <div class="centered scrolling content">
      <div
        v-for="user in missingUsers"
        :key="user.mocarz_id"
        style="
          display: flex;
          justify-content: center;
          align-items: center;
          margin-bottom: 20px;
        "
      >
        <div style="flex: 0.3">
          {{ user.name }} (<strong>{{ user.mocarz_id }}</strong
          >)
        </div>
        <input
          class="ui checkbox"
          type="checkbox"
          v-model="selectedCheckboxes"
          :value="user.mocarz_id"
        />
      </div>
    </div>
    <div class="center aligned actions" id="zaznacz-wszystkich" style="">
      <input type="checkbox" class="ui checkbox" @change="selectAll($event)" />
      <div style="margin-left: 15px">
        <strong>Zaznacz wszystkich</strong>
      </div>
    </div>
    <div class="center aligned actions">
      <div
        class="ui positive left labeled icon button"
        :class="{ disabled: selectedCheckboxes.length != missingUsers.length }"
      >
        Kontynuuj
        <i class="checkmark icon"></i>
      </div>
      <div class="ui negative right labeled icon button">
        W takim razie anuluj
        <i class="times icon"></i>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  props: ["missingUsers"],
  data() {
    return {
      selectedCheckboxes: [],
    };
  },
  methods: {
    checkboxEvent(val) {
      val.target.checked == true
        ? (this.checkedCheckboxes += 1)
        : (this.checkedCheckboxes -= 1);
    },
    selectAll(val) {  
      if (val.target.checked) {
        for (const each of this.missingUsers) {
          if (!this.selectedCheckboxes.includes(each.mocarz_id)) {
            this.selectedCheckboxes.push(each.mocarz_id);
          }
        }
      } else {
        this.selectedCheckboxes = [];
      }
    },
  },
};
</script>
<style scoped>
#missing-users,
.centered.header {
  background-color: var(--lotr-darkerGreen) !important;
  color: var(--lotr-lightGold) !important;
}

.header {
  color: var(--lotr-lightGold) !important;
}

.centered.scrolling.content {
  color: var(--lotr-lightGold) !important;
  background-color: var(--lotr-green) !important;
}

.actions {
  background-color: var(--lotr-darkerGreen) !important;
  color: var(--lotr-lightGold) !important;
}

#zaznacz-wszystkich {
  display: flex;
  justify-content: center;
}
/* .ui.negative.right.labeled.icon.button {
  background-color: greenyellow !important;
} */
</style>
