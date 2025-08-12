"""
Classe DataExtractor
---------------------
Ce module fournit des fonctions pour extraire différents types de données énergétiques
(prix spot, prix forward annuels/mensuels, courbes PFC) depuis Databricks, via tentaclio.

Auteur : Jean Bertin
Email : jean.bertin@octopusenergy.fr
"""

import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from yaspin import yaspin
import tentaclio as tio

class DataExtractor:
    @staticmethod
    def get_spot_price_fr(start_date: str, end_date: str) -> pd.DataFrame:
        """
        Récupère les prix spot de l’électricité en France depuis Databricks (marché EPEX spot)
        via la connexion simplifiée avec tentaclio.

        Paramètres :
        -----------
        start_date : str
            Date de début au format 'YYYY-MM-DD'.
        end_date : str
            Date de fin au format 'YYYY-MM-DD'.

        Retour :
        -------
        pd.DataFrame
            DataFrame avec les colonnes ['delivery_from', 'price_eur_per_mwh'] contenant
            les dates/heures de livraison et les prix spot correspondants.
        """

        # 1. Initialisation du spinner de chargement avec yaspin (affiche un message pendant l'exécution)
        with yaspin(text="Chargement des prix spot depuis Databricks...") as spinner:

            # 2. Connexion à Databricks via tentaclio (gestionnaire de contexte simplifié)
            databricks = "databricks+thrift://octoenergy-oefr-prod.cloud.databricks.com/"
            with tio.db(databricks) as client:

                # 3. Construction de la requête SQL pour récupérer les prix spot
                query = f"""
                    SELECT delivery_from, price_eur_per_mwh
                    FROM consumer.inter_energymarkets_epex_hh_spot_prices
                    WHERE source_identifier = 'epex'
                      AND price_date >= '{start_date}'
                      AND price_date < '{end_date}'
                    ORDER BY delivery_from
                """

                # 4. Récupération du curseur lié à la connexion Databricks
                cursor = client.cursor

                # 5. Exécution de la requête SQL sur le serveur Databricks
                cursor.execute(query)

                # 6. Récupération de toutes les lignes retournées par la requête
                rows = cursor.fetchall()

                # 7. Extraction des noms de colonnes depuis la description du curseur
                columns = [desc[0] for desc in cursor.description]

            # 8. Fin de la tâche : afficher une coche verte dans le spinner pour indiquer le succès
            spinner.ok("✅")

        # 9. Conversion des résultats en DataFrame pandas avec colonnes appropriées
        spot_df = pd.DataFrame(rows, columns=columns)

        # 10. Conversion de la colonne 'delivery_from' en datetime sans fuseau horaire (local naive)
        spot_df['delivery_from'] = pd.to_datetime(spot_df['delivery_from'], utc=True).dt.tz_localize(None)

        # 11. Conversion de la colonne 'price_eur_per_mwh' en float pour faciliter les calculs
        spot_df['price_eur_per_mwh'] = spot_df['price_eur_per_mwh'].astype(float)

        # 12. Retour du DataFrame final contenant les données de prix spot
        return spot_df


    @staticmethod
    def get_forward_price_fr_annual(cal_year: int) -> pd.DataFrame:
        """
        Récupère les prix forward annuels d’électricité en France pour une année donnée depuis Databricks (EEX),
        en utilisant une connexion simplifiée via tentaclio.

        Paramètres :
        -----------
        cal_year : int
            Année civile de livraison souhaitée (ex. 2026).

        Retour :
        -------
        pd.DataFrame
            DataFrame contenant les colonnes ['trading_date', 'forward_price', 'cal_year'] avec les
            dates de trading, les prix forward correspondants et l’année civile associée.
        """

        # 1. Initialisation du spinner de chargement
        with yaspin(text="Chargement des prix forward depuis Databricks...") as spinner:

            # 2. Connexion via tentaclio
            databricks = "databricks+thrift://octoenergy-oefr-prod.cloud.databricks.com/"
            with tio.db(databricks) as client:

                # 3. Construction de la requête SQL
                query = f"""
                    SELECT setllement_price AS forward_price, trading_date
                    FROM consumer.stg_eex_power_future_results_fr 
                    WHERE long_name = 'EEX French Power Base Year Future' 
                      AND delivery_start >= '{cal_year}-01-01'
                      AND delivery_end <= '{cal_year}-12-31'
                    ORDER BY trading_date
                """

                # 4. Exécution de la requête
                cursor = client.cursor
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

            # 5. Indication de succès via le spinner
            spinner.ok("✅")

        # 6. Transformation en DataFrame
        forward_df = pd.DataFrame(rows, columns=columns)

        # 7. Nettoyage et typage
        forward_df['trading_date'] = pd.to_datetime(forward_df['trading_date'], utc=True)
        forward_df['forward_price'] = forward_df['forward_price'].astype(float)
        forward_df['cal_year'] = cal_year

        # 8. Retour du résultat
        return forward_df


    @staticmethod
    def get_forward_price_fr_months(cal_year_month: str) -> pd.DataFrame:
        """
        Récupère les prix forward mensuels d’électricité en France depuis Databricks (EEX),
        en utilisant une connexion standardisée via tentaclio.

        Paramètres :
        -----------
        cal_year_month : str
            Mois de livraison au format 'YYYY-MM' (exemple : '2025-03').

        Retour :
        -------
        pd.DataFrame
            DataFrame avec les colonnes ['trading_date', 'forward_price', 'cal_year'] 
            contenant les dates de trading, les prix forward mensuels et le mois associé.
        """

        # 1. Calcul des bornes temporelles du mois
        start_date = datetime.strptime(cal_year_month, "%Y-%m")
        end_date = start_date + relativedelta(months=1)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")

        # 2. Initialisation du spinner de chargement
        with yaspin(text="Chargement des prix forward mensuels depuis Databricks...") as spinner:

            # 3. Connexion via tentaclio
            databricks = "databricks+thrift://octoenergy-oefr-prod.cloud.databricks.com/"
            with tio.db(databricks) as client:

                # 4. Requête SQL
                query = f"""
                    SELECT setllement_price, trading_date, delivery_start, delivery_end
                    FROM consumer.stg_eex_power_future_results_fr 
                    WHERE long_name = 'EEX French Power Base Month Future' 
                      AND delivery_start >= '{start_str}'
                      AND delivery_start < '{end_str}'
                      AND setllement_price IS NOT NULL
                    ORDER BY trading_date
                """
                forward_df = client.get_df(query)

            # 5. Fin du chargement
            spinner.ok("✅")

        # 6. Nettoyage et enrichissement
        forward_df.rename(columns={'setllement_price': 'forward_price'}, inplace=True)
        forward_df['trading_date'] = pd.to_datetime(forward_df['trading_date'], utc=True)
        forward_df['forward_price'] = forward_df['forward_price'].astype(float)
        forward_df['cal_year'] = cal_year_month
        forward_df = forward_df.drop_duplicates()

        # 7. Retour des données
        return forward_df


    @staticmethod
    def get_pfc_fr(price_date: int, delivery_year: int) -> pd.DataFrame:
        """
        Récupère les courbes de prix Price Forward Curve (« PFC ») pour la France depuis Databricks.

        Paramètres :
        -----------
        price_date : int
            Année de la date de prix (exemple : 2024).
        delivery_year : int
            Année de livraison des prix forward (exemple : 2025).

        Retour :
        -------
        pd.DataFrame
            DataFrame contenant les colonnes ['delivery_from', 'price_date', 'forward_price'] 
            correspondant aux dates de livraison, date de prix et prix forward associés.
        """

        # 1. Initialisation du spinner yaspin
        with yaspin(text="Chargement des prix PFC depuis Databricks...") as spinner:

            # 2. Connexion via tentaclio
            databricks = "databricks+thrift://octoenergy-oefr-prod.cloud.databricks.com/"
            with tio.db(databricks) as client:

                # 3. Construction de la requête SQL
                query = f"""
                    SELECT delivery_from,
                           price_date,
                           forward_price
                    FROM consumer.stg_octo_curves
                    WHERE mode = 'EOD'
                      AND asset = 'FRPX'
                      AND year(delivery_from) = '{delivery_year}'
                      AND year(price_date) = '{price_date}'
                    ORDER BY price_date
                """

                # 4. Exécution de la requête
                cursor = client.cursor
                cursor.execute(query)
                rows = cursor.fetchall()
                colnames = [desc[0] for desc in cursor.description]

            # 5. Fin du chargement
            spinner.ok("✅")

        # 6. Conversion en DataFrame pandas
        df = pd.DataFrame(rows, columns=colnames)

        # 7. Retour du DataFrame
        return df
