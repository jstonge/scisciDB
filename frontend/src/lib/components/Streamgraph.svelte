<script>
    import { Plot, AreaY } from 'svelteplot';
    let {  data, isNormalized = $bindable()} = $props();
</script>

<Plot x={{ grid:true}} y={{ axis: false }} marginLeft={50} color={{legend: true}}>
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
    </Plot>