const ConnectedTerms = {
    props: [],
    data() {
        return {
            term:'מונח'
        }
    },
    created(){
        this.nodes = [];
        this.edges = [];
        this.network = null;
    },
    mounted(){

        this.create_graph();

        this.emitter.on('term-selected', selected_term => {
            if(selected_term === this.term){
                return;
            }

            this.term = selected_term;
            axios.get(`/connections/${selected_term}`).then(response => {
                let connected_terms = response.data;
                this.update_graph(selected_term, connected_terms);
            });
        });

    },
    methods: {
        handle_double_click(event){
            if (event.nodes && event.nodes.length > 0) {
                let node_id = event.nodes[0];
                let term = this.nodes[node_id].label;
                this.emitter.emit('term-selected', term);
            }
        },
        handle_edge_selection(event){
            // console.log(event);
        },
        handle_node_selection(event){
            // console.log(event);
            if (event.nodes && event.nodes.length > 0) {
                let node_id = event.nodes[0]
                let term = this.nodes[node_id].label
                if (term === this.term) {
                    this.emitter.emit('term-selected', term);
                }
                else{
                    this.emitter.emit('connection-selected', {termA: this.term, termB: term})
                }

            }
        },
        update_graph(selected_term, connected_terms){
            this.nodes = [{
                id:0,
                label:selected_term,
                font:{
                    size:50,
                    color:'rgb(255,255,255)'
                },
                fixed:true,
                color:{
                    background:  '#0F79EB',
                    highlight: {
                        border: 'rgb(0,0,0)',
                        background:  '#0F79EB'
                    }}}];
            this.edges = [];

            connected_terms_keys = Object.keys(connected_terms);
            connected_terms_keys.forEach((conn_term, i)=>{
                this.nodes.push({
                    id:i+1,
                    label:conn_term,
                    font:{size:30}
                });
                this.edges.push({from:0,to:i+1, width:4})
            });

            let new_nodes = new vis.DataSet(this.nodes);
            let new_edges =  new vis.DataSet(this.edges);
            this.network.setData({nodes:new_nodes,edges:new_edges});
            // this.network.fit(0, {locked:true});
        },
        create_graph(){
            let container = this.$refs.container;

            let data = {
                nodes: [],
                edges: []
            };
            let options = {
                width:'500px', height:'300px',
                interaction:{
                    dragNodes:true,
                    dragView: false,
                    zoomView:false,
                    hover:true
                },
                edges: {
                    length:250,
                    color: {
                        opacity: 0.6
                    },
                    smooth:false
                    //     {
                    //     type:"continuous",
                    //     roundness:0.5
                    // }
                },
                layout: {
                    improvedLayout: false
                },
                nodes:{
                    shape: "box",
                    chosen: {
                        label: function (values, id, selected, hovering) {
                            values.color = 'rgb(255,255,255)';
                            values.strokeWidth = 0.5;
                        }
                    },
                    color:{
                        border: 'rgb(0,0,0)',
                        background: 'rgb(255,255,255)',
                        highlight: {
                            border: 'rgb(0,0,0)',
                            background:  '#9966FF'
                        },
                        hover: {
                            border: 'rgb(0,0,0)',
                            background:  'rgb(0,0,0)'
                        }
                    },
                    font:{
                        strokeWidth:0.3,
                        strokeColor:'rgb(0,0,0)',
                        // background:'rgba(255,255,255,0.8)'
                    }
                },
                physics: {
                    enabled: true,
                    solver: "barnesHut",
                    barnesHut:{
                        springLength:200
                    }
                }
            };

            this.network = new vis.Network(container, data, options);
            // this.network.on("click", this.handle_click)
            this.network.on("doubleClick", this.handle_double_click)
            // this.network.on("selectEdge",this.handle_edge_selection)
            this.network.on("selectNode", this.handle_node_selection)
        }
    },
    template: `
    <div>
        <h3><u>השוואה:</u> <b>{{term}}</b> ומונחים קשורים </h3>
        <div ref="container" id="connected-terms-container"></div>
    </div>
    `
};