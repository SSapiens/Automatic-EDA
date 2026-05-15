import subprocess
import os

class PrologEngine:
    @staticmethod
    def infer(metadata_list):
        """
        metadata_list: list of dicts like {'column': 'name', 'cardinality': 5, 'ratio_dominante': 0.4, ...}
        """
        # 1. Generate OAV Facts
        facts = []
        for meta in metadata_list:
            col_name = "".join(x for x in meta['column'] if x.isalnum()).lower()
            facts.append(f"atributo({col_name}, cardinalidad, {meta['cardinality']}).")
            facts.append(f"atributo({col_name}, ratio_dominante, {meta['ratio_dominante']}).")
            facts.append(f"atributo({col_name}, ratio_nulos, {meta['ratio_nulos']}).")
        
        facts_text = "\n".join(facts)
        
        # 2. Define Expert Rules (Hardcoded for the demo to be robust)
        rules = """
% Reglas de Inferencia EDA
es_binaria(X) :- atributo(X, cardinalidad, 2).
es_card_baja(X) :- atributo(X, cardinalidad, N), N > 2, N =< 5.
es_card_media(X) :- atributo(X, cardinalidad, N), N > 5, N =< 15.
es_card_alta(X) :- atributo(X, cardinalidad, N), N > 15.
es_desbalanceada(X) :- atributo(X, ratio_dominante, R), R > 0.8.

sugiere_tecnica(X, torta_pastel) :- es_binaria(X).
sugiere_tecnica(X, barras_vertical) :- es_card_baja(X).
sugiere_tecnica(X, barras_horizontal) :- es_card_media(X).
sugiere_tecnica(X, treemap) :- es_card_alta(X).
"""
        
        temp_file = "/tmp/demo_prolog.pl"
        with open(temp_file, "w") as f:
            f.write(facts_text + "\n" + rules)
        
        # 3. Execute Inferences via CLI
        # Query: Get all suggestions
        query = "findall(suggestion(X, T), sugiere_tecnica(X, T), L), write(L), halt."
        
        try:
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
