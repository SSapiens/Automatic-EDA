% =================================================================
% SISTEMA EXPERTO EDA - REPRESENTACION DE CONOCIMIENTO (PROLOG)
% =================================================================

% 1. Representacion Objeto-Atributo-Valor (Metadatos de flight_price.csv - 1000 registros)
% Formato: atributo(Objeto, Atributo, Valor).

% Metadatos de la columna 'airline'
atributo(airline, cardinalidad, 6).
atributo(airline, ratio_nulos, 0.0).
atributo(airline, ratio_dominante, 0.40).

% Metadatos de la columna 'source_city' (Solo Delhi)
atributo(source_city, cardinalidad, 1).
atributo(source_city, ratio_nulos, 0.0).
atributo(source_city, ratio_dominante, 1.0).

% Metadatos de la columna 'destination_city' (Solo Mumbai)
atributo(destination_city, cardinalidad, 1).
atributo(destination_city, ratio_nulos, 0.0).
atributo(destination_city, ratio_dominante, 1.0).

% Metadatos de la columna 'class' (Solo Economy)
atributo(class, cardinalidad, 1).
atributo(class, ratio_nulos, 0.0).
atributo(class, ratio_dominante, 1.0).

% Metadatos de la columna 'stops'
atributo(stops, cardinalidad, 3).
atributo(stops, ratio_nulos, 0.0).
atributo(stops, ratio_dominante, 0.85).

% 2. Proposiciones y Reglas de Inferencia (Conocimiento Experto)

% Clasificacion de Columnas
es_unaria(X) :- 
    atributo(X, cardinalidad, 1).

es_binaria(X) :- 
    atributo(X, cardinalidad, 2).

es_cardinalidad_baja(X) :- 
    atributo(X, cardinalidad, N), N > 2, N =< 5.

es_cardinalidad_media(X) :- 
    atributo(X, cardinalidad, N), N > 5, N =< 15.

es_cardinalidad_alta(X) :- 
    atributo(X, cardinalidad, N), N > 15.

es_desbalanceada(X) :- 
    atributo(X, ratio_dominante, R), R > 0.8.

% Recomendacion de Tecnicas
sugiere_tecnica(X, torta_pastel) :- 
    es_binaria(X).

sugiere_tecnica(X, barras_vertical) :- 
    es_cardinalidad_baja(X).

sugiere_tecnica(X, barras_horizontal) :- 
    es_cardinalidad_media(X).

sugiere_tecnica(X, treemap) :- 
    es_cardinalidad_alta(X).

recomienda_agrupar(X) :- 
    es_cardinalidad_alta(X).

% 3. Ejemplos de Consultas (Inferencias)
% ?- sugiere_tecnica(airline, T).
% ?- es_desbalanceada(source_city).
% ?- sugiere_tecnica(X, barras_horizontal).
