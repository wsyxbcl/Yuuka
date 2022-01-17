import requests


iplant_base_url = "http://www.iplant.cn/info/{value}"
iplant_search_url = "http://www.iplant.cn/ashx/searchautocomplete.ashx?query={keyword}" # Not working

cvh_base_url = "https://www.cvh.ac.cn/species/taxon_tree.php?type=sp&param={value}"
cvh_species_url = "https://www.cvh.ac.cn/controller/species/species_info.php?spname={species}"
cvh_search_url = "https://www.cvh.ac.cn/controller/ajax/autocomplete.php?term={keyword}"

def search_iplant(keyword): # temporaryly deprecated
    search_url = iplant_search_url.format(keyword=keyword)
    results = requests.get(search_url).json()['suggestions']
    for i in results:
        i['url'] = iplant_base_url.format(value=i['value'])
    #TODO return species objects
    return results

def search_cvh(keyword):
    search_url = cvh_search_url.format(keyword=keyword)
    results = requests.get(search_url, headers={'referer': 'https://www.cvh.ac.cn/species/taxon_tree.php'}).json()
    for i in results:
        i['url'] = cvh_base_url.format(value=i['value']))
    #TODO return species objects
    return results
