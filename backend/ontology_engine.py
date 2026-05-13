import os
import pandas as pd
from owlready2 import *


# Mapping of individual names to human-readable labels
INDIVIDUAL_LABELS = {
    "indBarrasVertical": "Gráfico de Barras Vertical",
    "indBarrasHorizontal": "Gráfico de Barras Horizontal",
    "indTortaPastel": "Gráfico de Torta / Pastel",
    "indFrecuenciaAcumulada": "Gráfico de Frecuencia Acumulada",
    "indTreemap": "Gráfico Treemap",
    "indAgruparMinoritarias": "Agrupar Categorías Minoritarias (<5%)",
    "indNoInformativa": "Columna no informativa para segmentación",
    "indAptoSegmentacion": "✓ Apta para segmentación",
    "indAlertaNulos": "⚠ Alerta: ratio de nulos >20%",
    "indAlertaDominante": "⚠ Alerta: categoría dominante >80%",
    "indDistBalanceada": "Distribución Balanceada",
    "indDistDesbalanceada": "Distribución Desbalanceada",
    "indDistMuyDesbalanceada": "Distribución Muy Desbalanceada",
    "indDistLevDesbalanceada": "Distribución Levemente Desbalanceada",
}

# Mapping of class names to human-readable labels
CLASS_LABELS = {
    "ColumnaBinaria": "Columna Binaria (2 categorías)",
    "ColumnaCardinalidadBaja": "Cardinalidad Baja (3–14 categorías)",
    "ColumnaCardinalidadMedia": "Cardinalidad Media",
    "ColumnaCardinalidadAlta": "Cardinalidad Alta (≥15 categorías)",
    "ColumnaCardinalidadMuyAlta": "Cardinalidad Muy Alta (ID-like)",
    "DistribucionBalanceada": "Distribución Balanceada",
    "DistribucionLevementeDesbalanceada": "Distribución Levemente Desbalanceada",
    "DistribucionDesbalanceada": "Distribución Desbalanceada",
    "DistribucionMuyDesbalanceada": "Distribución Muy Desbalanceada",
    "AlertaNulosAltos": "⚠ Alerta: Muchos valores nulos (>20%)",
    "AlertaCategoriaDominante": "⚠ Alerta: Categoría dominante (>80%)",
    "AptoParaSegmentacion": "✓ Apto para segmentación",
    "NoInformativaParaSegmentacion": "✗ No informativa para segmentación",
    "AgruparCategoriasMinoritarias": "Agrupar categorías minoritarias",
}

# Classes to suppress from profiles (internal/structural)
SUPPRESS_CLASSES = {
    "ColumnaCategorica", "DistribucionCategorica", "TecnicaVisualizacion",
    "Recomendacion", "Thing", "Nothing"
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

        # Detect categorical columns: object/category dtypes + low-cardinality numerics
        cat_cols = []
        for col in df.columns:
            if df[col].dtype in ["object", "category", "string"]:
                cat_cols.append(col)
            elif df[col].nunique() < 20:
                cat_cols.append(col)

        print(f"DEBUG: Columnas detectadas para analizar: {cat_cols}")
        if not cat_cols:
            return []

        ColumnaCategorica = self.onto.search_one(iri="*#ColumnaCategorica")
        if not ColumnaCategorica:
            raise Exception("Clase 'ColumnaCategorica' no encontrada en la ontologia")

        for col in cat_cols:
            try:
                cardinality = int(df[col].nunique())
                total = int(len(df[col]))
                ratio_nulos = float(df[col].isnull().mean())
                counts = df[col].value_counts(normalize=True)
                ratio_dominante = float(counts.iloc[0]) if not counts.empty else 0.0

                with self.onto:
                    safe_name = "".join(x for x in str(col) if x.isalnum()) or "unnamed"
                    ind_name = f"tmp_{safe_name}_{pd.Timestamp.now().strftime('%M%S%f')}"
                    ind = ColumnaCategorica(ind_name)
                    ind.tieneCardinalidad = [cardinality]
                    ind.tieneTotalRegistros = [total]
                    ind.tieneRatioDominante = [ratio_dominante]
                    ind.tieneRatioNulos = [ratio_nulos]

                analysis_results.append({
                    "column": str(col),
                    "cardinality": cardinality,
                    "ratio_dominante": ratio_dominante,
                    "ratio_nulos": ratio_nulos,
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
                    if hasattr(obj, "tieneNombre") and obj.tieneNombre:
                        return obj.tieneNombre[0]
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
            return "No hay datos categoricos para analizar."
        context = "=== Análisis EDA de Variables Categóricas ===\n\n"
        for res in results:
            context += f"Columna: '{res['column']}'\n"
            context += f"  Cardinalidad: {res['cardinality']} valores únicos\n"
            context += f"  Ratio dominante: {res['ratio_dominante']:.1%}\n"
            context += f"  Ratio nulos: {res['ratio_nulos']:.1%}\n"
            if res["profiles"]:
                context += f"  Perfiles: {', '.join(res['profiles'])}\n"
            if res["recommendations"]:
                context += f"  Técnicas sugeridas: {', '.join(res['recommendations'])}\n"
            context += "\n"
        return context
