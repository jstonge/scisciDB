<script>
    import { Plot, BarY} from 'svelteplot';
    let { data } = $props();
</script>

<Plot 
    x={{tickRotate: 40, label: ""}}
    y={{grid: true, label: "↑ # Available papers"}}
    height={300}
    marginRight={40}
    >
    <BarY 
        {data}
        x="field"
        y="total_count"
        fillOpacity=0.6
        stroke="black"
    />
</Plot>