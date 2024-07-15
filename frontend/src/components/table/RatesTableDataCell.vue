<template>
  <td class="my-td selectable">
    <div class="td-cell" style="display: flex; flex-direction: column">
      <div class="td-head">
        <h5>
          Stawka: {{ Number(cellData.stawka_za_dzien).toLocaleString("pl") }}zł
        </h5>
        (<span class="ui normal text">{{ cellData.rodzaj_umowy }}</span
        >)
      </div>
      <div class="td-body">
        <div class="stawki">
          <div>
            <h5>Dniówka:</h5>
            <span>{{ Number(cellData.kwota).toLocaleString("pl") }}zł</span>
          </div>
          <div>
            <h5>Koszt:</h5>
            <span
              >{{
                Number(cellData.koszt_pracodawcy).toLocaleString("pl")
              }}zł</span
            >
          </div>
          <div>
            <h5>Łącznie:</h5>
            <span
              >{{
                Number(cellData.kwota_z_kosztem).toLocaleString("pl")
              }}zł</span
            >
          </div>
        </div>
        <div class="godziny">
          <div>
            <h5>Liczba godzin:</h5>
            <span>{{ cellData.suma_godzin }}</span>
          </div>
          <div>
            <h5>W tym nieefektywne:</h5>
            <span v-if="cellData.w_tym_nieEFE">{{
              cellData.w_tym_nieEFE
            }}</span>
            <span v-else>0</span>
          </div>
          <div>
            <h5>W tym szkoleniowe:</h5>
            <span v-if="cellData.w_tym_nieEFE">{{
              cellData.w_tym_szkoleniowe
            }}</span>
            <span v-else>0</span>
          </div>
        </div>
      </div>
    </div>
  </td>
</template>

<script>
export default {
  props: ["cellData"],
};
</script>

<style scoped>
h5 {
  margin-bottom: 2px;
}
.my-td {
  padding: 0 !important;
  height: 14em !important;
  border: 1px solid var(--lotr-green) !important;
}
.td-cell {
  width: 20rem !important;
  display: flex !important;
  height: 100% !important;
}
.godziny {
  flex: 2;
}
.stawki {
  flex: 1.5;
  border-right: 1px solid rgba(34, 36, 38, 0.1);
}

.godziny,
.stawki {
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  height: 100%;
}


.td-head {
  background-color: var(--lotr-green);
  padding: 0;
  color: var(--lotr-lightGold);
}
.td-body {
  display: flex;
  flex-grow: 1;
}
</style>
