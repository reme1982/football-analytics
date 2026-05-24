# Football Analytics con StatsBomb

Análisis interactivo de datos de fútbol usando datos abiertos de **StatsBomb** y Python.  
El proyecto analiza en profundidad el partido **Manchester City 1 – 4 Liverpool** (Premier League, 21 Nov 2015).

---

## Visualizaciones

### Tarjeta Resumen del Partido
![Resumen](graficos/paso_57_resumen_partido.png)

### xG vs Goles Reales
![xG](graficos/paso_51_xg.png)

### Mapa de Tiros
![Mapa de Tiros](graficos/paso_52_mapa_tiros.png)

### Mapa de Calor de Pases
![Heatmap Pases](graficos/paso_53_heatmap_pases.png)

### Red de Pases
![Red de Pases](graficos/paso_54_red_pases.png)

### Evolución del Partido por Minuto
![Evolución](graficos/paso_55_evolucion_partido.png)

### Top 5 Jugadores por Métrica
![Top Jugadores](graficos/paso_56_top_jugadores.png)

---

## Métricas analizadas (por equipo)

| Métrica | Manchester City | Liverpool |
|---|---|---|
| Total Pases | 610 | 417 |
| Precisión de Pase | 74.4% | 70.7% |
| Tiros | 12 | 14 |
| Tiros a Puerta | 1 | 3 |
| Posesión | 55.5% | 44.5% |
| Recuperos de Balón | 197 | 291 |
| Duelos Ganados | 3 | 4 |
| Intercepciones | 4 | 5 |
| Faltas Cometidas | 11 | 13 |
| xG | 0.90 | 3.25 |

---

## Tecnologías

- **Python 3**
- **statsbombpy** — acceso a datos abiertos de StatsBomb
- **pandas** — manipulación de datos
- **matplotlib** — gráficos estáticos
- **mplsoccer** — visualizaciones sobre campo de fútbol
- **Jupyter Notebook**

## Cómo ejecutar

```bash
pip install statsbombpy mplsoccer pandas matplotlib jupyter
jupyter notebook Analisis_StatsBomb.ipynb
```

Ejecuta las celdas en orden de arriba hacia abajo. Los gráficos se guardan automáticamente en la carpeta `graficos/`.

---

## Fuente de datos

[StatsBomb Open Data](https://github.com/statsbomb/open-data) — datos de uso libre para educación e investigación.