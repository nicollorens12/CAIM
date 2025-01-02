import matplotlib.pyplot as plt

# Datos de clusters y tiempos promedio por iteración
clusters = [2, 4, 8, 16]
average_times = [2.016, 2.07, 2.27, 2.79]  # Promedios calculados

# Crear la gráfica
plt.figure(figsize=(10, 6))
plt.plot(clusters, average_times, marker='o', label="Average Time per Iteration")

# Personalizar la gráfica
plt.title("Impacto del Número de Clusters en el Tiempo Promedio por Iteración", fontsize=14)
plt.xlabel("Número de Clusters", fontsize=12)
plt.ylabel("Tiempo Promedio por Iteración (segundos)", fontsize=12)
plt.xticks(clusters)
plt.grid(True)
plt.legend()

# Guardar la gráfica como un archivo PNG
output_file = "cluster_time_evolution.png"
plt.savefig(output_file)
print(f"Gráfica guardada como {output_file}")

