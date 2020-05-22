# Import Package
import pandas as pd
import numpy as np
import re, unidecode, shutil
from sklearn.preprocessing import MultiLabelBinarizer

#1. function
def keep_numeric(x):
    x = str(x).replace(' ', '')
    x = re.sub('[^0-9]', '', str(x))
    try:
        x = float(x)
    except:
        x = np.nan
    return x


def keep_character(x):
    x = str(x)
    x = x.replace('(', '')
    x = x.replace(')', '')
    x = re.sub("\d+", '', str(x))
    return x


def check_stationnement(x, word):
    if x is not np.NaN:
        for i in x:
            if word in i:
                nombre_abri = re.sub('[^0-9]', '', str(i))
                return float(nombre_abri)
            else:
                nombre_abri = 0.0
                return float(nombre_abri)
    else:
        nombre_abri = 0.0
        return float(nombre_abri)


def city(x):
    if len(x) > 2:
        city = x[2]
        return str(city)
    else:
        return 'non reconnue'


def check_unit(x, word):
    if x is not np.NaN:
        for i in x:
            if word in i:
                nombre = i.split('x')[0]
                return float(nombre)
            else:
                nombre = 0.0
                return nombre
    else:
        nombre = 0.0
        return nombre


def annee(data):
    data['age_inconnu'] = np.where(data['annee'] == 'Âge inconnu', 1, 0)
    try:
        data['construction_centenaire'] = np.where(data['annee'].str.contains('Centenaire'), 1, 0)
    except:
        data['construction_centenaire']=0
    try:
        data['construction_historique'] = np.where(data['annee'].str.contains('Historique'), 1, 0)
    except:
        data['construction_historique']=0
    try:
        data['construction_neuve'] = np.where(data['annee'].str.contains('Neuve'), 1, 0)
    except:
        data['construction_neuve'] = 0
    data['annee'] = [keep_numeric(x) for x in data['annee']]
    data['annee'] = 2020 - data['annee']
    return data


def utilisation(data):
    data = data[data['utilisation'] != 'Résidentielle et commerciale']
    return data


def supeficie(data):
    data['superficie_terrain'] = [keep_numeric(x) for x in data['superficie_terrain']]
    data['superficie_batiment'] = [keep_numeric(x) for x in data['superficie_batiment']]
    return data


def stationnement(data):
    data['stationnement'] = data['stationnement'].str.split(',')
    data['inconne_stationnement'] = np.where(data['stationnement'].isnull() == True, 1, 0)
    data['abri_stationnement'] = [check_stationnement(x, word="Abri d'auto") for x in data['stationnement']]
    data['allee_stationnement'] = [check_stationnement(x, word="Allée") for x in data['stationnement']]
    data['garage_stationnement'] = [check_stationnement(x, word="Garage") for x in data['stationnement']]
    data['total_stationnement'] = data[["abri_stationnement", "allee_stationnement", 'garage_stationnement']].sum(
        axis=1)
    del data['stationnement']
    return data


def building_type(data):
    data['unitees'] = [keep_numeric(x) for x in data['unitees']]
    data['building_type'] = data['building_type'].str.replace(' à vendre', '').str.strip()
    data[['building_type', 'unitees']]
    data[(data['building_type'] == "Quadruplex") & (data['unitees'] == 5.0)]['building_type'] = 'Quintuplex'
    data = data[(data['building_type'] != "Quintuplex") & (data['unitees'] != 5.0)]
    data[(data['building_type'] == "Triplex") & (data['unitees'] != 3.0)]['building_type'] = 'Quadruplex'
    return data


def autres(data):
    data['autres'] = np.where(data['autres'].isnull() == True, 'aucun', data['autres'])
    data['autres'] = [unidecode.unidecode(x).lower() for x in data['autres']]
    data['autres'] = data['autres'].str.strip()
    data['autres'] = data['autres'].str.replace(', ', ',')
    data['autres'] = data['autres'].str.split(',')
    mlb = MultiLabelBinarizer()
    data = data.join(pd.DataFrame(mlb.fit_transform(data.pop('autres')), columns=mlb.classes_, index=data.index))
    return data


