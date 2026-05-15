import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.preprocessing import LabelEncoder
from mlxtend.frequent_patterns import apriori, association_rules

class MLEngine:
    @staticmethod
    def extract_rules(df, target_column):
        try:
            # 1. Decision Tree Classification
            # Prepare features (all categorical columns except target)
            cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            features = [c for c in cat_cols if c != target_column]
            
            if not features:
                # If no other cat cols, try to use high-cardinality numerics or just all others
                features = [c for c in df.columns if c != target_column]
            
            # Label encoding for tree
            le = LabelEncoder()
            X = df[features].copy()
            for col in X.columns:
                X[col] = le.fit_transform(X[col].astype(str))
            
            y = le.fit_transform(df[target_column].astype(str))
            target_names = le.classes_.tolist()

            clf = DecisionTreeClassifier(max_depth=4, min_samples_leaf=5)
            clf.fit(X, y)
            
            tree_text = export_text(clf, feature_names=features)
            
            # 2. Association Rules
            # Get dummies for categorical columns
            df_assoc = df[cat_cols].copy()
            df_dummies = pd.get_dummies(df_assoc)
            
            frequent_itemsets = apriori(df_dummies, min_support=0.1, use_colnames=True)
            assoc_rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.6)
            
            # Format association rules for display
            rules_list = []
            for _, row in assoc_rules.head(10).iterrows():
                ant = list(row['antecedents'])
                con = list(row['consequents'])
                rules_list.append(f"IF {ant} THEN {con} (Conf: {row['confidence']:.2f})")

            return {
                "success": True,
                "tree": tree_text,
                "target_names": target_names,
                "association_rules": rules_list
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
