<script setup>
import {computed} from "vue";
const props = defineProps(["details"]);
const emit = defineEmits(["backToSummary"]);


const totalSalary = computed(() => {
  let totalSum = 0;
  for (const each of props.details) {
    totalSum += each.total;
  }
  console.log(typeof(totalSum.toFixed(2)))
  return totalSum.toLocaleString("pl")
});
const backToSummaryHandler = () => {
  emit('backToSummary');
};
</script>

<template>
  <table class="ui celled scrolling table">
    <thead>
      <tr class="centered-tr">
        <th>Projekt</th>
        <th>Kod Projektu</th>
        <th>RBH</th>
        <th>Koszt pracodawcy</th>
        <th>
          <div
            data-inverted=""
            data-tooltip="Np. bonusy, premie, zaległe szkoleniowe itd."
          >
            Dodatkowe wypłaty
          </div>
        </th>
        <th>Łącznie</th>
      </tr>
    </thead>
    <tbody>
      <tr class="centered-tr" v-for="detail in details">
        <td data-label="projekt">{{ detail.project_name }}</td>
        <td data-label="zatwierdzone">{{ detail.project_code }}</td>
        <td data-label="rbh">{{ detail.rbh.toLocaleString("pl") }} zł</td>
        <td data-label="koszt">{{ detail.cost.toLocaleString("pl") }} zł</td>
        <td data-label="extra">{{ detail.bonuses.toLocaleString("pl") }} zł</td>
        <td data-label="total">{{ detail.total.toLocaleString("pl") }} zł</td>
      </tr>
      <!-- <tr class="centered-tr">
        <td data-label="projekt">Projekt A</td>
        <td data-label="zatwierdzone">Projekt A</td>
        <td data-label="rbh">Test zł</td>
        <td data-label="extra">Test zł</td>
        <td data-label="total">Test zł</td>
      </tr>
      <tr class="centered-tr">
        <td data-label="projekt">Projekt A</td>
        <td data-label="zatwierdzone">Projekt A</td>
        <td data-label="rbh">Test zł</td>
        <td data-label="extra">Test zł</td>
        <td data-label="total">Test zł</td>
      </tr>
      <tr class="centered-tr">
        <td data-label="projekt">Projekt A</td>
        <td data-label="zatwierdzone">Projekt A</td>
        <td data-label="rbh">Test zł</td>
        <td data-label="extra">Test zł</td>
        <td data-label="total">Test zł</td>
      </tr>
      <tr class="centered-tr">
        <td data-label="projekt">Projekt A</td>
        <td data-label="zatwierdzone">Projekt A</td>
        <td data-label="rbh">Test zł</td>
        <td data-label="extra">Test zł</td>
        <td data-label="total">Test zł</td>
      </tr>
      <tr class="centered-tr">
        <td data-label="projekt">Projekt A</td>
        <td data-label="zatwierdzone">Projekt A</td>
        <td data-label="rbh">Test zł</td>
        <td data-label="extra">Test zł</td>
        <td data-label="total">Test zł</td>
      </tr>
      <tr class="centered-tr">
        <td data-label="projekt">Projekt A</td>
        <td data-label="zatwierdzone">Projekt A</td>
        <td data-label="rbh">Test zł</td>
        <td data-label="extra">Test zł</td>
        <td data-label="total">Test zł</td>
      </tr>
      <tr class="centered-tr">
        <td data-label="projekt">Projekt A</td>
        <td data-label="zatwierdzone">Projekt A</td>
        <td data-label="rbh">Test zł</td>
        <td data-label="extra">Test zł</td>
        <td data-label="total">Test zł</td>
      </tr>
      <tr class="centered-tr">
        <td data-label="projekt">Projekt A</td>
        <td data-label="zatwierdzone">Projekt A</td>
        <td data-label="rbh">Test zł</td>
        <td data-label="extra">Test zł</td>
        <td data-label="total">Test zł</td>
      </tr>
      <tr class="centered-tr">
        <td data-label="projekt">Projekt A</td>
        <td data-label="zatwierdzone">Projekt A</td>
        <td data-label="rbh">Test zł</td>
        <td data-label="extra">Test zł</td>
        <td data-label="total">Test zł</td>
      </tr>
      <tr class="centered-tr">
        <td data-label="projekt">Projekt A</td>
        <td data-label="zatwierdzone">Projekt A</td>
        <td data-label="rbh">Test zł</td>
        <td data-label="extra">Test zł</td>
        <td data-label="total">Test zł</td>
      </tr>
      <tr class="centered-tr">
        <td data-label="projekt">Projekt A</td>
        <td data-label="zatwierdzone">Projekt A</td>
        <td data-label="rbh">Test zł</td>
        <td data-label="extra">Test zł</td>
        <td data-label="total">Test zł</td>
      </tr>
      <tr class="centered-tr">
        <td data-label="projekt">Projekt A</td>
        <td data-label="zatwierdzone">Projekt A</td>
        <td data-label="rbh">Test zł</td>
        <td data-label="extra">Test zł</td>
        <td data-label="total">Test zł</td>
      </tr>
      <tr class="centered-tr">
        <td data-label="projekt">Projekt A</td>
        <td data-label="zatwierdzone">Projekt A</td>
        <td data-label="rbh">Test zł</td>
        <td data-label="extra">Test zł</td>
        <td data-label="total">Test zł</td>
      </tr>
      <tr class="centered-tr">
        <td data-label="projekt">Projekt A</td>
        <td data-label="zatwierdzone">Projekt A</td>
        <td data-label="rbh">Test zł</td>
        <td data-label="extra">Test zł</td>
        <td data-label="total">Test zł</td>
      </tr>
      <tr class="centered-tr">
        <td data-label="projekt">Projekt A</td>
        <td data-label="zatwierdzone">Projekt A</td>
        <td data-label="rbh">Test zł</td>
        <td data-label="extra">Test zł</td>
        <td data-label="total">Test zł</td>
      </tr>
      <tr class="centered-tr">
        <td data-label="projekt">Projekt A</td>
        <td data-label="zatwierdzone">Projekt A</td>
        <td data-label="rbh">Test zł</td>
        <td data-label="extra">Test zł</td>
        <td data-label="total">Test zł</td>
      </tr> -->
    </tbody>
    <tfoot class="full-width">
      <tr class="centered-tr">
        <td>SUMA:</td>
        <td colspan="3">{{totalSalary}} zł</td>

        <td>
          <button class="ui button" @click="backToSummaryHandler">
            Wróć do podsumowania
          </button>
        </td>
      </tr>
    </tfoot>
  </table>
</template>
<style scoped></style>
