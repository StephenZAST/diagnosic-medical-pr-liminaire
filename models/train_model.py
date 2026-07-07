# Script d'entraînement du modèle ML
# Ce script prépare et entraîne le modèle de prédiction des maladies

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
import json

def load_training_data(filepath):
    """Charge les données d'entraînement"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return pd.DataFrame(data)

def prepare_data():
    """Prépare les données pour l'entraînement"""
    print("Chargement des données...")
    df = load_training_data('data/symptoms_diseases.json')
    
    # Préparation des features et labels
    X = df['symptom'].values
    y = df['disease'].values
    
    return X, y

def train_model(X, y):
    """Entraîne le modèle de classification"""
    print("Entraînement du modèle...")
    
    # Pipeline: TF-IDF + Naive Bayes
    model = Pipeline([
        ('tfidf', TfidfVectorizer(analyzer='char', ngram_range=(2, 3))),
        ('classifier', MultinomialNB())
    ])
    
    model.fit(X, y)
    
    print(f"Modèle entraîné avec {len(y)} exemples")
    return model

def save_model(model, filepath):
    """Sauvegarde le modèle"""
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)
    print(f"Modèle sauvegardé à {filepath}")

def main():
    """Fonction principale"""
    # Préparer les données
    X, y = prepare_data()
    
    # Entraîner le modèle
    model = train_model(X, y)
    
    # Sauvegarder
    save_model(model, 'models/disease_predictor.pkl')
    
    # Test simple
    test_symptoms = ['fièvre et toux']
    predictions = model.predict(test_symptoms)
    probabilities = model.predict_proba(test_symptoms)
    
    print(f"\nTest: '{test_symptoms[0]}'")
    print(f"Prédiction: {predictions[0]}")
    print(f"Confiance: {max(probabilities[0]):.2%}")

if __name__ == '__main__':
    main()
