<template>
  <SummaryView v-if="!showDetails" @show-details="showDetails = true" />
  <RatesTable v-else @returnToMain="showDetails = false" />
</template>
<script>
import RatesTable from "./table/RatesTable.vue";
import SummaryView from "./SummaryView.vue";
export default {
  components: {
    RatesTable,
    SummaryView
  },
  data() {
    return {
      showDetails: false,
    };
  },
};
</script>
<style></style>
