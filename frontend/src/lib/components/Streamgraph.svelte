<script>
    import { Plot, AreaY, RuleY, Text } from 'svelteplot';
    let {  data, isNormalized = $bindable()} = $props();
    const text_labels = [{"y":0.25}, {"y":0.5}, {"y":0.75}];
</script>

<Plot 
    x={{ grid: isNormalized ? false : true}} 
    y={{ axis: false }} 
    marginLeft={15}
    marginRight={15} 
    color={{legend: true, scheme: "paired"}}
    >
        <AreaY
            {data}
            x="year"
            y="count" 
            z="field"
            fill="field" 
            stroke="white"
            strokeOpacity=0.1
            fillOpacity=0.8
            stack={{ 
                order: 'inside-out',
                offset: isNormalized ? 'normalize' : 'wiggle'
            }}
        />
        <RuleY
            data={isNormalized ? [0.25, 0.5, 0.75] : []}
            strokeDasharray="4,4"
            opacity={0.9} 
        />
        {#each [0.25, 0.5, 0.75] as v}
            <Text
                frameAnchor="left"
                dy={-5}
                y={v}
                text={isNormalized ? `${v*100}%` : ""}
                fontSize={13} 
            />
        {/each}
        <RuleY
        data={isNormalized ? [0.125, 0.375, 0.625, 0.875] : []}
        strokeDasharray="2,2"
        opacity={0.3} 
        />
    </Plot>