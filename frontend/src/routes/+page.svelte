<!-- +page.svelte -->
<script>
    import { getVenues, getAllPapers, getFieldsSocSci, getFieldsStem, getAllFieldsAgg } from './data.remote.js';
    import { Plot, BarY, HTMLTooltip } from 'svelteplot';
    import Slider from '$lib/components/Slider.svelte'
    import Select from '$lib/components/Select.svelte'
    import Toggle from '$lib/components/Toggle.svelte'
	import Streamgraph from '$lib/components/Streamgraph.svelte';
	import FosBarChart from '$lib/components/FosBarChart.svelte';

    let selectedVenue = $state('Nature');
    let minYear = $state(1970);
    let isNormalized = $state(false);
</script>

<div class="dashboard">
    
    <h1>A whirldwind tour of <a href="https://github.com/jstonge/scisciDB">SciSciDB</a> (WIP)</h1>
    
    <p>We introduce useful snapshots of databases are hosted at the University of Vermont, namely <a href="https://api.semanticscholar.org/api-docs/datasets">semantic scholar</a>, ... (more to come). Here we provide information specific to projects at the <a href="https://github.com/Vermont-Complex-Systems/">Vermont Complex Systems Institute</a>.</p>

    <p style="color: red;" >[!TODO: Add TOC in the right margin when on desktop, but collapsible from the top on mobile]</p>

    <h2>The <a href="https://api.semanticscholar.org/api-docs/datasets">Semantic Scholar</a> snapshot</h2>

    <p>The Semantic Scholar database provides metadata for over 200M texts, fully parsed text for over 16M papers, their embedding using AllenAI's <a href="https://huggingface.co/allenai/specter2">Specter2</a> embeddings, and the 2.4B citation graph that goes with all the papers. They also provide a collection of open-source methods tools on top of the data, such as their custom <a href="https://github.com/allenai/s2_fos">field of study</a>  classifier, a spaCy pipeline for medical documents (<a href="https://github.com/allenai/scispacy">scispacy</a>), and many more.</p>

    <h3>Examining field of studies (fos)</h3>

    <p>We already know from the papers that computer science and medicine papers are heavily represented in the semantic scholar database, by virtue of being more openly available, than, say, economics or information science. The question is really: "how bad is it is". For the following plots, we use a 10M samples by fos for convenience.</p>

    <p>Here is the macro perspective, looking at the counts of papers by fos:</p>

    {#await getAllFieldsAgg()}
        <p>Loading...</p>
    {:then data}    
        <div class="chart-container">
            <FosBarChart {data}/>
        </div>
    {/await}


    <p>With streamgraph, it is always the same story; we have more field of studies than humans are able to distinguish colors. An easy workaground will be to categorize our field of studies between STEM++ (like Physics and Chemistry, but also including environmental science and even medicine and computer science) and the Social Sciences++ (including humanities, law, and the arts). We now use a streamgraph to know the decomposition of fields of studies over time of STEM++:</p>
    
    <div class="toggle-container">
        <Toggle bind:isTrue={isNormalized}/>
    </div>

    {#await getFieldsStem()}
        <p>Loading...</p>
    {:then data}    
        <Streamgraph {data} {isNormalized}/>
    {/await}
    
    <p>When normalized, we note that medicine takes up much of the shares, which make sense as pubmed is a big open source datasets integrated in the database. Interestingly, we can see the extra space medicine takes around 2020, which is probably all the biomedical research that has been happening around COVID-19. We can see the rise of computer science. And now we do the same for the social sciences and humanities:</p>

    {#await getFieldsSocSci()}
        <p>Loading...</p>
    {:then data}    
        <Streamgraph {data} {isNormalized}/>
    {/await}

    <p>Here we will take the data with a grain of salt, as it could be something with how we wrangled the data (we are taking the first field of study in a list of entries) or perhaps something with the semantic scholar classifier, but what is up with Psychology after 2020?! Sociology grew almost to a 25% of papers in that categorization. The Art was also fairly constant, until COVID-19 hit. But again, I would take all that with a big grain of salt. The important bit here is to have a broad overview of what field of studies are biasing the semantic scholar dataset, nothing less, nothing more.</p>

    <h3>Time series venues</h3>
    
    <p>For given project, we wanted to know about the evolution of data sharing practices. We decided to sample the data by venue, as journal policies with respect to methods matter. Here we look at a time series by "top" venues, here simply defined by the venues' h5-index found on Google Scholar (we also use Google Scholar's subcategories of journals to classify papers).  We use bullet bars to indicate how many of available papers have been parsed out of all available papers in that venue.</p>
    
    <p style="color: red;" >[!TODO: add aggregated bar chart by subcategories of venues (see google scholar for the subcategories).]</p>

    <p>You can explore the coverage of any specific venue below:</p>

    <!-- Controls -->
    <div class="controls">
        <label>
        Venue:
        {#await getVenues()}
            <select disabled>
            <option>Loading venues...</option>
            </select>
        {:then venues}
            <Select bind:value={selectedVenue} options={venues}/>
        {:catch error}
            <select disabled>
            <option>Error loading venues</option>
            </select>
        {/await}
        </label>
        
        <label>
        From Year: {minYear}
        <Slider bind:value={minYear}/>
        </label>
    </div>
    
    {#await getAllPapers()}
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
                data={data.filter((d) => d.venue == selectedVenue && d.year >= minYear)}
                x="year"
                y="count"
                fillOpacity=0.1
                stroke="black"
            />
            {#snippet overlay()}
                <HTMLTooltip
                    data={data.filter((d) => d.venue == selectedVenue && d.year >= minYear)}
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

    <p style="color: red;" >[!TODO: add bullet bars to show the extent to which available papers are parsed or not.]</p>

    <p>We start by looking at the number of papers by field of studies to know the bias in the database. We already know from the papers that computer science papers are heavily represented, by virtue of being more openly available, than, say, economics or information science. The question is more; how bad is it is.</p>
</div>

<style>
    
  .dashboard {
    border: 2px solid black; /* Sets a 2px solid black border */
    padding: 2rem;
    background-color: #f5f5f5;
    max-width: 800px;
    margin: 0 auto;
  }
  :global(html) {
    background-color: #ccc;
  }

  .dashboard p {
    line-height: 1.3rem;
    font-size: 1.1rem;
    font-family: sans-serif;
  }
  
  .toggle-container {
    margin-top: 1rem;
    margin-bottom: 1rem;
    max-width: fit-content;
    margin-inline: auto;
  }

  .controls {
    display: flex;
    gap: 2rem;
    align-items: center;
    background: #ccc;
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