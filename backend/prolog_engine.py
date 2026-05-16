import subprocess
import os

class PrologEngine:
    @staticmethod
    def infer(metadata_list):
        """
        metadata_list: list of dicts like {'column': 'name', 'asimetria': 1.2, 'ratio_outliers': 0.08, 'max_corr': 0.5}
        """
        # 1. Generate OAV Facts
        facts = []
        for meta in metadata_list:
            col_name = "".join(x for x in meta['column'] if x.isalnum()).lower()
            facts.append(f"atributo({col_name}, asimetria, {meta.get('asimetria', 0.0)}).")
            facts.append(f"atributo({col_name}, ratio_outliers, {meta.get('ratio_outliers', 0.0)}).")
            facts.append(f"atributo({col_name}, correlacion_max, {meta.get('max_corr', 0.0)}).")
            facts.append(f"atributo({col_name}, ratio_nulos, {meta.get('ratio_nulos', 0.0)}).")
        
        facts_text = "\n".join(facts)
        
        # 2. Define Expert Rules (Numerical EDA logic)
        rules = """
% Reglas de Inferencia EDA Numérica
es_sesgada(X) :- atributo(X, asimetria, A), (A > 1.0 ; A < -1.0).
es_normal(X) :- atributo(X, asimetria, A), A > -0.5, A < 0.5.
tiene_outliers(X) :- atributo(X, ratio_outliers, R), R > 0.05.
alta_correlacion(X) :- atributo(X, correlacion_max, C), C > 0.7.

sugiere_tecnica(X, histograma_log) :- es_sesgada(X).
sugiere_tecnica(X, histograma_estandar) :- es_normal(X).
sugiere_tecnica(X, boxplot) :- tiene_outliers(X).
sugiere_tecnica(X, scatter_plot) :- alta_correlacion(X).
"""
        
        # Using a safer temp path for the workspace
        temp_file = "temp_prolog_rules.pl"
        try:
            with open(temp_file, "w") as f:
                f.write(facts_text + "\n" + rules)
            
            # 3. Execute Inferences via CLI
            query = "findall(suggestion(X, T), sugiere_tecnica(X, T), L), write(L), halt."
            
            result = subprocess.check_output(
                ["swipl", "-s", temp_file, "-g", query],
                stderr=subprocess.STDOUT,
                text=True
            )
            return {
                "success": True,
                "facts": facts_text,
                "inferences": result
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
