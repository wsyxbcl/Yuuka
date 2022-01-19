# species nameing patch for quarrying_plantid_label_map
import csv
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

    def suggest_label(self, cn_name_suggest=None):
        #TODO specify format for unnamed species in Chinese
        # Unfinished, only for species name correction

        if not cn_name_suggest:
            cn_name_suggest = self.iplant_name_cn

        label_suggest = '_'.join(self.label.split('_')[:2])+'_'+cn_name_suggest
        label_name_latin_suggest = self.iplant_name_latin
        return (label_suggest, label_name_latin_suggest)

    def add_to_csv(self, filename):
        # for offline analysis
        with open(filename, 'a') as f:
            f.write(','.join([self.label_id, self.label, self.label_name_cn, str(self.label_name_latin), 
                              str(self.iplant_name_cn), str(self.iplant_name_latin), 
                              str(self.cvh_name_cn), str(self.cvh_name_latin)]))
            f.write('\n')

    def add_to_label_map(self, filename):
        # for CV model
        with open(filename, 'a') as f:
            f.write(','.join([self.label_id, self.label, str(self.label_name_latin)])) 
            f.write('\n')

    @classmethod
    def from_csv(cls, data, header=['label_id', 'label', 'label_name_cn', 'label_name_latin', 
                                    'iplant_name_cn', 'iplant_name_latin', 'cvh_name_cn', 'cvh_name_latin']):
        species = cls.__new__(cls)
        for (i, value) in enumerate(data):
            if value == 'None':
                value = None
            setattr(species, header[i], value)
        return species

    def __repr__(self):
        return "{0.label_id} {0.label} {0.label_name_latin}\niplant: {0.iplant_name_cn} {0.iplant_name_latin}\ncvh: {0.cvh_name_cn} {0.cvh_name_latin}\n".format(self)
    def __str__(self):
        return "{0.label_id} {0.label} {0.label_name_latin}".format(self)


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

    result = Species(label=label[1], label_id=label_id, label_name_cn=label_name_cn, label_name_latin=label_name_latin,
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
    offline = True # using local csv data

    label_list = np.loadtxt("./lib/quarrying_plant_id/plantid/models/quarrying_plantid_label_map.txt", 
                            dtype=str, delimiter=',')
    output_csv = "./data/species.csv"
    output_label_map = "./data/quarrying_plantid_label_map.txt"

    if offline:
        species_list = []
        with open(output_csv, 'r') as f:
            data_csv = csv.reader(f)
            for data in data_csv:
                species_list.append(Species.from_csv(data))
        for species in species_list:
            # CompoundLabelIssue
            if '&' in species.label_name_cn:
                #TODO
                print(f"CompoundLabelIssue: {species}")
                continue

            # TaxonIssue
            if species.label_name_latin == '':
                # missing latin name or non-plant species
                print(f"TaxonIssue: {species}")
                user_command = input("(S)uggest/(N)on-plant/(P)ass)? ").lower()
                if user_command == 's':
                    label_suggestion, label_latin_suggestion = species.suggest_label()
                    print(f"Label suggestion: {label_suggestion} {label_latin_suggestion}")
                    if input("(A)ccept/(P)ass").lower == 'a':
                        species.label = label_suggestion
                        species.label_name_latin = label_latin_suggestion
                    else:
                        continue
                else:
                    continue

            # NameingIssue
            if species.iplant_name_latin:
                # LatinNameIssue
                if species.label_name_latin != species.iplant_name_latin:
                    print(f"LatinNameIssue: {species}")
                    print(species.__repr__)
                    #TODO

                # CNnameIssue
                if species.cvh_name_cn and species.iplant_name_cn:
                    if species.cvh_name_cn == species.label_name_cn:
                        print(f"{species} Passed")
                        continue
                    else:
                        # Prefer cvh name over iplant
                        print(f"CNnameIssue: {species}")
                        print(species.__repr__)
                        print("Suggest CVH name instead")
                        label_suggestion, label_latin_suggestion = species.suggest_label(cn_name_suggest=species.cvh_name_cn)
                        print(f"Label updated: {label_suggestion} {label_latin_suggestion}")
                        species.label_name_cn = species.cvh_name_cn
                        species.label = label_suggestion
                elif species.iplant_name_cn:
                    if species.iplant_name_cn == species.label_name_cn:
                        print(f"{species} Passed")
                        continue
                    else:
                        # iplant name as reference
                        print(f"CNnameIssue: {species}")
                        print(species.__repr__)
                        label_suggestion, label_latin_suggestion = species.suggest_label()
                        print(f"Label suggestion: {label_suggestion} {label_latin_suggestion}")
                        species.label_name_cn = species.iplant_name_cn
                        species.label = label_suggestion
                else:
                    # no reference Chinese name in database
                    #TODO replace '<某种>'
                    continue

            else:
                # no reference
                print(f"No reference: {species.label_id} {species.label}")
                continue
        for species in species_list:
            species.add_to_label_map(output_label_map)

    else:
        for (i, label) in enumerate(label_list):
            species = label_analyzer(label, debug=True)
            species.add_to_csv(output_csv)