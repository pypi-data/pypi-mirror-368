"""
Classe Forecast
---------------
Ce module contient la classe Forecast qui permet de :
1. Récupérer les températures horaires moyennes lissées sur les grandes villes françaises
2. Effectuer une prévision de consommation (ou autre cible) à l’aide d’un modèle Random Forest.

Auteur : Jean Bertin
Email : jean.bertin@octopusenergy.fr
"""

import numpy as np
import pandas as pd
import requests
import holidays
from tqdm import tqdm
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


class Forecast:

    @staticmethod
    def get_temp_smoothed_fr(start_date: str, end_date: str) -> pd.DataFrame:
        """
        Récupère les températures moyennes horaires lissées sur plusieurs grandes villes françaises.

        Paramètres :
        -----------
        start_date : str
            Date de début (format 'YYYY-MM-DD').
        end_date : str
            Date de fin (format 'YYYY-MM-DD').

        Retour :
        -------
        pd.DataFrame
            DataFrame avec les colonnes ['timestamp', 'temperature'] représentant la température moyenne lissée.
        """

        # 1. Définition des grandes villes françaises pour lisser les données à l'échelle nationale
        cities = {
            "Paris": (48.85, 2.35),
            "Lyon": (45.76, 4.84),
            "Marseille": (43.30, 5.37),
            "Lille": (50.63, 3.07),
            "Toulouse": (43.60, 1.44),
            "Strasbourg": (48.58, 7.75),
            "Nantes": (47.22, -1.55),
            "Bordeaux": (44.84, -0.58)
        }

        city_dfs = []  # 2. Liste pour stocker les DataFrames de chaque ville

        # 3. Boucle sur chaque ville pour récupérer les données météo horaires via l'API Open-Meteo
        for city, (lat, lon) in tqdm(cities.items(), desc="Fetching city data"):
            url = "https://archive-api.open-meteo.com/v1/archive"
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date,
                "end_date": end_date,
                "hourly": "temperature_2m",
                "timezone": "Europe/Paris"
            }
            try:
                # 4. Requête GET à l'API météo
                response = requests.get(url, params=params)
                response.raise_for_status()  # Vérifie que la requête est OK
                data = response.json()

                # 5. Construction du DataFrame pour la ville courante
                df = pd.DataFrame({
                    'timestamp': data['hourly']['time'],
                    city: data['hourly']['temperature_2m']
                })
                df['timestamp'] = pd.to_datetime(df['timestamp'])  # Conversion en datetime
                df.set_index('timestamp', inplace=True)  # Mise en index sur la date/heure

                city_dfs.append(df)  # 6. Ajout du DataFrame ville à la liste

            except Exception as e:
                print(f"Error with {city}: {e}")  # 7. Gestion simple des erreurs

        # 8. Fusion de tous les DataFrames de villes selon l'index timestamp (concaténation horizontale)
        df_all = pd.concat(city_dfs, axis=1)

        # 9. Calcul de la moyenne horaire sur toutes les villes (lissage national)
        df_all['temperature'] = df_all.mean(axis=1)

        # 10. Retourne uniquement la colonne timestamp et la température moyenne lissée (réinitialisation de l'index)
        return df_all[['temperature']].reset_index()

    @staticmethod
    def eval_forecast(df, temp_df, cal_year=None, datetime_col='timestamp', target_col='MW', plot_chart=False, save_path=None):
        """
        Calcule un forecast (et éventuellement affiche un graphique) pour une année donnée.

        Paramètres :
        -----------
        df : pd.DataFrame
            Données historiques contenant au moins les colonnes datetime_col et target_col.
        temp_df : pd.DataFrame
            Données de température avec colonnes ['datetime', 'temperature'].
        cal_year : int ou None, optionnel (par défaut None)
            Année civile pour laquelle générer la prévision. Obligatoire si plot_chart=True.
        datetime_col : str, optionnel (par défaut 'timestamp')
            Nom de la colonne contenant les timestamps dans df.
        target_col : str, optionnel (par défaut 'MW')
            Nom de la colonne cible à prédire dans df.
        plot_chart : bool, optionnel (par défaut False)
            Indique si un graphique interactif Plotly doit être généré.
        save_path : str ou None, optionnel
            Chemin pour sauvegarder le graphique HTML si plot_chart est True.

        Retour :
        --------
        pd.DataFrame
            DataFrame contenant les colonnes datetime_col, target_col et 'forecast' (prévision).
        """

        # 1. Vérifie la cohérence des paramètres
        if cal_year is None and plot_chart:
            raise ValueError("Vous devez fournir `cal_year` si vous souhaitez générer un graphique.")

        # 2. Fixe la graine aléatoire pour assurer la reproductibilité
        np.random.seed(42)

        # 3. Copie des données d'origine pour éviter modifications involontaires
        df = df.copy()

        # 4. Uniformise la colonne datetime
        df[datetime_col] = pd.to_datetime(df[datetime_col], utc=True).dt.tz_localize(None)

        # 5. Suppression des lignes où datetime ou target est manquant
        df = df.dropna(subset=[datetime_col, target_col])

        # 6. Tri chronologique des données et ré-indexation
        df = df.sort_values(datetime_col).reset_index(drop=True)

        # 7. Vérification que les données couvrent toute l’année cal_year
        expected_start = pd.Timestamp(f"{cal_year}-01-01 00:00:00")
        expected_end = pd.Timestamp(f"{cal_year}-12-31 23:59:59")
        if not ((df[datetime_col] <= expected_start).any() and (df[datetime_col] >= expected_end).any()):
            raise ValueError(
                f"Les données ne couvrent pas toute l’année civile {cal_year}.\n"
                f"Période attendue : {expected_start.date()} à {expected_end.date()}\n"
                f"Données disponibles de {df[datetime_col].min().date()} à {df[datetime_col].max().date()}"
            )

        # 8. Définition de la période de test correspondant à l’année cal_year
        test_start = expected_start
        test_end = expected_end

        # 9. Nettoyage des données météo
        temp_df = temp_df.copy()
        temp_df[datetime_col] = pd.to_datetime(temp_df['timestamp'], utc=True).dt.tz_localize(None)
        #temp_df = temp_df.drop(columns=['timestamp'])

        # 10. Fusion avec les données principales
        df = pd.merge(df, temp_df, on=datetime_col, how='left')

        # 11. Remplissage des valeurs manquantes
        df['temperature'] = df['temperature'].ffill().bfill()

        # 12. Ajout des features temporelles
        def add_features(df):
            df['hour'] = df[datetime_col].dt.hour
            df['dayofweek'] = df[datetime_col].dt.dayofweek
            df['month'] = df[datetime_col].dt.month

            df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
            df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
            df['dayofweek_sin'] = np.sin(2 * np.pi * df['dayofweek'] / 7)
            df['dayofweek_cos'] = np.cos(2 * np.pi * df['dayofweek'] / 7)
            df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
            df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)

            df['minute'] = df[datetime_col].dt.minute
            df['is_weekend'] = (df['dayofweek'] >= 5).astype(int)
            df['dayofyear'] = df[datetime_col].dt.dayofyear
            df['week'] = df[datetime_col].dt.isocalendar().week.astype(int)
            df['quarter'] = df[datetime_col].dt.quarter
            df['is_month_start'] = df[datetime_col].dt.is_month_start.astype(int)
            df['is_month_end'] = df[datetime_col].dt.is_month_end.astype(int)

            fr_holidays = holidays.country_holidays('FR')
            df['is_holiday'] = df[datetime_col].dt.date.astype(str).isin(fr_holidays).astype(int)

            df['heating_on'] = (df['temperature'] < 15).astype(int)
            df['cooling_on'] = (df['temperature'] > 25).astype(int)

            df['temp_below_10'] = np.maximum(0, 10 - df['temperature'])
            df['temp_above_30'] = np.maximum(0, df['temperature'] - 30)
            df['temp_diff_15'] = df['temperature'] - 15

            return df

        df = add_features(df)

        # 13. Suppression des valeurs manquantes restantes
        df = df.dropna().reset_index(drop=True)

        # 14. Séparation train/test
        train_df = df[(df[datetime_col] < test_start) | (df[datetime_col] > test_end)].copy()
        test_df = df[(df[datetime_col] >= test_start) & (df[datetime_col] <= test_end)].copy()

        # 15. Vérification de la taille des données d'entraînement
        if len(train_df) < 1000:
            raise ValueError("Pas assez de données pour entraîner le modèle.")

        # 16. Entraînement modèle Random Forest
        features = [col for col in train_df.columns if col not in [datetime_col, target_col]]
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(train_df[features], train_df[target_col])

        # 17. Prédictions sur la période test
        test_df['forecast'] = model.predict(test_df[features])

        # 18. Graphique interactif optionnel
        if plot_chart:
            y_true = test_df[target_col].values
            y_pred = test_df['forecast'].values
            mask = y_true != 0
            mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=test_df[datetime_col], y=test_df[target_col],
                mode='lines', name='Valeurs réelles', line=dict(color='blue')))
            fig.add_trace(go.Scatter(
                x=test_df[datetime_col], y=test_df['forecast'],
                mode='lines', name='Prévision', line=dict(color='red', dash='dash')))

            fig.update_layout(
                title=f'Prévision vs Réel — MAPE: {mape:.2f}%',
                xaxis_title='Date',
                yaxis_title=target_col,
                hovermode='x unified',
                template='plotly_white',
                plot_bgcolor='black',
                paper_bgcolor='black',
                font=dict(color='white'),
                legend=dict(x=0.01, y=0.99, font=dict(color='white')),
                xaxis=dict(color='white', gridcolor='gray'),
                yaxis=dict(color='white', gridcolor='gray'),
                margin=dict(t=100)
            )

            if save_path:
                fig.write_html(save_path)
                print(f"Graph saved as interactive HTML at: {save_path}")
            else:
                fig.show()

        # 19. Retourne les résultats
        return test_df[[datetime_col, target_col, 'forecast']]
