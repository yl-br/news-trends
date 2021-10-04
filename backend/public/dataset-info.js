const DatasetInfo = {
    data() {
        return {
            articles_count:null,
            number_of_days:null,
            max_article_date:null,
            is_show_chart:false
        }
    },
    created(){
        this.chart = null;
        this.dataset_info = null;
    },
    mounted(){
        axios.get('/dataset-info').then(response=>{
            this.dataset_info = response.data;
            this.articles_count = this.dataset_info.length

            let dates = this.dataset_info.map(item=>Date.parse(item.timestamp))

            this.number_of_days = Math.round(moment.duration(moment().startOf('day') - moment(Math.min(...dates))).asDays());
            this.max_article_date = moment(Math.max(...dates)).local().format("YYYY-MM-DD HH:mm:ss")
        });

    },
    methods: {
        toggle_chart(){
            if(!this.chart){
                this.create_graph(this.dataset_info);
            }
            this.is_show_chart = !this.is_show_chart;
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
                all_data_agg.push({x:date,y:all_count})

                sources.forEach(source=>{
                    let count = items.filter(item=> item.source === source).length;
                    source_to_data[source].push({x:date, y:count})
                });
            });
            return {source_to_data:source_to_data, total:all_data_agg, days:days, sources: sources};
        },
        create_graph(dataset_info){
            let canvas = this.$refs.container
            let context = canvas.getContext('2d');

            let {source_to_data, total, days,  sources} = this.aggregate_by_source_and_day(dataset_info);
            let datasets = []
            sources.sort().forEach((source, index)=>{
                datasets.push({
                    'data':source_to_data[source],
                    'label': sources_map[source].display_value,
                    lineTension: 0,
                    // 'fill':false,
                    backgroundColor: sources_colors[index],
                    borderColor: sources_border_colors[index],
                    borderWidth: 1,
                })
            });

            // datasets.push({'data':total,'label':'Total','fill':false, type:'line',
            //     backgroundColor: chartColors.blue,
            //     borderColor: chartColors.black,
            //     borderWidth: 3,});

            this.chart = new Chart(context, {
                type: 'line',
                data: {
                    labels:days,
                    datasets: datasets
                },
                options:
                    {
                        responsive:true,
                        legend:{
                            position:'left',
                            rtl:true
                        },
                         scales: {
                        //     xAxes: [{
                        //         type: 'time',
                        //         distribution: 'series',
                        //         time: {
                        //             unit: 'month'
                        //         }
                        //     }],
                            yAxes:[{
                                stacked:true
                            }]
                        }
                    }
            });
        },
        display_date(date){
            return moment(date).local().format('LLL');
        },
        date_from_now(date){
            return moment(date).fromNow();
        }
    },
    template:`
    <div class="mx-3 my-3">
        <p class="my-3">
            מאגר הנתונים מכיל כ- <b>{{articles_count}}</b>  כתבות שנאספו ב- <b>{{number_of_days}}</b> ימים האחרונים.
            <br>
            סריקה אחרונה התבצעה <b>{{date_from_now(max_article_date)}}</b> 
            ({{display_date(max_article_date)}}).
        </p>
        <p class="lead mb-0"><a class="text-white fw-bold" @click="toggle_chart()" href="javascript:void(0);">לכמות כתבות לפי מקור...</a></p>
        <div v-show="is_show_chart" style="height: 300px;width: 90%" class="bg-light bg-gradient">
            <canvas ref="container" height="300" width="90%"></canvas>
        </div>
    </div>
    `
};
