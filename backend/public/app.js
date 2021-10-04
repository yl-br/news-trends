const appComponent = {
    data() {
        return {
            selected_term:null
        }
    },
    create(){
    },
    mounted(){
        this.emitter.on('term-selected', term=>{
            console.log(`term_selected: ${term}`);

            let div_element = document.getElementById("term-data");
            if(!this.selected_term){
                setTimeout(()=>{
                    div_element.scrollIntoView(true);
                    },200);
            }
            else if(!this.isElementXPercentInViewport(div_element, 25)){
                div_element.scrollIntoView(true);
            }

            // window.scrollTo(0,document.body.scrollHeight-200);
            this.selected_term = term;
        })
    },
    methods: {
        term_clicked(selected_term){
            this.emitter.emit('term-selected', selected_term);
        },
        isElementXPercentInViewport(el, percentVisible) {
            let rect = el.getBoundingClientRect(), windowHeight = (window.innerHeight || document.documentElement.clientHeight);

            return !(
                Math.floor(100 - (((rect.top >= 0 ? 0 : rect.top) / +-rect.height) * 100)) < percentVisible ||
                Math.floor(100 - ((rect.bottom - windowHeight) / rect.height) * 100) < percentVisible
            )
        }
    }

};

moment.locale('he');

const app = Vue.createApp(appComponent);
const emitter = mitt();
app.config.globalProperties.emitter = emitter;

app.component('trends', Trends);
app.component('network',Network);
app.component('popularity',Popularity);
app.component('connected-terms',ConnectedTerms);
app.component('term-search',TermSearch);
app.component('dataset-info',DatasetInfo);
app.component('headlines',Headlines);
app.component('articles',Articles);

app.mount('#app');