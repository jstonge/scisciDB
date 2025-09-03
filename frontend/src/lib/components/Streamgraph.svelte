<script>
    import { Plot, AreaY, RuleY, Text } from 'svelteplot';
    let {  data, offset = $bindable(), clicked = $bindable()} = $props();
</script>

<Plot 
    x={{ grid: offset === 'normalize' ? false : true}} 
    y={{ 
        axis: offset === 'none' ? 'left' : false, 
        grid: offset === 'none' ? true : false 
        }} 
    marginLeft={offset === 'none' ? 40 : 15}
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
            stack={{ 
                order: 'inside-out',
                offset: offset
            }}
            cursor="pointer"
            opacity={{
                scale: null,
                value: (d) =>
                        !clicked || clicked === d.field ? 0.8 : 0.3
            }}
            onclick={(event, d) => {
                clicked = clicked === d.field ? null : d.field; // or d.data.field, depending on structure
            }} 
        />
        <RuleY
            data={offset === 'normalize' ? [0.25, 0.5, 0.75] : []}
            strokeDasharray="4,4"
            opacity={0.9} 
        />
        {#each [0.25, 0.5, 0.75] as v}
            <Text
                frameAnchor="left"
                dy={-5}
                y={v}
                text={offset === 'normalize' ? `${v*100}%` : ""}
                fontSize={13} 
            />
        {/each}
        <RuleY
        data={offset === 'normalize' ? [0.125, 0.375, 0.625, 0.875] : []}
        strokeDasharray="2,2"
        opacity={0.3} 
        />
    </Plot>