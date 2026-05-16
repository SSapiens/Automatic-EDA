import os
import pandas as pd
import numpy as np
from owlready2 import *


# Mapping of individual names to human-readable labels
INDIVIDUAL_LABELS = {
    "indHistograma": "Histograma de Frecuencias",
    "indHistogramaEst": "Histograma Estándar (Distribución Normal)",
    "indHistogramaLog": "Histograma con Transformación Logarítmica",
    "indBoxPlot": "Diagrama de Caja (BoxPlot)",
    "indViolinPlot": "Diagrama de Violín",
    "indScatterPlot": "Gráfico de Dispersión (Relacional)",
    "indPearson": "Cálculo de Correlación de Pearson",
    "indZScore": "Detección de Outliers (Z-Score)",
    "indIQR": "Detección de Outliers (Rango Intercuartílico)",
    "indNoInformativa": "Variable con baja varianza / No informativa",
}

# Mapping of class names to human-readable labels
CLASS_LABELS = {
    "ColumnaAsimetrica": "Distribución Asimétrica (Sesgada)",
    "ColumnaConOutliers": "Presencia Significativa de Outliers (>5%)",
    "DistribucionNormal": "Distribución Aproximadamente Normal",
    "ColumnaNumerica": "Variable Numérica Continua",
    "ParDeColumnasCorrelacionadas": "Alta Correlación Detectada (>0.7)",
}

# Classes to suppress from profiles (internal/structural)
SUPPRESS_CLASSES = {
    "ColumnaCategorica", "DistribucionCategorica", "TecnicaVisualizacion",
    "Recomendacion", "Thing", "Nothing", "ColumnaNumerica"
}


class OntologyEngine:
    def __init__(self, ontology_path):
        self.ontology_path = ontology_path
        self.onto = None
        self.load_ontology()

    def load_ontology(self):
        try:
            path = self.ontology_path
            # Support .owx or .owl
            if not os.path.exists(path):
                alt_path = path.replace(".owx", ".owl")
                if os.path.exists(alt_path):
                    path = alt_path

            print(f"DEBUG: Cargando ontologia desde {path}")
            self.onto = get_ontology(f"file://{path}").load()
            print(f"DEBUG: Ontologia cargada. IRI base: {self.onto.base_iri}")
        except Exception as e:
            print(f"ERROR: No se pudo cargar la ontologia: {str(e)}")
            raise e

    def analyze_csv(self, df):
        analysis_results = []

        # Detect numerical columns
        num_cols = []
        for col in df.columns:
            # Skip index-like columns or Unnamed columns
            if "Unnamed" in str(col) or str(col).lower() == "id":
                continue
            if df[col].dtype in [np.number, "float64", "int64"]:
                num_cols.append(col)
        
        print(f"DEBUG: Columnas numéricas detectadas para analizar: {num_cols}")
        if not num_cols:
            return []

        ColumnaNumerica = self.onto.search_one(iri="*#ColumnaNumerica")
        if not ColumnaNumerica:
            # Fallback if class name changed or root is generic
            ColumnaNumerica = self.onto.search_one(iri="*#ColumnaCategorica") or self.onto.Thing

        # Calculate correlation matrix once
        corr_matrix = df[num_cols].corr().abs()

        for col in num_cols:
            try:
                data = df[col].dropna()
                if data.empty: continue

                asimetria = float(data.skew()) if len(data) > 2 else 0.0
                curtosis = float(data.kurt()) if len(data) > 2 else 0.0
                ratio_nulos = float(df[col].isnull().mean())
                
                # IQR Outlier Detection
                q1 = data.quantile(0.25)
                q3 = data.quantile(0.75)
                iqr = q3 - q1
                outliers_count = ((data < (q1 - 1.5 * iqr)) | (data > (q3 + 1.5 * iqr))).sum()
                ratio_outliers = float(outliers_count / len(data)) if len(data) > 0 else 0.0

                # Max Correlation and the name of the column
                if len(num_cols) > 1:
                    corrs = corr_matrix[col].drop(col)
                    max_corr = float(corrs.max())
                    max_corr_col = str(corrs.idxmax())
                else:
                    max_corr = 0.0
                    max_corr_col = "N/A"

                with self.onto:
                    safe_name = "".join(x for x in str(col) if x.isalnum()) or "unnamed"
                    ind_name = f"num_{safe_name}_{pd.Timestamp.now().strftime('%M%S%f')}"
                    ind = ColumnaNumerica(ind_name)
                    ind.tieneAsimetria = asimetria
                    ind.tieneRatioOutliers = ratio_outliers
                    ind.tieneRatioNulos = ratio_nulos
                    ind.tieneCorrelacionMaxima = max_corr

                analysis_results.append({
                    "column": str(col),
                    "asimetria": asimetria,
                    "ratio_outliers": ratio_outliers,
                    "ratio_nulos": ratio_nulos,
                    "max_corr": max_corr,
                    "max_corr_col": max_corr_col,
                    "individual_name": ind_name,
                })
            except Exception as e:
                print(f"ERROR: Procesando {col}: {str(e)}")
                continue

        if not analysis_results:
            return []

        # Run Pellet — the OWL DL EquivalentClasses drive all classification
        print("DEBUG: Ejecutando razonador Pellet...")
        try:
            sync_reasoner_pellet(infer_property_values=True)
            print("DEBUG: Razonamiento completado.")
        except Exception as e:
            print(f"ERROR: Razonador Pellet: {str(e)}")

        # Collect inferences from the reasoner's output
        final_results = []
        for res in analysis_results:
            try:
                ind = self.onto[res["individual_name"]]
                if not ind:
                    print(f"WARNING: Individuo {res['individual_name']} no encontrado post-razonamiento")
                    continue

                # Profiles: all inferred classes except internal structural ones
                profiles = []
                for cls in ind.is_a:
                    if hasattr(cls, "name") and cls.name not in SUPPRESS_CLASSES:
                        label = CLASS_LABELS.get(cls.name, cls.name)
                        profiles.append(label)

                # Recommendations: inferred object properties
                recommendations = []
                def resolve_name(obj):
                    if hasattr(obj, "name"):
                        return INDIVIDUAL_LABELS.get(obj.name, obj.name)
                    return str(obj)

                for tech in getattr(ind, "sugiereTecnica", []):
                    recommendations.append(resolve_name(tech))
                for rec in getattr(ind, "tieneRecomendacion", []):
                    recommendations.append(resolve_name(rec))

                final_results.append({
                    **res,
                    "profiles": list(set(profiles)),
                    "recommendations": list(set(recommendations)),
                })
            except Exception as e:
                print(f"ERROR: Recuperando inferencias para {res['column']}: {str(e)}")

        return final_results

    def get_knowledge_context(self, results):
        if not results:
            return "No hay datos numéricos para analizar."
        context = "=== Análisis EDA de Variables Numéricas ===\n\n"
        for res in results:
            context += f"Columna: '{res['column']}'\n"
            context += f"  Asimetría: {res['asimetria']:.2f}\n"
            context += f"  Outliers: {res['ratio_outliers']:.1%}\n"
            context += f"  Máx Correlación: {res['max_corr']:.2f}\n"
            if res["profiles"]:
                context += f"  Perfiles: {', '.join(res['profiles'])}\n"
            if res["recommendations"]:
                context += f"  Técnicas sugeridas: {', '.join(res['recommendations'])}\n"
            context += "\n"
        return context
