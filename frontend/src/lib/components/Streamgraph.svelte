<script>
    import { Plot, AreaY, RuleY, Text } from 'svelteplot';
    let {  data, isNormalized = $bindable()} = $props();
    const text_labels = [{"y":0.25}, {"y":0.5}, {"y":0.75}];
</script>

<Plot x={{ grid:true}} y={{ axis: false }} marginLeft={50} marginRight={50} color={{legend: true}}>
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
                offset: isNormalized ? 'normalize' : 'wiggle'
            }}
        />
        <RuleY
            data={isNormalized ? [0.25, 0.5, 0.75] : []}
            strokeDasharray="4,4"
            opacity={0.9} 
        />
        <Text
            frameAnchor="right"
            dx={35}
            text={isNormalized ? "50%" : ""}
            fontSize={15} 
        />
    </Plot>