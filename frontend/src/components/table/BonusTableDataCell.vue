<template>
	<td class="my-td selectable">
		<div class="td-cell">
			<div class="stawki">
				<div>
					<h5>Kwota:</h5>
					<span>{{cellData.kwota}}zł</span>
				</div>
			</div>
			<div class="godziny" >
				<div>
					<h5>Kategoria:</h5>
					<span v-if="cellData.kategoria">{{cellData.kategoria}}</span>
					<span v-else>Brak</span>
				</div>
        <div class="ui divider"></div>
				<div style="overflow-x: auto;">
					<h5>Komentarz:</h5>
					<span v-if="cellData.komentarz">{{cellData.komentarz}}</span>
					<span v-else>Brak</span>
				</div>
			</div>
		</div>
	</td>
</template>

<script>
	export default {
    props: ['cellData']
  };
</script>

<style scoped>
	h5 {
		margin-bottom: 2px;
	}
	.my-td {
		padding-top: 0 !important;
		padding-bottom: 0 !important;
		height: 12em !important;
	}
	.td-cell {
		width: 35rem !important;
		display: flex !important;
		justify-content: space-between;
		height: 100% !important;
	}
	.godziny {
		flex: 2;
	}
	.stawki {
		flex: 1.5;
    border-right: 1px solid rgba(34,36,38,.1);
	}
  

	.godziny,
	.stawki {
		display: flex;
		flex-direction: column;
		justify-content: space-around;
		padding: 10px;
	}
</style>