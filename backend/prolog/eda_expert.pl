% =================================================================
% SISTEMA EXPERTO EDA - REPRESENTACION DE CONOCIMIENTO (PROLOG)
% DATASET: SEATTLE WEATHER
% =================================================================

% 1. Representacion Objeto-Atributo-Valor
% atributo(Variable, Metrica, Valor).

% Metadatos de 'precipitation'
atributo(precipitation, asimetria, 3.45).
atributo(precipitation, ratio_outliers, 0.12).
atributo(precipitation, correlacion_max, 0.32).

% Metadatos de 'temp_max'
atributo(temp_max, asimetria, 0.15).
atributo(temp_max, ratio_outliers, 0.01).
atributo(temp_max, correlacion_max, 0.88).

% Metadatos de 'wind'
atributo(wind, asimetria, 0.85).
atributo(wind, ratio_outliers, 0.07).
atributo(wind, correlacion_max, 0.25).

% 2. Reglas de Inferencia (Conocimiento Estadistico)

es_sesgada(X) :- 
    atributo(X, asimetria, A), (A > 1.0 ; A < -1.0).

tiene_outliers(X) :- 
    atributo(X, ratio_outliers, R), R > 0.05.

alta_correlacion(X) :- 
    atributo(X, correlacion_max, C), C > 0.7.

% Inferencia de tecnicas
sugiere_tecnica(X, histograma_log) :- es_sesgada(X).
sugiere_tecnica(X, boxplot) :- tiene_outliers(X).
sugiere_tecnica(X, scatter_plot) :- alta_correlacion(X).

% 3. Consultas de ejemplo
% ?- sugiere_tecnica(precipitation, T).
% ?- alta_correlacion(temp_max).
% ?- tiene_outliers(wind).
