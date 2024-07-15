<script setup>
import { useRatesStore } from "../../stores/ratesStore";
const props = defineProps(["projects"]);
const emit = defineEmits(["details", "co"]);
const store = useRatesStore();

const showZatwierdzoneDetails = (val) => {
  emit("details", val);
};

const exportCo = (val) => {
  emit("co", val);
};
</script>
<template>
  <table class="ui celled table">
    <thead>
      <tr class="centered-tr">
        <th>Projekt</th>
        <th>Zatwierdzone LP</th>
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
        <th>Luxmed</th>
        <th>Multisport</th>
        <th>MGM</th>
        <th>Łącznie</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="project in projects"
        :class="{ positive: project.zatwierdzone == project.total }"
        class="centered-tr"
      >
        <td data-label="projekt">{{ project.name }}</td>
        <td data-label="zatwierdzone">
          {{ project.zatwierdzone }}
          <!-- /{{ project.total }} ({{
            project.percentage
          }}%) -->
        </td>
        <td data-label="rbh">{{ project.total_rbh.toLocaleString("pl") }} zł</td>
        <td data-label="rbh">{{ project.total_cost.toLocaleString("pl") }} zł</td>
        <td data-label="extra">{{ project.total_bonuses.toLocaleString("pl") }} zł</td>
        <td data-label="luxmed">{{ project.total_luxmed.toLocaleString("pl") }} zł</td>
        <td data-label="multisport">{{ project.total_multisport.toLocaleString("pl") }} zł</td>
        <td data-label="mgm">{{ project.total_mgm.toLocaleString("pl") }} zł</td>
        <td data-label="total">{{ project.total_salary.toLocaleString("pl") }} zł</td>
        <td class="collapsing">
          <div
            class="ui button"
            :class="{ disabled: project.zatwierdzone == 0 }"
            @click="showZatwierdzoneDetails(project.zatwierdzone_details)"
          >
            Szczegóły
          </div>
          <div
            class="ui button"
            :class="{ disabled: project.zatwierdzone == 0 }"
            @click="exportCo(project.name)"
          >
            Wyeksportuj dla {{ project.name }}
          </div>
        </td>
      </tr>
    </tbody>
    <tfoot class="full-width">
      <tr class="centered-tr">
        <td>SUMA:</td>
        <td colspan="9">{{ store.totalSalary.toLocaleString("pl") }} zł</td>
      </tr>
    </tfoot>
  </table>
</template>

<style>
.centered-tr {
  text-align: center;
}
</style>
