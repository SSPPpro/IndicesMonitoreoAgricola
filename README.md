# ArcPy-Tools: Índices de Vegetación y Agua para Imágenes Planet SuperDove

<p align="center">
  <img src="https://img.shields.io/badge/ArcGIS%20Pro-3.0%2B-blue.svg" alt="ArcGIS Pro Version">
  <img src="https://img.shields.io/badge/Python-3.x-blue.svg" alt="Python Version">
</p>

---

## 📄 Descripción General

Esta herramienta de geoprocesamiento para ArcGIS Pro permite el cálculo automatizado de varios índices de vegetación y agua a partir de imágenes satelitales **Planet SuperDove de 8 bandas**. Está diseñada específicamente para el monitoreo y análisis de plantaciones agrícolas, generando tanto rásteres de índices como su vectorización en polígonos, con atributos de metadatos útiles.

## ✨ Características Principales

*   **Cálculo de Múltiples Índices**: Calcula NDVI, GNDVI, NDWI, MSAVI, EVI y NDVI-RE.
*   **Procesamiento por Lotes**: Procesa todas las imágenes `.tif` compatibles dentro de una carpeta de entrada.
*   **Salidas Organizadas**: Genera una carpeta `idxs` dentro de cada directorio de imagen, conteniendo subcarpetas para cada índice ráster y una carpeta `vec` con los polígonos vectorizados.
*   **Vectorización y Atributos**: Reclasifica los rásteres de índices y los convierte a polígonos con campos adicionales para "carpeta", "fecha" e "índice", facilitando el análisis posterior.
*   **Fusión de Salidas**: Unifica todos los polígonos generados en una única capa de entidades (`.shp`) para una gestión y visualización centralizada.

## 🚀 Cómo Empezar

### Prerequisitos

*   **ArcGIS Pro**: Versión 3.0 o superior (compatible con ArcPy 3.x).
*   **Extensión Spatial Analyst**: Necesaria para las funciones de geoprocesamiento ráster.
*   **Imágenes Planet SuperDove**: La herramienta espera imágenes de 8 bandas (AnalyticMS_SR.tif).

### ⚙️ Instalación

1.  **Clona o Descarga el Repositorio**:
    ```bash
    git clone https://github.com/SSCR98/ArcPy-Tools.git
    ```
    O descarga el ZIP directamente desde GitHub.

2.  **Agrega la Caja de Herramientas a ArcGIS Pro**:
    *   Abre tu proyecto de ArcGIS Pro.
    *   En la ventana de **Catálogo**, navega hasta `Toolboxes`.
    *   Haz clic derecho en `Toolboxes` y selecciona `Add Toolbox...`.
    *   Navega hasta la ubicación donde guardaste el archivo `CalculateIndexes_Tool.pyt` y selecciónalo.

### 📝 Uso de la Herramienta

1.  Una vez que la caja de herramientas `Vegetation Indexes` esté agregada a tu proyecto, expándela.
2.  Haz doble clic en la herramienta `Calculate image vegetation indexes`.
3.  Aparecerá el cuadro de diálogo de la herramienta:
    *   **Images folder**: Navega y selecciona la carpeta que contiene todas tus imágenes Planet SuperDove (`.tif`). La herramienta buscará subcarpetas que contengan imágenes con el patrón `AnalyticMS_SR.tif`.
    *   **Ejemplo de estructura de carpetas de entrada**:
        ```
        your_input_folder/
        ├── image_set_1/
        │   └── 20230101_100000_AnalyticMS_SR.tif
        │   └── other_files.xml
        ├── image_set_2/
        │   └── 20230115_100000_AnalyticMS_SR.tif
        │   └── other_files.json
        └── ...
        ```
4.  Haz clic en `Run` para ejecutar la herramienta.

### 📊 Salida de la Herramienta

La herramienta creará la siguiente estructura de salida dentro de cada carpeta de imagen procesada, además de un archivo shapefile unificado en la carpeta raíz de entrada:
your_input_folder/
├── image_set_1/
│ └── 20230101_100000_AnalyticMS_SR.tif
│ └── idxs/
│ ├── ndvi/
│ │ └── NDVI.tif
│ ├── gndvi/
│ │ └── GNDVI.tif
│ ├── ndwi/
│ │ └── NDWI.tif
│ ├── msavi/
│ │ └── MSAVI.tif
│ ├── evi/
│ │ └── EVI.tif
│ ├── ndvi_re/
│ │ └── NDVI_RE.tif
│ └── vec/
│ ├── ndvi_1.shp
│ ├── gndvi_1.shp
│ └── ...
├── image_set_2/
│ └── ...
└── merged_indices_polygons.shp <-- Capa de polígonos unificada con todos los resultados.

Cada shapefile de polígonos contendrá los siguientes campos:

*   `gridcode`: Valor reclasificado del índice.
*   `carpeta`: Nombre de la carpeta padre de la imagen.
*   `fecha`: Fecha de adquisición de la imagen (extraída del nombre del archivo).
*   `indice`: Nombre del índice calculado (e.g., "ndvi", "gndvi").

