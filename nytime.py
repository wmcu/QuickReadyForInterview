import requests
import urllib


def nytime_json(keyword='google'):
    '''
    demo:
    result = nytime_json('google')
    for it in result:
        print it['abstract']
    '''
    base_url = r'http://api.nytimes.com/svc/search/v2/articlesearch.json'
    query = keyword
    begin_date = r'20100101'
    fq = r'news_desk:("Business" "Technology") AND headline:("%s")' % keyword
    api_key = r'7182809a0aab73c3c0fb8b6d0af04c31:5:71187653'
    result = []

    payload = {
        'q': query,
        'fq': fq,
        'page': 0,
        'begin_date': begin_date,
        'api-key': api_key
    }

    for p in range(3):
        payload['page'] = p
        response = requests.get(base_url, params=payload).json()
        result0 = response['response']['docs']

        for it in result0:
            if it['lead_paragraph'] is None: continue
            web_url = it['web_url']
            headline = it['headline']['main'].encode('UTF-8')
            paragraph = it['lead_paragraph'].encode('UTF-8')
            pub_date = it['pub_date']
            thumb = next((x['url']
                          for x in it['multimedia']
                          if x['subtype']=='thumbnail'),
                         '')
            result.append({
                'web_url': web_url,
                'headline': headline,
                'paragraph': paragraph,
                'pub_date': pub_date,
                'thumb': thumb
                })

    return result

if __name__ == '__main__':
    result = nytime_json('google')
    for it in result:
        print "**", it['headline']