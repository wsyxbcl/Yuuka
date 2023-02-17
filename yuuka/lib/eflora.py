import re
import requests


iplant_base_url = "http://www.iplant.cn/info/{value}"
iplant_search_url = "http://www.iplant.cn/ashx/searchautocomplete.ashx?query={keyword}" # Not working

cvh_base_url = "https://www.cvh.ac.cn/species/taxon_tree.php?type=sp&param={value}"
cvh_species_url = "https://www.cvh.ac.cn/controller/species/species_info.php?spname={species}"
cvh_search_url = "https://www.cvh.ac.cn/controller/ajax/autocomplete.php?term={keyword}"
cvh_tree_url = "https://www.cvh.ac.cn/controller/species/tree_lazyload.php?type={level}&param={name}"
cvh_taxa_level = ['kin', 'phy', 'fam', 'gen']

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

def taxon_branch_cvh(taxon_level, taxon_name):
    """
    Retrieve an 1-level branch from the taxa tree from CVH
    """
    if taxon_level == 'kin':
        url = cvh_tree_url.split('?')[0]
    else:
        url = cvh_tree_url.format(level=taxon_level, name=taxon_name)
    results = requests.get(url, headers={'referer': 'https://www.cvh.ac.cn/species/taxon_tree.php'}).json()
    cvh_names = [taxa['text'].split()[1] for taxa in results]
    sci_names = [taxa['param'] for taxa in results]
    branch = [[x, y] for x,y in zip(sci_names, cvh_names)]
    return branch

def iterate_cvh():
    # Phylum
    taxa_phy = taxon_branch_cvh(taxon_level='kin', 'Plantae')
    # Family
    for family in taxa_phy:
        taxa_fam = taxon_branch_cvh(taxon_level='phy', family)
            # Genus
            for genus in taxa_fam:
                taxa_genus = taxon_branch_cvh(taxon_level='fam', genus)
                    # Species
                    for species in taxa_genus:
                        taxa_species = taxon_branch_cvh(taxon_level='gen', species):
        
