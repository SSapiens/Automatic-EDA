import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.preprocessing import LabelEncoder
try:
    from mlxtend.frequent_patterns import apriori, association_rules
except ImportError:
    print("Nota: mlxtend no instalado. Saltando reglas de asociación.")

def run_ml_pipeline():
    # 1. Carga de datos
    df = pd.read_csv('data/flight_price.csv')
    
    # 2. Preprocesamiento simple para el árbol
    # Variables de interés: airline, source_city, stops, class
    le = LabelEncoder()
    df_tree = df[['airline', 'source_city', 'stops', 'class']].copy()
    for col in df_tree.columns:
        df_tree[col] = le.fit_transform(df_tree[col])
    
    # Target: Binning del precio (Bajo, Medio, Alto)
    df['price_range'] = pd.qcut(df['price'], q=3, labels=['Low', 'Medium', 'High'])
    y = le.fit_transform(df['price_range'])
    
    # 3. Entrenamiento de Árbol de Decisión
    clf = DecisionTreeClassifier(max_depth=3)
    clf.fit(df_tree, y)
    
    tree_rules = export_text(clf, feature_names=list(df_tree.columns))
    
    print("--- Reglas del Árbol de Decisión ---")
    print(tree_rules)
    
    # 4. Reglas de Asociación (Apriori)
    # Solo columnas categóricas
    df_assoc = df[['airline', 'source_city', 'departure_time', 'stops', 'destination_city', 'class']]
    df_dummies = pd.get_dummies(df_assoc)
    
    output_text = "=== REGLAS EXTRAIDAS DEL DATASET FLIGHT_PRICE ===\n\n"
    output_text += "1. REGLAS DE CLASIFICACION (ARBOL DE DECISION)\n"
    output_text += "Objetivo: Predecir rango de precio (Low/Medium/High)\n"
    output_text += tree_rules + "\n\n"
    
    try:
        frequent_itemsets = apriori(df_dummies, min_support=0.1, use_colnames=True)
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.7)
        
        output_text += "2. REGLAS DE ASOCIACION (APRIORI)\n"
        for _, row in rules.iterrows():
            ant = list(row['antecedents'])
            con = list(row['consequents'])
            output_text += f"IF {ant} THEN {con} (Conf: {row['confidence']:.2f}, Supp: {row['support']:.2f})\n"
    except NameError:
        output_text += "2. REGLAS DE ASOCIACION (No ejecutado - falta mlxtend)\n"

    with open('ml/reglas_extraidas.txt', 'w') as f:
        f.write(output_text)
    
    print("\n[OK] Reglas guardadas en ml/reglas_extraidas.txt")

if __name__ == "__main__":
    run_ml_pipeline()
