import requests


iplant_base_url = "http://www.iplant.cn/info/{value}"
iplant_search_url = "http://www.iplant.cn/ashx/searchautocomplete.ashx?query={keyword}"

def search_iplant(keyword):
    search_url = iplant_search_url.format(keyword=keyword)
    results = requests.get(search_url).json()['suggestions']
    for i in results:
        i['url'] = iplant_base_url.format(value=i['value'])
    #TODO return species objects
    return results