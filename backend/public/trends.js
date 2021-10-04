const Trends = {
    props: {},
    data() {
        return {
            week_trends:[],
            weekly_term_max_size:null,
            selected_day:null,
            days:[],
            trends_by_day:{},
        }
    },
    mounted(){
        axios.get('/trends').then(response => {
            let trends_data = response.data;
            this.week_trends = trends_data.week;
            this.weekly_term_max_size =  Math.max(...this.week_trends.map(item => item[1]));

            this.trends_by_day = trends_data.days;
            this.days = Object.keys(this.trends_by_day).sort();
            this.selected_day = this.days[this.days.length-1];
        });

        let myCarousel = document.getElementById('day-trends-carousel')
        let self = this;
        myCarousel.addEventListener('slide.bs.carousel', function (event) {
            self.selected_day = self.days[event.to];
        })
    },
    methods: {
        term_clicked(term){
            this.emitter.emit('term-selected', term)
        },
        display_date(date){
            return moment(date).format('dddd Do MMMM');
        }
    },
    computed:{
        // filtered_terms(){
        //     let terms_filtered = this.terms;
        //     if(this.search_text && this.search_text !==''){
        //         terms_filtered = terms_filtered.filter(term_obj => term_obj.term.includes(this.search_text))
        //     }
        //     return terms_filtered
        // }
    },
    template:`
<div>
    <div class="row pb-5">
    
        <h5 class="text-center">מונחים תדירים מהשבוע האחרון:</h5>
      
        <div class="row gx-2 align-items-center" v-for="([term, term_size],index) in week_trends"> 
            <div class="col-4">
                <span class="badge p-0 my-1 text-dark bg-white bg-gradient">
                    <button type="button" @click="term_clicked(term)" class="btn btn-outline-dark">{{term}}</button>
                </span>
            </div>  
            <div class="col-7 align-middle text-center">
                <div class="progress ml-0 disable-progress-background" style="height: 15px;">
                    <div class="progress-bar" role="progressbar" :style="{width: (100*term_size/weekly_term_max_size)+'%'}" 
                        :aria-valuenow="term_size" aria-valuemin="0" :aria-valuemax="weekly_term_max_size">{{term_size}} אזכורים</div>
                </div>
            </div>
        </div>
        
    </div>

    

    <div class="row">
<div id="day-trends-carousel" class="carousel carousel-dark slide" data-bs-ride="carousel">
  
  
        <div class="carousel-indicators">
    <button v-for="(day, index) in days" type="button" data-bs-target="#day-trends-carousel" :data-bs-slide-to="index" 
        :class="{active:index==days.length-1}" aria-current="true" :aria-label="display_date(day)"></button>
  </div>

  
  <div class="carousel-inner mb-3 pb-5 px-5">
    <div v-for="(day, index) in days" class="carousel-item" :class="{active:index==days.length-1}">
      <div class="text-center">
      <h5>מונחים בולטים מיום - <b>{{display_date(day)}}</b></h5>
      <span v-for="term in trends_by_day[day]" class="badge p-0 m-1 text-dark bg-white bg-gradient">
                <button type="button" @click="term_clicked(term)" class="btn btn-outline-dark">{{term}}</button>
    </span>
      </div>
    </div>

  </div>
  
  <button class="carousel-control-prev" type="button" data-bs-target="#day-trends-carousel" data-bs-slide="prev">
    <span class="carousel-control-prev-icon" aria-hidden="true"></span>
    <span class="visually-hidden">Previous</span>
  </button>
  <button class="carousel-control-next" type="button" data-bs-target="#day-trends-carousel" data-bs-slide="next">
    <span class="carousel-control-next-icon" aria-hidden="true"></span>
    <span class="visually-hidden">Next</span>
  </button>
</div>
    </div>
    
    
    
</div>
    `

};
