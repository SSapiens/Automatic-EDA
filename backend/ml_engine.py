import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.preprocessing import LabelEncoder

class MLEngine:
    @staticmethod
    def extract_rules(df, target_column):
        try:
            # 1. Decision Tree Classification (Numerical features)
            # Use numerical columns for the tree
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            features = [c for c in num_cols if c != target_column]
            
            if not features:
                # Fallback to categorical if no numerical features
                features = [c for c in df.columns if c != target_column]
            
            # Label encode target if it's categorical
            le_target = LabelEncoder()
            y = le_target.fit_transform(df[target_column].astype(str))
            target_names = le_target.classes_.tolist()

            # Prepare X (numerical)
            X = df[features].copy()
            # Handle non-numerical features in X if any
            for col in X.columns:
                if X[col].dtype == object:
                    X[col] = LabelEncoder().fit_transform(X[col].astype(str))
                else:
                    X[col] = X[col].fillna(X[col].mean())

            clf = DecisionTreeClassifier(max_depth=3, min_samples_leaf=10)
            clf.fit(X, y)
            
            tree_text = export_text(clf, feature_names=features)
            
            # 2. Correlation-based Association Rules (Numerical)
            corr_matrix = df[num_cols].corr()
            assoc_rules = []
            
            # Find pairs with high correlation (> 0.7)
            for i in range(len(num_cols)):
                for j in range(i + 1, len(num_cols)):
                    col_a = num_cols[i]
                    col_b = num_cols[j]
                    val = corr_matrix.loc[col_a, col_b]
                    if abs(val) > 0.7:
                        assoc_rules.append(f"DEPENDENCIA: {col_a} <-> {col_b} (Pearson: {val:.2f})")

            return {
                "success": True,
                "tree": tree_text,
                "target_names": target_names,
                "association_rules": assoc_rules[:10]  # Show top 10 correlations
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
