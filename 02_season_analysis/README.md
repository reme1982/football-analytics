# Análisis de Temporada con SQL — Premier League 2015/16

Análisis estadístico de la temporada completa usando una base de datos **SQLite** con 1.3 millones de eventos de los 380 partidos de la Premier League 2015/16.

---

## Resumen Ejecutivo

### Hallazgos principales

**1. Arsenal lideró en posesión, Tottenham en tiros**
Arsenal fue el equipo con más pases de la temporada (22,709), seguido de Manchester City (22,340). Sin embargo, Tottenham fue el equipo más amenazante con 656 tiros totales, superando a Liverpool (635) y Manchester City (614).

**2. Liverpool fue el equipo que más presionó**
Con 6,540 acciones de presión, Liverpool lideró ampliamente esta métrica — coherente con el estilo de Klopp que llegó en octubre de 2015. Este dato explica en parte por qué fueron tan efectivos en partidos clave como el 4-1 ante Manchester City.

**3. Harry Kane fue el máximo goleador**
Con 25 goles, Kane lideró la tabla de anotadores de la temporada en los datos de StatsBomb, seguido de Jamie Vardy (Leicester City) cuya temporada histórica le llevó al título.

**4. El xG confirma la sorpresa de Leicester**
Leicester City ganó la liga con un xG modesto comparado con Arsenal o Manchester City, lo que indica que fueron muy eficientes de cara al gol — convirtieron más de lo esperado estadísticamente.

**5. Partidos más goleadores**
Los encuentros con más goles de la temporada muestran que los equipos recién ascendidos (AFC Bournemouth, Watford) tendieron a protagonizar los marcadores más abultados.

---

## Visualizaciones

### Top 10 Goleadores
![Goleadores](graficos/sql_01_goleadores.png)

### xG vs Goles Reales por Equipo
![xG por equipo](graficos/sql_02_xg_equipos.png)

### Ranking de Equipos por Tipo de Evento
![Ranking eventos](graficos/sql_03_ranking_equipos.png)

### Top 10 Partidos con Más Goles
![Partidos goles](graficos/sql_04_partidos_mas_goles.png)

---

## Estructura de la Base de Datos

| Tabla | Filas | Descripción |
|---|---|---|
| `matches` | 380 | Info de cada partido (equipos, resultado, fecha) |
| `events` | 1,313,783 | Todos los eventos de la temporada (pases, tiros, presiones, etc.) |
| `shots` | 9,908 | Solo tiros con xG, coordenadas x/y |

### Ejemplo de consulta SQL

```sql
-- Top 10 goleadores de la temporada
SELECT player, team, COUNT(*) AS goles
FROM shots
WHERE shot_outcome = 'Goal'
GROUP BY player, team
ORDER BY goles DESC
LIMIT 10;
```

---

## Tecnologías

- **Python 3** + **SQLite3** — base de datos local
- **statsbombpy** — descarga de datos abiertos
- **pandas** — manipulación y consultas
- **matplotlib** — visualizaciones

## Cómo ejecutar

```bash
pip install statsbombpy pandas matplotlib jupyter
jupyter notebook Season_Analysis_SQL.ipynb
```

> **Nota:** La base de datos `.db` no está incluida en el repositorio por su tamaño (139 MB).
> Se genera automáticamente al ejecutar los pasos 3-5 del notebook.
> La descarga de los 380 partidos tarda aproximadamente 5-10 minutos.

---

## Fuente de datos

[StatsBomb Open Data](https://github.com/statsbomb/open-data) — datos de uso libre para educación e investigación.
