# Pruebas a Realizar
- Probar con diferentes tamaños de vocabulario
    Genera datasets con vocabularios de tamaños diferentes (por ejemplo, 100 y 250 palabras). Analiza cómo estos tamaños afectan:
        - La calidad de los clusters.
        - El tiempo de ejecución.

- Variar el número de clusters (𝑘)
    Este es el parámetro principal que afecta los resultados de K-Means. Prueba con valores de 𝑘:
        - Número de carpetas (8).
        - Valores menores (𝑘 = 5, 6, 7) para agrupar temas más generales.
        - Valores mayores (𝑘 = 10, 12, 15) para desglosar subtemas.

- Impacto del número de cores (ncores)
    Cambia el número de núcleos (e.g., `--ncores 1`, `--ncores 2`, `--ncores 4`). Evalúa cómo afecta al tiempo de ejecución y, opcionalmente, a la calidad.

- Número de iteraciones (iter)
    Experimenta con valores como 5, 10 y 15 iteraciones para ver si un mayor número mejora la calidad de los clusters.

## Probar con diferentes tamaños de vocabulario

Hemos modificado `ExtractData.py` para que de los `.txt` de outputs dependientes de `numwords` así podemos en paralelo ir haciendo diferentes pruebas.

Generar vocabularios con diferentes configuraciones:

```bash
python ExtractData.py --index arxiv_abs_index --minfreq 0.01 --maxfreq 0.5 --numwords 100
python ExtractData.py --index arxiv_abs_index --minfreq 0.05 --maxfreq 0.3 --numwords 250
```

```bash
python GeneratePrototypes.py --data documents_100.txt --nclust 8
python GeneratePrototypes.py --data documents_250.txt --nclust 8
```

```bash
python MRKMeans.py --ncores 2 --iter 10 --protprototypes_100.txt --docs documents_100.txt
python MRKMeans.py --ncores 2 --iter 10 --protprototypes_250.txt --docs documents_250.txt
```



