<!-- Dashboard.svelte -->
<script>
  import { getVenues, getFilteredPapers } from './data.remote.js';
  import { Plot, BarY } from 'svelteplot';
  
  let selectedVenue = $state('Nature');
  let minYear = $state(1970);
  
  // Get filtered data reactively
  let displayData = $derived(getFilteredPapers({ venue: selectedVenue, minYear }));
</script>

<div class="dashboard">
  <h1>Publications Dashboard</h1>
  
  <!-- Controls -->
  <div class="controls">
    <label>
      Venue:
      {#await getVenues()}
        <select disabled>
          <option>Loading venues...</option>
        </select>
      {:then venues}
        <select bind:value={selectedVenue}>
          {#each venues as venue}
            <option value={venue}>{venue}</option>
          {/each}
        </select>
      {:catch error}
        <select disabled>
          <option>Error loading venues</option>
        </select>
      {/await}
    </label>
    
    <label>
      From Year: {minYear}
      <input 
        type="range" 
        bind:value={minYear}
        min="1900"
        max="2025"
        step="1"
      >
    </label>
  </div>
  
  <!-- Debug: Show raw data -->
  {#await displayData}
    <p>Loading...</p>
  {:then data}
    
      <div class="chart-container">
        <!-- Try simple data format first -->
        <Plot 
          grid 
          x={{tickRotate: 40, label: ""}}
          marginRight={40}
          title="{selectedVenue} Publications by Year"
        >
          <BarY 
            data={data}
            x="year"
            y="count"
          />
        </Plot>
      </div>
  {/await}
</div>

<style>
  .dashboard {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .controls {
    display: flex;
    gap: 2rem;
    align-items: center;
    background: #f5f5f5;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
    flex-wrap: wrap;
  }
  
  .controls label {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .controls select {
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
  }
  
  .debug {
    background: #fff3cd;
    padding: 1rem;
    border-radius: 4px;
    margin: 1rem 0;
    border: 1px solid #ffeaa7;
  }
  
  .chart-container {
    width: 100%;
    padding: 1rem 0;
  }
</style>