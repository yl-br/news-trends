const Network = {
    props: [],
    data() {
        return {
        }
    },
    created(){
        this.nodes = null;
        this.edges = null;
        this.network = null;
    },
    mounted(){
        this.emitter.on('term-selected', selected_term =>{
            this.run_focus_animation(selected_term);
        });

        axios.get('/network').then(response => {
            let network_data = response.data;
            this.nodes = network_data.nodes;
            this.edges = network_data.edges;
            this.create_graph()
        });

    },
    methods: {
        run_focus_animation(term){
            let node_id = this.nodes.map(n=>n.label).indexOf(term)
            // this.network.fit({animation:{duration: 500}, maxZoomLevel:0.5})
            // setTimeout(()=>{
            // this.network.selectNodes([node_id], true)
            this.network.selectNodes([node_id], true);
            this.network.focus(node_id, {locked:true, scale:0.4,animation:{ duration: 500}})
            // },520)
            // setTimeout(()=>{

            // },600)

        },
        handle_click(event) {
            if (event.nodes && event.nodes.length > 0) {
                let node_id = event.nodes[0]
                let term = this.nodes[node_id].label
                this.emitter.emit('term-selected', term)
            }
            // else if (event.edges && event.edges.length > 0) {
            //     let edge_id = event.edges[0];
            //     let nodeA_id = this.edges[edge_id].from;
            //     let nodeB_id = this.edges[edge_id].to;
            //     let termA = this.nodes[nodeA_id].label;
            //     let termB = this.nodes[nodeB_id].label;
            //
            //     this.emitter.emit('connection-selected', {termA:termA, termB:termB})
            // }

        },
        handle_edge_selection(event){
            // console.log(event);
        },
        handle_node_selection(event){
            // console.log(event);
        },
        create_graph(){
            let max_node_size = Math.max(...this.nodes.map(n=>n.size))
            let min_font = 20,max_font = 4*min_font;

            let scale_font = (size) => Math.max(min_font, (size/max_node_size)*max_font);
            this.nodes.forEach(item=>{
                item.value = item.size;
                // item.font = {size:scale_font(item.size)};
            });


            let max_width_size = Math.max(...this.edges.map(e=>e.width))
            let min_width = 1, max_width =10;
            let scale_width = (size) => Math.max(min_width, (size/max_width_size)*max_width);
            this.edges.forEach(item=>{
                // item.width = scale_width(item.width, max_width_size);
                item.value =  item.width;
            });

            let nodes = new vis.DataSet(this.nodes);
            let edges = new vis.DataSet(this.edges);
            let container = this.$refs.container;

            let data = {
                nodes: nodes,
                edges: edges
            };
            let options = {
                width:'1200px', height:'800px', // window.innerWidth
                interaction: {
                    // zoomView: false
                    hover:true,
                    // dragView:false
                },
                edges: {
                    color: {
                        opacity: 0.6
                    },
                    smooth: false
                    // {
                    //     type:"continuous",
                    //     roundness:0.3
                    // }
                },
                nodes: {
                    shape: "box",
                    chosen:{
                        label: function (values, id, selected, hovering) {
                            values.color =  'rgb(255,255,255)';
                            values.strokeWidth = 0.5;
                        }
                    },
                    color:{
                        border: 'rgb(0,0,0)',
                        background: 'rgb(255,255,255)',
                        highlight: {
                            border: 'rgb(0,0,0)',
                            background:  'rgb(0,0,0)'
                        },
                        hover: {
                            border: 'rgb(0,0,0)',
                            background:  'rgb(0,0,0)'
                        }
                    },
                    font:{
                        strokeWidth:0.3,
                        strokeColor:'rgb(0,0,0)',
                    },
                    scaling:{
                        min: 20,
                        max: 120,
                        label: {
                            enabled: true,
                            min: 20,
                            max: 80,
                            maxVisible: 40,
                            drawThreshold: 4
                        }
                    }
                },
                layout: {
                    improvedLayout: false
                },
                physics:{
                    enabled:true,
                    stabilization: {
                        enabled: true,
                        iterations: 400    // YMMV
                    },
                    // maxVelocity:100,
                    minVelocity: 30,
                    timestep: 0.2,
                    // // adaptiveTimestep:true,
                    solver:"forceAtlas2Based",
                    //
                    // barnesHut: {
                    //     theta: 0.5,
                    //     gravitationalConstant: -200,
                    //     centralGravity: 0.3,
                    //     springLength: 600,
                    //     springConstant: 0.02,
                    //     damping: 0.09,
                    //     avoidOverlap: 0.9
                    // },
                    forceAtlas2Based: {
                        "gravitationalConstant": -1000,
                        "centralGravity": 0.01,
                        "springLength": 200,
                        "springConstant": 0.02,
                        "damping": 0.4,
                        "avoidOverlap": 1
                    }
                },
                // configure:{
                //     container:this.$refs.configure_container
                //     }
            };

            this.network = new vis.Network(container, data, options);
            this.network.on("click", this.handle_click)
            this.network.on("selectEdge",this.handle_edge_selection)
            this.network.on("selectNode", this.handle_node_selection)

            // setTimeout(()=>{
            // this.network.stabilize({iterations: 1000});
            // }, 500)

        }
    },
    template: `
    <div ref="container" id="network-container" class="row justify-content-center"></div>
    `
};