def adresse(data):
    data['ville'] = data['adresse'].str.split(',')
    data['ville'] = [city(x) for x in data['ville']]
    data['ville'] = data['ville'].str.split('(')
    data['ville'] = [unidecode.unidecode(x[0]).lower().strip() for x in data['ville']]
    return data


def price(data):
    data['revenus'] = [keep_numeric(x) for x in data['revenus']]
    data['price'] = [keep_numeric(x) for x in data['price']]
    data = data[data['price'] > 200000]
    data['revenus'] = np.where(data['revenus'] < 5000, np.NaN, data['revenus'])
    return data


def unite_residence(data):
    data['unitee_res'] = data['unitee_res'].str.split(',')
    data['unitee_res_1'] = [check_unit(x, '1 1⁄2') for x in data['unitee_res']]
    data['unitee_res_2'] = [check_unit(x, '2 1⁄2') for x in data['unitee_res']]
    data['unitee_res_3'] = [check_unit(x, '3 1⁄2') for x in data['unitee_res']]
    data['unitee_res_4'] = [check_unit(x, '4 1⁄2') for x in data['unitee_res']]
    data['unitee_res_5'] = [check_unit(x, '5 1⁄2') for x in data['unitee_res']]
    data['unitee_res_6'] = [check_unit(x, '6 1⁄2') for x in data['unitee_res']]
    data['unitee_res_7'] = [check_unit(x, '7 1⁄2') for x in data['unitee_res']]
    data['unitee_res_8'] = [check_unit(x, '8 1⁄2') for x in data['unitee_res']]
    data['unitee_res_9'] = [check_unit(x, '9 1⁄2') for x in data['unitee_res']]
    return data


def final_cleaning(data):
    data = data.reset_index(drop=True)
    df_filled = pd.DataFrame(
        columns={"utilisation", "style", "annee", "superficie_terrain", "superficie_batiment", "unitees", "revenus",
            "building_type", "age_inconnu", "construction_centenaire", "construction_historique", "construction_neuve",
            "inconne_stationnement", "abri_stationnement", "allee_stationnement", "garage_stationnement",
            "total_stationnement", "acces a un fleuve", "acces a un lac", "acces a une riviere",
            "adapte pour mobilite reduite", "ascenseur", "aucun", "bord d'un fleuve", "bord d'un lac",
            "bord d'un ruisseau", "bord d'une riviere", "bord de mer", "plan d'eau navigable",
            "plan d'eau non navigable", "reprise de finance", "sous-sol 6 pieds +", "ville", "price", "unitee_res_1",
            "unitee_res_2", "unitee_res_3", "unitee_res_4", "unitee_res_5", "unitee_res_6", "unitee_res_7",
            "unitee_res_8", "unitee_res_9", "ratio", "url"})
    df_filled.loc[0] = 0
    df_filled = data.combine_first(df_filled)
    df_filled.to_csv('data_preprocessed.csv', index=False)
    return


#2. main_preprocessing
def main_preprocessing():
    data = pd.read_csv('plex.csv')
    print('Processing plex.csv File')
    data = utilisation(data)
    print('Processing utilisation...')
    data = annee(data)
    print('Processing annee...')
    data = supeficie(data)
    print('Processing superficie...')
    data = stationnement(data)
    print('Processing stationnement...')
    data = building_type(data)
    print('Processing building_type...')
    data = autres(data)
    print('Processing autres...')
    data = adresse(data)
    print('Processing adresse...')
    data = price(data)
    print('Processing price...')
    data = unite_residence(data)
    print('Processing unite_residence...')
    final_cleaning(data)
    shutil.rmtree('json_files')
    print('Folder deleted...')
    return

#3. run main_preprocessing
if __name__ == '__main__':
    main_preprocessing()