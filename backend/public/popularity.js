const Popularity = {
    data() {
        return {
            single_term: null,
            connection_terms:null
        }
    },
    created(){
        this.chart = null;
    },
    mounted(){
        let canvas = this.$refs.container
        let context = canvas.getContext('2d');
        let self = this;

        this.chart = new Chart(context, {
            type: 'bar',
            data: {
                labels: [],
                datasets: []
            },
            options:
                {
                    responsive:true,
                    legend:{
                        position:'left',
                        rtl:true
                    },
                    tooltips:{
                        rtl:true,
                        callbacks:{
                            footer: function(tooltipItem, data) {
                                if (self.connection_terms || tooltipItem[0].datasetIndex != 0)// If its not tooltip for Total dataset.
                                {
                                    return;
                                }
                                return data.datasets[tooltipItem[0].datasetIndex].data[tooltipItem[0].index].titles.slice(0,3).map(title=> '• ' + title);
                            }
                        }
                    }
                }
        });

        this.emitter.on('term-selected', selected_term =>{
            this.connection_terms =null;
            this.single_term = selected_term;
            this.load_term(selected_term);
        });
        this.emitter.on('connection-selected', event =>{
            this.single_term = null;
            this.connection_terms = {termA:event.termA, termB:event.termB}
            this.load_connection(event.termA, event.termB);
        });
    },
    methods: {
        load_term(term){
            axios.get(`/terms/popularity/${term}`).then(response => {
                let data = response.data;
                this.chart.data = this.create_single_term_chart_data(term, data);
                this.chart.update();
            });
        },
        load_connection(termA, termB){
            axios.get(`/terms/popularity/${termA}`).then(response => {
                let termA_data = response.data;
                axios.get(`/terms/popularity/${termB}`).then(response => {
                    let termB_data = response.data;
                    this.chart.data = this.create_connection_chart_data(termA, termB, termA_data, termB_data)
                    this.chart.update();
                });
            });
        },
        aggregate_by_day(data){
          let out_agg_data=[];
            let dates = data.map(item=>Date.parse(item.timestamp))
            let min_date = moment(Math.min(...dates)).endOf('day')
            let max_date = moment(Math.max(...dates)).endOf('day')

            let days = [];
            let diff = max_date.diff(min_date, 'days')
            for(let i=0; i <= diff; i++){
                days.push(moment(min_date).add(i, 'days').format('L'))
            }
            let days_map =days.reduce((accumulate_object, key) => ({ ...accumulate_object, [key]: []}), {})
            data.forEach((item)=>{
                let day = moment(item.timestamp).format('L')
                days_map[day].push(item);
            });
            days.forEach(day=>{
                let items = days_map[day];
                let all_count = items.length;
                let date = moment(day,'L');
                out_agg_data.push({x:date,y:all_count})
            });
            return {agg_data:out_agg_data,days: days};
        },
        aggregate_by_source_and_day(data){
            let dates = data.map(item=>Date.parse(item.timestamp))
            let min_date = moment(Math.min(...dates)).endOf('day')
            let max_date = moment(Math.max(...dates)).endOf('day')

            let days = []
            let diff = max_date.diff(min_date, 'days')
            for(let i=0; i <= diff; i++){
                days.push(moment(min_date).add(i, 'days').format('L'))
            }

            let days_map =days.reduce((accumulate_object, key) => ({ ...accumulate_object, [key]: []}), {})
            data.forEach((item)=>{
                let day = moment(item.timestamp).format('L')
                days_map[day].push(item);
            });

            let sources =[...new Set(data.map((item)=>item.source))];

            let source_to_data = sources.reduce((accumulate_object, key) => ({ ...accumulate_object, [key]: []}), {})
            let all_data_agg = [];

            // days = days.sort()
            days.forEach(day=>{
                let items = days_map[day];
                let all_count = items.length;
                let date = moment(day,'L');
                let all_titles = items.map(x=> x.title);
                all_data_agg.push({x:date,y:all_count, titles:all_titles})

                sources.forEach(source=>{
                    let count = items.filter(item=> item.source === source).length;
                    source_to_data[source].push({x:date, y:count})
                });
            });
            return {source_to_data:source_to_data, total:all_data_agg, days:days, sources: sources};
        },
        create_connection_chart_data(termA, termB, data_A,data_B){
            let {agg_data:agg_data_A,days:days_A} = this.aggregate_by_day(data_A);
            let {agg_data:agg_data_B,days:days_B} = this.aggregate_by_day(data_B);
            let datasets = [];
            datasets.push({
                'data':agg_data_A,
                'label':termA,
                'fill':false,
                type:'line',
                backgroundColor: '#0F79EB',
                borderColor: '#0F79EB',
                borderWidth: 1,
            });
            datasets.push({
                'data':agg_data_B,
                'label':termB,
                'fill':false,
                type:'line',
                backgroundColor: '#9966FF',
                borderColor: '#9966FF',
                borderWidth: 1,
            });
            let days_join = [...new Set(days_A.concat(days_B))].sort();
            let labels = days_join.map((day)=> moment(day,'L').format('dddd L'));
            return {datasets:datasets, labels:labels}
        },
        create_single_term_chart_data(term, data){
            let {source_to_data, total, days,  sources} = this.aggregate_by_source_and_day(data);

            let datasets = []

            sources.sort().forEach((source, index)=>{
                datasets.push({
                    'data':source_to_data[source],
                    'label': sources_map[source].display_value,
                    // 'fill':false,
                    backgroundColor: sources_map[source].color,
                    borderColor: chartColors.black, //sources_border_colors[index],
                    borderWidth: 1,
                })
            });

            datasets.sort((x1,x2)=> x1.label.localeCompare(x2.label));

            datasets.splice(0,0,{
                'data':total,
                label:'סה"כ',
                fill:false,
                type:'line',
                backgroundColor: chartColors.light_blue,
                borderColor: chartColors.black,
                borderWidth: 3,
                pointRadius: 8,
                pointHoverRadius: 15,
            });

            let labels = days.map((day)=> moment(day,'L').format('dddd L'));

            return {datasets:datasets, labels:labels}
        }
    },
    template:`
    <div>
        <h3 v-if="single_term"><u>כמות אזכורים:</u> <b>{{single_term}}</b></h3>
        <h3 v-else-if="connection_terms"><u>כמות אזכורים:</u> <b>{{connection_terms.termA}}</b>  {{'<----->'}}  <b>{{connection_terms.termB}}</b></h3>
        
        <div style="height:250px; width:90%">
            <canvas ref="container" height="250" width="100%"></canvas>
        </div>
    </div>
    `
};
let chartColors = {
    red: 'rgb(255, 99, 132)',
    orange: 'rgb(255, 159, 64)',
    yellow: 'rgb(255, 205, 86)',
    green: 'rgb(75, 192, 192)',
    blue: 'rgb(54, 162, 235)',
    purple: 'rgb(153, 102, 255)',
    grey: 'rgb(201, 203, 207)',
    light_blue: 'rgb(145,206,255)',
    dark_blue: 'rgb(15,55,160)',
    black: 'rgb(0,0,0)'
};

let sources_colors = [
    "rgba(255, 99, 132, 0.2)",
    "rgba(255, 159, 64, 0.2)",
    "rgba(255, 205, 86, 0.2)",
    "rgba(75, 192, 192, 0.2)",
    "rgba(54, 162, 235, 0.2)",
    "rgba(153, 102, 255, 0.2)",
    "rgba(201, 203, 207, 0.2)"
];
let sources_border_colors =[
    "rgb(255, 99, 132)",
    "rgb(255, 159, 64)",
    "rgb(255, 205, 86)",
    "rgb(75, 192, 192)",
    "rgb(54, 162, 235)",
    "rgb(153, 102, 255)",
    "rgb(201, 203, 207)"
];