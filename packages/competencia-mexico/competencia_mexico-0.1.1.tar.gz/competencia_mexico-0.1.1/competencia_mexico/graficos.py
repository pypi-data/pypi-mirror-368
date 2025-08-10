# graficos.py (por ejemplo, dentro de tu paquete)

def graficar_y_resumir_asuntos_interactiva():
    """
    Lee 'estadisticas_final.csv' incluido en el paquete y lanza
    un flujo interactivo para graficar y resumir asuntos por mes/año,
    filtrando por Rubro y, opcionalmente, por tipo de Decisión.

    Requiere que el CSV tenga las columnas:
    ['FechaResolucion', 'Rubro', 'Decision'].
    """
    # 1) Cargar el CSV empacado
    import pandas as pd
    import matplotlib.pyplot as plt
    df = _cargar_csv_empaquetado("estadisticas_final.csv")

    # 2) Validar columnas necesarias
    for col in ['FechaResolucion', 'Rubro', 'Decision']:
        if col not in df.columns:
            raise ValueError(f"Falta la columna requerida: '{col}'")

    # 3) Asegurar formato de fecha
    df = df.copy()
    df["FechaResolucion"] = pd.to_datetime(df["FechaResolucion"], errors="coerce")

    # 4) Opciones de rubro
    rubros_disponibles = df["Rubro"].dropna().astype(str).str.upper().unique().tolist()
    print("\n📊 GRAFICADOR DE ASUNTOS")
    print("-------------------------")
    print("Rubros disponibles:", ', '.join(sorted(rubros_disponibles)))

    # 5) Inputs
    rubro = input("\n👉 ¿Qué rubro quieres graficar? (Ej. DE, IO, OPN): ").strip().upper()
    if rubro not in rubros_disponibles:
        raise ValueError(f"El rubro '{rubro}' no está en los datos.")

    desagregacion = input("📆 ¿Quieres agrupar por mes o por año? [mes/año]: ").strip().lower()
    if desagregacion not in ["mes", "año"]:
        raise ValueError("Debes escribir 'mes' o 'año'.")

    por_decision = input("📌 ¿Quieres desglosar por tipo de decisión? [s/n]: ").strip().lower()
    if por_decision not in ["s", "n"]:
        raise ValueError("Responde 's' para sí o 'n' para no.")
    por_decision = (por_decision == "s")

    # 6) Filtrar por rubro y fechas válidas
    df = df[df["Rubro"].astype(str).str.upper() == rubro]
    df = df.dropna(subset=["FechaResolucion"])

    # 7) Crear columna Periodo
    if desagregacion == "mes":
        df["Periodo"] = df["FechaResolucion"].dt.to_period("M").astype(str)
    else:
        df["Periodo"] = df["FechaResolucion"].dt.year

    # 8) Agrupar y graficar
    if por_decision:
        resumen = df.groupby(["Periodo", "Decision"]).size().unstack(fill_value=0)
        resumen.plot(kind="bar", stacked=True, figsize=(12, 6))
        plt.title(f"Asuntos por {desagregacion} (Rubro '{rubro}') desglosados por decisión")
    else:
        resumen = df["Periodo"].value_counts().sort_index()
        resumen.plot(kind="bar", figsize=(10, 5))
        plt.title(f"Asuntos por {desagregacion} (Rubro '{rubro}')")

    # 9) Ajustes estéticos
    plt.xlabel("Periodo")
    plt.ylabel("Número de asuntos")
    ax = plt.gca()
    xticklabels = ax.get_xticklabels()
    N = 3  # Muestra 1 de cada N etiquetas para evitar saturación
    for i, label in enumerate(xticklabels):
        label.set_visible(i % N == 0)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # 10) Tabla resumen
    print("\n📋 Tabla resumen:")
    resumen_final = (resumen.reset_index().rename(columns={0: "Total"})
                     if not por_decision else resumen.reset_index())

    # display() está disponible en notebooks; si no, imprime head
    try:
        display(resumen_final)
    except NameError:
        print(resumen_final.head(20).to_string(index=False))

    return resumen_final


def _cargar_csv_empaquetado(nombre_archivo):
    """
    Carga un CSV ubicado en competencia_tools/data/<nombre_archivo>
    usando importlib.resources. Devuelve un DataFrame.
    """
    # Python 3.9+: importlib.resources.files
    try:
        from importlib.resources import files
        data_path = files('competencia_tools.data').joinpath(nombre_archivo)
        return pd.read_csv(data_path)
    except Exception:
        # Fallback para entornos más viejos
        import pkgutil, io
        raw = pkgutil.get_data('competencia_tools.data', nombre_archivo)
        if raw is None:
            raise FileNotFoundError(
                f"No se encontró '{nombre_archivo}' dentro de competencia_tools/data."
            )
        return pd.read_csv(io.BytesIO(raw))
