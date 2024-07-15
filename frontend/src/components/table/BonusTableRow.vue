<template>
	<tr>   
		<BonusTableDataCell style="border: 1px solid black;" v-for="each in rowData" :cellData="each" />
	</tr>
</template>

<script>
	import BonusTableDataCell from "./BonusTableDataCell.vue";
	export default {
		props: ["rowData"],
		components: {
			BonusTableDataCell,
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