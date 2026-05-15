from owlready2 import *

def generate_sqwrl_onto():
    onto = get_ontology("http://www.semanticweb.org/eda/ontologies/sqwrl_queries")
    
    # Importar la ontología base (demo_experto_eda.owx)
    # Nota: Para Protégé esto funciona mejor si el archivo está en la misma carpeta
    
    with onto:
        class ColumnaCategorica(Thing): pass
        class tieneCardinalidad(DataProperty): range = [int]
        class tieneRatioDominante(DataProperty): range = [float]
        class sugiereTecnica(ObjectProperty): pass
        
        # Definir las queries SQWRL como reglas con cabeza sqwrl:select
        # Debido a las limitaciones de Owlready2 para guardar built-ins de SQWRL directamente,
        # generaremos el XML manualmente o usaremos comentarios para que el usuario las copie.
        
        # Sin embargo, intentaremos el formato estandar:
        rules = [
            ("Q01_ListarBinarias", "ColumnaCategorica(?c), tieneCardinalidad(?c, 2) -> sqwrl:select(?c)"),
            ("Q02_SugerirTreemap", "ColumnaCategorica(?c), tieneCardinalidad(?c, ?n), swrlb:greaterThan(?n, 15) -> sqwrl:select(?c)"),
            ("Q03_Desbalanceadas", "ColumnaCategorica(?c), tieneRatioDominante(?c, ?r), swrlb:greaterThan(?r, 0.8) -> sqwrl:select(?c)")
        ]
        
        # Guardaremos esto en un TXT para que el usuario sepa qué pegar en la pestaña SQWRL de Protégé
        # ya que el guardado directo de SQWRL en OWL desde Owlready2 es propenso a errores de esquema.
        
    query_text = "=== CONSULTAS SQWRL PARA PROTEGE ===\n\n"
    query_text += "Copia estas consultas en la pestaña 'SQWRLTab' de Protégé:\n\n"
    for name, rule in rules:
        query_text += f"--- {name} ---\n{rule}\n\n"
        
    with open('ontology/sqwrl_queries.txt', 'w') as f:
        f.write(query_text)
    
    print("[OK] Consultas SQWRL guardadas en ontology/sqwrl_queries.txt")

if __name__ == "__main__":
    generate_sqwrl_onto()
