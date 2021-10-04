const Articles = {
    props: {},
    data() {
        return {
            single_term: null,
            connection_terms: null,
            occurrences:[],
            sources_map:sources_map
        }
    },
    mounted(){
        this.emitter.on('term-selected', selected_term =>{
            this.load_term(selected_term);
        });
        let self = this;
        this.emitter.on('connection-selected', function(event) {
            self.load_connection(event.termA,event.termB);
        })
    },
    methods: {
        load_term(term){
            axios.get('/terms/' + term).then(response => {
                this.occurrences = response.data
                this.occurrences.forEach(o=> o.timestamp = Date.parse(o.timestamp))
                this.occurrences.sort((o1, o2)=> o2.timestamp - o1.timestamp);

                this.connection_terms = null;
                this.single_term = term
            });
        },
        load_connection(termA, termB){
            axios.get(`/connections/${termA}/${termB}`).then(response => {
                this.occurrences = response.data
                this.occurrences.forEach(o=> o.timestamp = Date.parse(o.timestamp))
                this.occurrences.sort((o1, o2)=> o2.timestamp - o1.timestamp);

                this.single_term =null;
                this.connection_terms = {termA: termA.length > termB.length? termA : termB, termB:termB.length < termA.length ? termB : termA};
            });
        },
        display_date(timestamp){
            return moment(timestamp).fromNow()
        },
        display_snippet(snippet){
            if (this.single_term){
                return '• ' + snippet.replaceAll(this.single_term, `<b>${this.single_term}</b>`)
            }
            else if (this.connection_terms){
                return '&#x25CF;' + snippet.replaceAll(this.connection_terms.termA, `<b>${this.connection_terms.termA}</b>`)
                    .replaceAll(this.connection_terms.termB, `<b>${this.connection_terms.termB}</b>`)
            }
        }
    },
    computed:{
    },
    template:`
    <h3 v-if="single_term"><u>אזכורים בכתבות:</u> <b>{{single_term}}</b></h3>
    <h3 v-else-if="connection_terms"><u>אזכורים בכתבות:</u> <b>{{connection_terms.termB}}</b>  {{'  <----->  '}}  <b>{{connection_terms.termA}}</b></h3>
    <div class="container" style="height:300px; overflow-y:auto;direction: ltr">
        <div class="my-3 p-3 bg-body rounded shadow-sm" dir="rtl">
            
        <div v-for="article in occurrences.slice(0,20)" class="d-flex text-muted pt-3">
          <svg class="bd-placeholder-img flex-shrink-0 me-2 rounded" width="24" height="24" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Placeholder: 32x32" preserveAspectRatio="xMidYMid slice" focusable="false">          
            <image :href="sources_map[article.source].img_url" width="24" height="24"></image>
          </svg>
    
          <p class="pb-3 mb-0 small lh-sm border-bottom">
            <a target="_blank" rel="noopener noreferrer" :href="article.url" class="articles-title-link">
                <h6 class="d-block text-gray-dark">{{article.title}} ({{sources_map[article.source].display_value}} - {{display_date(article.timestamp)}})</h6>
            </a>
            <span v-for="snippet in article.snippets" v-html="display_snippet(snippet)">
            
            </span>
          </p>
        </div>
        
        </div>
        
    </div>
    `

};