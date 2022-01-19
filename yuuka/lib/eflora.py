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

def iplant_value_from_latin(latin_name):
    # convert latin name to iplant searching name
    if "'" in latin_name:
        # Cultivated species
        return latin_name.replace("'", "cv. '", 1)
    else:
        return latin_name

def search_cvh(keyword):
    """
    search keyword from cvh database
    Example for returned value:
        [{'value': 'Saxifraga stolonifera',
        'format': '<em>Saxifraga stolonifera</em>',
        'desc': '虎耳草'}]
    """
    search_url = cvh_search_url.format(keyword=keyword)
    results = requests.get(search_url, headers={'referer': 'https://www.cvh.ac.cn/species/taxon_tree.php'}).json()
    for i in results:
        i['url'] = cvh_base_url.format(value=i['value'])
    #TODO return species objects
    return results

def species_info_cvh(species):
    """
    Example for returned value:
        {'id': 'T20171000024074',
        'canName': 'Saxifraga stolonifera',
        'sciName': '<em>Saxifraga stolonifera</em>  <em></em> Curtis',
        'chName': '虎耳草',
        'taxon': {'genus': 'Saxifraga',
        'genus_c': '虎耳草属',
        'family': 'Saxifragaceae',
        'family_c': '虎耳草科',
        'phylum': 'Angiospermae',
        'phylum_c': '被子植物门'}}
    """
    url = cvh_species_url.format(species=species)
    results = requests.get(url, headers={'referer': 'https://www.cvh.ac.cn/species/taxon_tree.php'}).json()
    required_info = ['id', 'canName', 'sciName', 'chName', 'taxon']
    try:
        species_info = {k: v for k, v in results['info'].items() if k in required_info}
    except KeyError:
        return None
    return species_info