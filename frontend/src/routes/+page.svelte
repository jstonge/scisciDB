<!-- frontend/src/routes/Dashboard.svelte -->
<script>
	import { getCounts } from './data.remote.js';
</script>

<div class="dashboard">
	<h1>Testing Remote Functions</h1>
	
	<h2>Venue Counts:</h2>
	
	{#await getCounts()}
		<p>Loading venue data...</p>
	{:then counts}
		{#each counts as item}
			<div class="item">
				Venue: {item.venue}, Year: {item.year}, Count: {item.count}
			</div>
		{/each}
	{:catch error}
		<p>Error loading data: {error.message}</p>
	{/await}
</div>

<style>
	.dashboard {
		padding: 2rem;
	}
	
	.item {
		padding: 0.5rem;
		margin: 0.5rem 0;
		border: 1px solid #ddd;
		border-radius: 4px;
	}
</style>