<template>
  <tr>
    <td v-for="each in rowData.dane" >{{ each.data }}</td>
  </tr>
	<tr>
		<!-- <td data-label="Name" style="border: 1px solid black;">
			{{ rowData.imie_i_nazwisko }}
			{{ rowData.mocarz_id }}
		</td>
		<td data-label="Name" style="border: 1px solid black;">
			{{ rowData.total_salary }}zł
		</td> -->
    
		<RatesTableDataCell style="border: 1px solid black;" v-for="each in rowData.dane" :cellData="each" />
	</tr>
</template>

<script>
	import RatesTableDataCell from "./RatesTableDataCell.vue";
	export default {
		props: ["rowData"],
		components: {
			RatesTableDataCell,
		},
	};
</script>

<style>
	/* tr td:first-child {
		position: sticky;
		left: 0;
		background: white;
		z-index: 1;
	} */
</style>