# Import Packages
import pandas as pd
import numpy as np
try:
    from app.d_google_bigquery import csv_to_bq
except:
    from d_google_bigquery import csv_to_bq


#1. function
def invest(index, df):
    Sales_Price = float(df.loc[index, 'price'])  # Home price
    Down_Payment = float(20)  # Down payement
    Mortgage_Type = 25  # Mortage Amortization (Years)
    Interest_Rate = float(2.6 + .5)  # Mortage Interest (Years)

    # Revenus
    revenu_annuel = float(df.loc[index, 'revenus'])  # Revenu locatif
    revenu_autres = float(0)  # Revenu autres

    # Depenses
    vacances_perte_percentage = 3  # Pertes pour vacances
    taxe_municipal_percentage = 1.1  # Taxes Municipale et Scolaire
    entretien_general_percentage = 3  # Reserve pour entretiens general
    reserve_structural_percentage = 3  # Reserve structurale
    assurance = 2000  # Assurance Plex
    frais_gestion = 0  # Frais Gestions
    neige_paysagement = 1200  # Frais de paysagement
    publicite = 0
    Loan_Amount = Sales_Price * (1 - Down_Payment / 100)

    Loan_Term = int(12 * Mortgage_Type)

    R = 1 + (Interest_Rate) / (12 * 100)
    X = Loan_Amount * (R ** Loan_Term) * (1 - R) / (1 - R ** Loan_Term)

    Monthly_Interest = []
    Monthly_Balance = []
    for i in range(1, Loan_Term + 1):
        Interest = Loan_Amount * (R - 1)
        Loan_Amount = Loan_Amount - (X - Interest)
        Monthly_Interest = np.append(Monthly_Interest, Interest)
        Monthly_Balance = np.append(Monthly_Balance, Loan_Amount)

    Monthly_Payment = np.round(X, 2)
    Monthly_Capital = Monthly_Payment - Monthly_Interest

    # ROI Calculations
    reserve_structural = revenu_annuel * (reserve_structural_percentage / 100)
    entretien_general = revenu_annuel * (entretien_general_percentage / 100)
    vacances_perte = revenu_annuel * (vacances_perte_percentage / 100)
    taxe_municipal = Sales_Price * (taxe_municipal_percentage / 100)
    revenu = float(revenu_annuel + revenu_autres)
    depense = assurance + frais_gestion + neige_paysagement + publicite + reserve_structural + entretien_general + vacances_perte + taxe_municipal

    interet_annuel = Monthly_Interest[0] * 12
    capital_annuel = Monthly_Capital[0] * 12

    cashflow = revenu - depense - capital_annuel - interet_annuel

    revenu_apres_depense = revenu - depense
    revenu_apres_interet = revenu_apres_depense - interet_annuel

    cashflow_apres_capital = revenu_apres_interet - capital_annuel

    cashflow_net = cashflow_apres_capital + reserve_structural + entretien_general + vacances_perte

    rendement_annuel = cashflow_net + revenu_apres_interet

    cashflow_plus_capital = cashflow_apres_capital + revenu_apres_interet
    rendement_annuel_mise_de_fond = (cashflow_plus_capital / (Down_Payment * Sales_Price / 100))

    df.loc[index, 'cashflow'] = cashflow
    df.loc[index, 'cashflow_net'] = cashflow_net
    df.loc[index, 'rendement_annuel'] = rendement_annuel
    df.loc[index, 'rendement_annuel_mise_de_fond'] = rendement_annuel_mise_de_fond
    return df


def run_invest():
    print('Calcul des valeurs economiques...')
    data = pd.read_csv('data_preprocessed.csv')
    data = data[['price', 'revenus', 'ville', 'building_type', 'url', 'ratio']]
    data['cashflow_net'] = 0
    data['rendement_annuel'] = 0
    data['rendement_annuel_mise_de_fond'] = 0
    for index in range(len(data)):
        invest(index, data)
    data.to_csv('data_clean.csv', index=False)
    print(data.shape)
    return


def upload_data():
    print('Upload de la base de donnees sur Bigquery')
    dataset_id = 'plex'
    table_id = 'today_plexes'
    csv_to_bq('data_clean.csv', dataset_id, table_id, overwrite=True, auto=True)


#2. main_calculation_and_upload
def main_calculation_and_upload():
    run_invest()
    upload_data()
    return

#3. run main_calculation_and_upload
if __name__ == '__main__':
    main_calculation_and_upload()
