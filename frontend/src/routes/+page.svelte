<!-- +page.svelte -->
<script>
    import { base } from "$app/paths";
    
    import { getVenues, getAllPapers, getFieldsSocSci, getFieldsStem, getAllFieldsAgg } from './data.remote.js';
    import { Plot, BarY, HTMLTooltip } from 'svelteplot';
    import Slider from '$lib/components/Slider.svelte'
    import Select from '$lib/components/Select.svelte'
	import Streamgraph from '$lib/components/Streamgraph.svelte';
	import FosBarChart from '$lib/components/FosBarChart.svelte';
    import InsightBox from '$lib/components/InsightBox.svelte';

    let selectedVenue = $state('Nature');
    let selectedOffset = $state('wiggle');
    let minYear = $state(1970);
    let clicked = $state();

</script>

<div class="dashboard">
    <div class="header">
    <h1>Publications Dashboard</h1>
        <a href="https://github.com/jstonge/scisciDB" class="github-link" target="_blank" rel="noopener">
        <svg class="github-icon" viewBox="0 0 24 24" width="24" height="24">
            <path fill="currentColor" d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
        </svg>
        </a>
    </div>
    
    <h1>A whirldwind tour of <a href="https://github.com/jstonge/scisciDB">SciSciDB</a> (WIP)</h1>
    
    <p>We introduce useful snapshots of databases that are hosted at the University of Vermont, namely <a href="https://api.semanticscholar.org/api-docs/datasets">Semantic Scholar</a>, ... (more to come, <a href="https://docs.openalex.org/download-all-data/openalex-snapshot">OpenAlex</a> is next). Here we provide visualizations that we found missing from current APIs and have been helpful to a number of projects at the <a href="https://github.com/Vermont-Complex-Systems/">Vermont Complex Systems Institute</a>.</p>

    <InsightBox type="warning">
        <strong>TODO:</strong> Add TOC in the right margin when on desktop, but collapsible from the top on mobile
    </InsightBox>
    
    <h3>Introduction</h3>

    <p>The <a href="https://api.semanticscholar.org/api-docs/datasets">Semantic Scholar snapshot</a> provides metadata for over 200M texts from other aggregators such as PubMed, HAL, or the arXiv but also publishing partners such as ACM and the ACL (see <a href="https://www.semanticscholar.org/about/publishers">full list</a>). Although the raw number is impressive, Semantic Scholar distinguishes itself by open-sourcing a number of their natural language processing tools.</p>

    <div class="content-wrapper">
        <div class="text-content">
            <p>As part of their snapshot, they provide 16M parsed texts, refered to sa the <a href="github.com/allenai/s2orc">s2orc</a> collection, facilitating the creation of downstream applications such as <a href="https://www.connectedpapers.com/">Connected Papers</a>. Their original parsing scheme built on top of Grobid was made available on <a href="https://github.com/allenai/s2orc-doc2json">GitHub</a>. From that parsing, they extract a 2.4B citation graph that connects and contextualizes all that information.</p>
            <p>They provide useful representations of the texts as well, such as the <a href="https://huggingface.co/allenai/specter2">Specter2</a> embeddings for downstream tasks such as classification or topic modeling using density-based clustering. What I like about the Specter2 embedding is that it takes into account not only semantic similarity between texts, but also the relationships between texts. That is, two texts can be similar, but live in different reference spaces, which is a key feature of scientific work.</p> 
            <p>They also provide other tools on top of the data, such as their custom <a href="https://github.com/allenai/s2_fos">field of study</a> classifier, a spaCy pipeline for medical documents (<a href="https://github.com/allenai/scispacy">scispacy</a>), a recent toolkit for converting PDFs into clean and readable plain text (<a href="https://github.com/allenai/olmocr">OLMOCR</a>), and many more.</p>
        </div>
        <figure class="image-container">
            <img src='{base}/paper_layers.jpg' alt="some alt text" width="300"/>
            <figcaption><a href="https://github.com/allenai/papermage">PaperMage</a> view of the different layers in a paper.</figcaption>
        </figure>
    </div>

    <p>Practically, this means that the Semantic Scholar dataset provides researchers direct access to popular aggregators (arXiv, pubmed) and many more, some of which already having content parsed down to the paragraph level. This is tremendously helpful. If researchers want to expand their analysis beyond already parsed text, they can use AllenAI's open-source toolkits to do so. </p>

    <h3>Examining fields of study (FOS)</h3>

    <p>We already know from the papers that computer science and medicine papers are heavily represented in the Semantic Scholar database, by virtue of being more openly available than, say, economics or information science. The question is really: "how bad is it?" For the following plots, we use a 10M sample by FOS for convenience. Note that out of the 228M papers, around 148M papers have at least one associated field of study.</p>

    <p>Here is the macro perspective, looking at the counts of papers by FOS:</p>

    {#await getAllFieldsAgg()}
        <p>Loading...</p>
    {:then data}    
        <div class="chart-container">
            <FosBarChart {data}/>
        </div>
    {/await}

    <p>We next show the evolution of fields of study using a streamgraph. One issue is that we have more fields of study than humans are able to distinguish colors for. An easy workaround is to categorize our fields of study between STEM++ (like Physics and Chemistry, but also including environmental science and even medicine and computer science) and the Social Sciences++ (including humanities, law, and the arts). We now use a streamgraph to show the decomposition of fields of study over time for STEM++:</p>
    

    {#await getFieldsStem()}
        <p>Loading...</p>
    {:then data}  
        <div class="chart-container">
            <Streamgraph {data} offset={selectedOffset} {clicked}/>
        </div>
    {/await}

    <div class="select-container">
        <Select bind:value={selectedOffset} options={['wiggle', 'normalize', 'none']}/>
    </div>
    
    <p>When unnormalized, we can see the explosion of papers in different FOS, a trend that is acellerating in the 2000s. Note that we are currently using the <b>2025-08-19</b> release, which should include data up to very recently. We are still unclear whether the number of papers drastically shrink after 2020 or it is simply an artifact from the data pipeline. One hypothesis is that the Microsoft Academic Graph has been deprecated at the end of 2021, which was Microsoft undetaking of crawling scientific data at large. Maybe Semantic Scholar is somewhat less aggressive in their crawling, which would be aligned with their mission of providing high-quality data over quantity.</p>
    <p>When normalized, we note that medicine takes up much of the shares, which make sense as pubmed is a big open source datasets integrated in the database. Interestingly, we can see the extra space medicine takes around 2020, which is probably all the biomedical research that has been happening around COVID-19. We can see the rise of computer science.</p>

    <InsightBox type="tip">
        <p><strong>Tip:</strong> The streamgraph visualization requires a bit of practice to get right. Here we are using <em>inside-out</em> ordering, meaning the layers are arranged as to minimize the overall "wiggle" or movement of the baseline. When offset is set to null (also called silhouette mode), then all streams are stacked from a zero baseline upward. Click on a stream to make it more opaque, facilitating interpretation of the quantities.</p>
    </InsightBox>

    <p>We now move to the social sciences and humanities:</p>

    {#await getFieldsSocSci()}
        <p>Loading...</p>
    {:then data}   
        <div class="chart-container">
            <Streamgraph {data} offset={selectedOffset}/>
        </div>
    {/await}

    <div class="select-container">
        <Select bind:value={selectedOffset} options={['wiggle', 'normalize', 'none']}/>
    </div>

    <p>Here we will take the data with a grain of salt, as it could be something with how we wrangled the data (we are taking the first field of study in a list of entries) or perhaps something with the Semantic Scholar classifier, but what is up with Psychology after 2020?! Sociology grew to almost 25% of papers in that categorization. The Arts were also fairly constant, until COVID-19 hit. But again, I would take all that with a big grain of salt. The important bit here is to have a broad overview of what fields of study are biasing the Semantic Scholar dataset, nothing less, nothing more.</p>

    <p>One last thing to note is that by looking at the relative number of papers, we can see that STEM++ has around 3 times more papers than the Social Sciences++ category. It is not nothing, but any kind of analysis making claims about the whole of science based on the Semantic Scholar dataset should control for that fact. And this is also for papers with available FOS, which means the papers at least have an abstract. We might expect that STEM++ is even more represented when analyzing the S2ORC data.</p>

    <h3>Time series venues (Very WIP)</h3>

    <p>For a given project, we wanted to know about the evolution of data sharing practices. We decided to sample the data by venue, as journal policies with respect to methods matter. Here we look at a time series by "top" venues, here simply defined by the venues' h5-index found on Google Scholar (we also use Google Scholar's subcategories of journals to classify papers). We use bullet charts to indicate how many available papers have been parsed out of all available papers in that venue.</p>

    <InsightBox type="warning">
        <strong>TODO:</strong> Add aggregated bar chart by subcategories of venues (see google scholar for the subcategories).
    </InsightBox>
    

    <p>You can explore the coverage of any specific venue below:</p>
    
    {#await getAllPapers()}
        <p>Loading...</p>
    {:then data}    
        <div class="chart-container">
            <Plot 
                x={{tickRotate: 40, label: ""}}
                y={{grid: true}}
                height={300}
                marginRight={20}
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

    <p>(We are still unconvinced about the usefulness of looking at the data venue by venue. We might facet by category, putting all barcharts within that category in a grid.)</p>
    
    <InsightBox type="warning">
        <strong>TODO:</strong> Add bullet bars to show the extent to which available papers are parsed or not.
    </InsightBox>

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
    line-height: 1.4rem;
    font-size: 1.1rem;
    font-family: sans-serif;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
  }
  
  .header h1 {
    margin: 0;
  }

  .github-link {
    color: #666;
    text-decoration: none;
    transition: color 0.2s ease;
  }
  
  .github-link:hover {
    color: #000;
  }
  
  .github-icon {
    width: 28px;
    height: 28px;
  }

  .select-container {
    margin-top: 1rem;
    margin-bottom: 1rem;
    max-width: fit-content;
    margin-inline: auto;
  }

  .controls {
    display: flex;
    gap: 2rem;
    align-items: center;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
    flex-wrap: wrap;
    max-width: fit-content;
    margin-inline: auto;
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
    border-radius: 15px; 
    padding: 0.5rem 0.5rem 0.5rem 0.5rem;
    background-color: #e5e2e2;
  }

  .content-wrapper {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    gap: 20px;
}

.text-content {
    flex: 1 1 300px;
    min-width: 0;
}

.image-container { 
    flex: 0 0 auto;
    max-width: fit-content;
    border: 1px solid #ccc;
    padding: 20px;
    box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.2);
    margin: 0;
    margin-top: 3rem;
}


.image-container figcaption {
    margin-top: 10px;
    font-size: 14px;
    color: #666;
    text-align: center;
    font-style: italic;
}

      /* Center image when it wraps on smaller screens */
    @media (max-width: 640px) {
        .image-container {
            align-self: center; /* This centers the image container */
            order: 2; /* Move image below text */
            margin-top: 0;
            margin-bottom: 1rem;
        }
        
        .text-content {
            order: 1;
        }
    }
</style>