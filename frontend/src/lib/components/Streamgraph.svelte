<script>
    import { Plot, AreaY} from 'svelteplot';

    let {  data, isNormalized = $bindable()} = $props();
</script>

<Plot x={{ grid:true}} y={{ axis: false }} marginLeft={50}>
        <AreaY
            {data}
            x="year"
            y="count" 
            z="field"
            fill="field" 
            stack={{ 
                order: 'inside-out',
                offset: isNormalized ? 'normalize' : 'wiggle'
            }}
            />
    </Plot>