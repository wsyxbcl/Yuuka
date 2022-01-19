# species nameing patch for quarrying_plantid_label_map
from bs4 import BeautifulSoup
import numpy as np

from lib.eflora import *


class Species:
    def __init__(self, label, label_id, label_name_cn, label_name_latin, 
                 iplant_name_cn, iplant_name_latin, 
                 cvh_name_cn, cvh_name_latin):
        self.label = label
        self.label_id = label_id
        self.label_name_cn = label_name_cn
        self.label_name_latin = label_name_latin
        self.iplant_name_cn = iplant_name_cn
        self.iplant_name_latin = iplant_name_latin
        self.cvh_name_cn = cvh_name_cn
        self.cvh_name_latin = cvh_name_latin
    
    @property
    def get_iplant_url(self):
        return iplant_base_url.format(value=iplant_value_from_latin(self.iplant_name_latin))

    @property
    def get_cvh_url(self):
        return cvh_base_url.format(value=cvh_name_latin)

    def suggest_label(self, name_cn_suggest=None):
        #TODO specify format for unnamed species in Chinese
        # Unfinished, only for species name correction

        if not name_cn_suggest:
            name_cn_suggest = iplant_name_cn
        label_name_cn_suggest = '_'.join(self.label_name_cn.split('_')[:2].append(name_cn_suggest))
        label_name_latin_suggest = self.iplant_name_latin
        return [label_id, label_name_cn_suggest, label_name_latin_suggest]

    def add_to_csv(self, filename):
        with open(filename, 'a') as fp:
            fp.write(','.join([self.label_id, self.label_name_cn, str(self.label_name_latin), 
                              str(self.iplant_name_cn), str(self.iplant_name_latin), 
                              str(self.cvh_name_cn), str(self.cvh_name_latin)]))
            fp.write('\n')

    def __str__(self):
        return "label: {0.label!s}\niplant: {0.iplant_name_cn} {0.iplant_name_latin}\ncvh: {0.cvh_name_cn} {0.cvh_name_latin}\n".format(self)


def label_analyzer(label, debug=False):
    label_id = label[0]
    label_name_cn = label[1].split('_')[-1]
    try:
        label_name_latin = label[2]
    except IndexError:
        label_name_latin = None
    if '&' in label_name_latin:
        if debug:
            print("Compound species")
        iplant_name_cn = None
        iplant_name_latin = None
        cvh_name_cn = None
        cvh_name_latin = None
    else: 
        # iplant info
        r = requests.get(iplant_base_url.format(value=iplant_value_from_latin(label_name_latin)))
        soup = BeautifulSoup(r.content, 'html.parser')
        #TODO add test to check the format
        
        if not (iplant_name_latin := soup.find("div", {"class": "infolatin"}).text):
            # no matchup in iplant database
            if debug:
                print("No matchup")
            iplant_name_cn = None
            iplant_name_latin = None
            cvh_name_cn = None
            cvh_name_latin = None
            
        else:
            if not (iplant_name_cn := soup.find("span", {"class": "infocname"}).text):
                # unnamed species in Chinese
                iplant_name_cn = None

            # cvh info
            if cvh_info := species_info_cvh(species=iplant_name_latin):
                cvh_name_latin = cvh_info['canName']
                if 'chName' in cvh_info.keys():
                    cvh_name_cn = cvh_info['chName']
                else:
                    cvh_name_cn = None
            else:
                cvh_name_latin = cvh_name_cn = None

    result = Species(label=label, label_id=label_id, label_name_cn=label_name_cn, label_name_latin=label_name_latin,
                     iplant_name_cn=iplant_name_cn, iplant_name_latin=iplant_name_latin,
                     cvh_name_cn=cvh_name_cn, cvh_name_latin=cvh_name_latin)
    if debug:
        print(result)
    return result


# Some listed issues, manually iterating is preferred over broadcasting
# TaxonIssue: mismatched taxon hierarchy & wrong or empty latin names
    # mismatched taxon level / missed latin name
    # Fungi species
# NameingIssue
    # LatinNameIssue: wrong or incomplete latin names
    # CNnameIssue: wrong or empty Chinese species names
        # unnamed species in Chinese
        # missed Chinese names
        # (updated Chinese names) 
# CompoundLabelIssue
    # genus and compound species (&) in label

if __name__ == '__main__':
    plant_list = np.loadtxt("./lib/quarrying_plant_id/plantid/models/quarrying_plantid_label_map.txt", 
                            dtype=str, delimiter=',')
    output_file = "./species.csv"

    for (i, label) in enumerate(plant_list):
        # # CompoundLabelIssue
        # if '&' in label[1]: 
        #     #TODO
        #     print(f"CompoundLabelIssue: {str(label)}")
        #     continue

        species = label_analyzer(label, debug=True)
        species.add_to_csv(output_file)
        # TaxonIssue
        # if species.label_name_latin:
        #     level_cn = len(label[1].split('_'))
        #     level_latin = len(species.label_name_latin.split(' '))
        #     if (level_cn == 2 and level_latin >= 2) or (level_cn == 3 and level_latin == 1):
        #         # mismatched taxon level
        #         print(f"TaxonIssue: {label}")
        #         label_suggestion = species.suggest_label()
        #         print(f"Label suggestion: {label_suggestion}")
        #         user_command = input("(A)ccept/(P)ass)? ").lower()
        #         if user_command == 'a':
        #             plant_list[i] = label_suggestion
        #         else:
        #             continue
        # else:
        #     # missing latin name or non-plant species
        #     print(f"TaxonIssue: {label}")
        #     user_command = input("(S)uggest/(N)on-plant/(P)ass)? ").lower()
        #     if user_command == 's':
        #         label_suggestion = species.suggest_label()
        #         print(f"Label suggestion: {label_suggestion}")
        #         if input("(A)ccept/(P)ass").lower == 'a':
        #             plant_list[i] = label_suggestion
        #         else:
        #             continue
        #     else:
        #         continue


        # # NameingIssue
        # if species.iplant_name_latin:
        #     # LatinNameIssue
        #     if species.label_name_latin != species.iplant_name_latin:
        #         print(f"LatinNameIssue: {str(label)}")
        #         print(species)
        #         #TODO

        #     # CNnameIssue
        #     if species.cvh_name_cn and species.iplant_name_cn:
        #         if species.cvh_name_cn in (species.cvh_name_cn, species.iplant_name_cn, species.label_name_cn):
        #             print(f"{str(label)} Passed")
        #             continue
        #         else:
        #             # Prefer cvh name over iplant
        #             print(f"CNnameIssue: {str(label)}")
        #             print("Suggest CVH name instead")
        #             label_suggestion = sepcies.suggest_label(cn_name_suggest=species.cvh_name_cn)
        #             print(f"Label suggestion: {label_suggestion}")
        #             if input("(A)ccept/(P)ass").lower == 'a':
        #                 plant_list[i] = label_suggestion
        #             else:
        #                 continue
        #     elif species.iplant_name_cn:
        #         # iplant name as reference
        #         if species.iplant_name_cn == species.label_name_cn:
        #             print(f"{str(label)} Passed")
        #             continue
        #     else:
        #         # no reference Chinese name in database
        #         #TODO replace '<某种>'
        #         continue
        #     # unmatched Chinese name
        #     print(f"CNnameIssue: {str(label)}")
        #     print(species)
        #     # TODO  

        # else:
        #     # no reference
        #     print(f"No reference: {str(label)}")
        #     continue
    