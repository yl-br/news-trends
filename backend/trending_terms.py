import datetime

def get_trends(termCounter):
    today = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    out_trends = {}
    out_all_terms = set()
    for day_diff in range(7):
        previous_day = today - datetime.timedelta(days=day_diff+1)
        current_day = today - datetime.timedelta(days=day_diff)

        counts_previous = termCounter.create_terms_counts_mask(previous_day-datetime.timedelta(days=1),previous_day, min_count=4)
        counts_current = termCounter.create_terms_counts_mask(current_day-datetime.timedelta(days=1),current_day, min_count=4)

        bigram_counts_range1 = {k:v for k, v in counts_previous.items() if ' ' in k}
        bigram_counts_range2 = {k:v for k, v in counts_current.items() if ' ' in k}

        sort_by_difference = lambda term: len(bigram_counts_range1.get(term, [])) - len(bigram_counts_range2.get(term, []))
        terms = list(set([*bigram_counts_range1] + [*bigram_counts_range2]))
        terms.sort(key=sort_by_difference, reverse= True)
        # terms = calculate_trending_terms(bigram_counts_range1, bigram_counts_range2)
        chosen_day_terms = terms[:10] + terms[-10:]
        out_trends[current_day.date().isoformat()] = chosen_day_terms
        out_all_terms.update(chosen_day_terms)

    return out_trends,out_all_terms

# def calculate_trending_terms(terms_range1, terms_range2):
#     out_terms_list = []
#
#     for term in set([*terms_range1] + [*terms_range2]):
#         range1_count = len(terms_range1.get(term, []))
#         range2_count = len(terms_range2.get(term, []))
#         score = range1_count - range2_count
#         out_terms_list.append({'term':term,'range1':range1_count, 'range2':range2_count, 'score': score})
#
#     out_terms_list.sort(key=lambda item: item['score'], reverse=True)
#     return out_terms_list