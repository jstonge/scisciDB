<!-- +page.svelte -->
<script>
    import { getVenues, getAllPapers } from './data.remote.js';
    import { Plot, BarY, HTMLTooltip } from 'svelteplot';
    
    let selectedVenue = $state('Nature');
    let minYear = $state(1970);
  
    // Get filtered data reactively
    //   let displayData = $derived(getFilteredPapers({ venue: selectedVenue, minYear }));
    let displayData = $derived(async () => {
        const allPapers = await getAllPapers();
        return allPapers.filter(p => p.venue === selectedVenue && p.year >= minYear);
    });
    </script>

<div class="dashboard">
    <h1>A whirldwind tour of <a href="https://github.com/jstonge/scisciDB">SciSciDB</a></h1>
    
    <p>We introduce useful snapshots of databases are hosted at the University of Vermont, namely <a href="https://api.semanticscholar.org/api-docs/datasets">semantic scholar</a>, ... (more to come). Most snapshots are supplement to their API, which are awesome. Here we provide information specific to projects at the <a href="https://github.com/Vermont-Complex-Systems/">Vermont Complex Systems Institute</a>.</p>

    <h2>The <a href="https://api.semanticscholar.org/api-docs/datasets">Semantic Scholar</a> snapshot</h2>

    <p>This database is particularly useful in that it provides fully parsed text for over 16M papers, their embedding using AllenAI's <a href="https://huggingface.co/allenai/specter2">Specter2</a> embeddings, and the 2.4B citation graph that goes with all the papers. They also provide a collection of open-source methods tools on top of the data, such as their custom <a href="https://github.com/allenai/s2_fos">field of study</a>  classifier, a spaCy pipeline for medical documents (<a href="https://github.com/allenai/scispacy">scispacy</a>), and many more.</p>

    <h3>Examining field of studies</h3>

    <p>We start by looking at the number of papers by field of studies to know the bias in the database. We already know from the papers that computer science papers are heavily represented, by virtue of being more openly available, than, say, economics or information science. The question is more; how bad is it is.</p>

    <p>Here is the macro perspective, looking at the counts of papers by field of studie</p>

    <p>[INSERT BARCHART]</p>

    <p>We now use a streamgraph to know the decomposition of fields of studies over time:</p>

    <p>[INSERT STREAMGRAPH]</p>

    <h3>Time series venues</h3>
    
    <p>For a project, we wanted to know about the evolution of data sharing practices. We decided to sample the data by venue, as journal policies with respect to methods matter. Here we look at a time series by "top" venues, here simply defined by the venues' h5-index found on Google Scholar (we also use Google Scholar's subcategories of journals to classify papers).  We use color to indicate how many of available papers have been parsed out of all available papers in that venue.</p>
    
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
    
    {#await displayData}
        <p>Loading...</p>
    {:then data}    
        <div class="chart-container">
            <Plot 
            x={{tickRotate: 40, label: ""}}
            y={{grid: true}}
            height={300}
            marginRight={40}
            subtitle="{selectedVenue} Publications by Year"
            >
            <BarY 
                {data}
                x="year"
                y="count"
                fillOpacity=0.1
                stroke="black"
            />
            {#snippet overlay()}
                <HTMLTooltip
                    {data}
                    x="year"
                    y="count">
                    {#snippet children({ datum })}
                        <div>
                            <div>{datum.year}: {datum.count}</div>
                        </div>
                    {/snippet}
                </HTMLTooltip>
            {/snippet}
            </Plot>
        </div>
    {/await}

    <p>We start by looking at the number of papers by field of studies to know the bias in the database. We already know from the papers that computer science papers are heavily represented, by virtue of being more openly available, than, say, economics or information science. The question is more; how bad is it is.</p>
</div>

<style>
  .dashboard {
    padding: 2rem;
    max-width: 800px;
    margin: 0 auto;
  }

  .dashboard p {
    font-size: 1.1rem;
    font-family: sans-serif;
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
  
  .chart-container {
    width: 100%;
    padding: 1rem 0;
  }
</style>