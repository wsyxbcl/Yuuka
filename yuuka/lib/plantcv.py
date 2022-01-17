# image recognition for plants

import cv2
import numpy as np

from lib.quarrying_plant_id import plantid

def imread_ex(filename, flags=-1):
    try:
        return cv2.imdecode(np.fromfile(filename, dtype=np.uint8), flags)
    except Exception as e:
        print('Image decode error!', e)
        return None

def photo_to_species(filename):
    plant_identifier = plantid.PlantIdentifier()
    image = imread_ex(filename)
    outputs = plant_identifier.identify(image, topk=5)
    results = []
    if outputs['status'] == 0:
        for i in range(3):
            species = {'taxon_chinese': outputs['results'][i]['chinese_name'], 
                       'value': outputs['results'][i]['latin_name'],
                       'probability': outputs['results'][i]['probability']}
            results.append(species)
        return results
    else:
        return None