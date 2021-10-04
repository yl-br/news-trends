const Headlines = {
    props: {},
    data() {
        return {
            headlines:[],
            sources_map:sources_map
        }
    },
    mounted(){
        axios.get('/headlines').then(response => {
            this.headlines = response.data
        });
    },
    methods: {
        display_date(timestamp){
            return moment(timestamp).fromNow()
        },
        term_clicked(term){
            this.emitter.emit('term-selected', term)
        }
    },
    computed:{
    },
    template:`
    <div>
    
       <div v-for="headline in headlines" class="my-4 p-2 bg-body rounded shadow-sm" >
        
        
        <div class="d-flex text-muted pt-1 border-bottom">
          <svg class="bd-placeholder-img flex-shrink-0 me-2 rounded" width="32" height="32" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Placeholder: 32x32" preserveAspectRatio="xMidYMid slice" focusable="false">
                      <image :href="sources_map[headline.articles[0].source].img_url" width="32" height="32"></image>
          </svg>
          
          <p class="pb-3 mb-0 small lh-sm">
            <a target="_blank" rel="noopener noreferrer" :href="headline.articles[0].url" class="headlines-title-link">
                <h5><strong class="d-block text-gray-dark">{{headline.articles[0].title}}</strong></h5>
            </a>
            {{sources_map[headline.articles[0].source].display_value}} - {{display_date(headline.articles[0].timestamp)}}
          </p>
        </div>
        
        
        <div v-for="article in headline.articles.slice(1,headline.expand ? 10:2)" class="d-flex text-muted pt-2 ps-5">
          <svg class="bd-placeholder-img flex-shrink-0 me-2 rounded" width="24" height="24" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Placeholder: 32x32" preserveAspectRatio="xMidYMid slice" focusable="false">          
            <image :href="sources_map[article.source].img_url" width="24" height="24"></image>
          </svg>
    
          <p class="pb-3 mb-0 small lh-sm border-bottom">
            <a target="_blank" rel="noopener noreferrer" :href="article.url" class="headlines-title-link">
                <strong class="d-block text-gray-dark">{{article.title}}</strong>
            </a>
            {{sources_map[article.source].display_value}} - {{display_date(article.timestamp)}}
          </p>
        </div>
                <span v-for="term in headline.common_terms" class="badge text-dark">
                  <button type="button" @click="term_clicked(term)" class="btn btn-outline-dark">{{term}}</button>
                </span>
                <small class="float-end mb-2">
                <button class="accordion-button btn-sm disable-blue" type="button" @click="headline.expand = !headline.expand" :class="{ collapsed: !headline.expand }" aria-expanded="false"/>
        <!--          <a href="javascript:void(0);" @click="headline.expand = !headline.expand">כתבות נוספות...</a>-->
                </small>
        </div>
          
      
    </div>
    `

};