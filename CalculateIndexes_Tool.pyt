# -*- coding: utf-8 -*-
import arcpy
import os
import shutil
from arcpy.sa import *
from arcpy.ia import *

class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = "Vegetation Indexes"
        self.alias = "Vegetation_Indexes" # Alias mejorado para evitar espacios
        # List of tool classes associated with this toolbox
        self.tools = [CalculateIndexes]

class CalculateIndexes:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Calculate image vegetation and water indexes" # Descripción más completa
        self.description = "Geoprocessing tool to calculate several vegetation and water-related indexes for a given set of Planet SuperDove 8-band images. Generates raster indexes and their vectorized polygons."
        self.canRunInBackground = True # Permite que la herramienta se ejecute en segundo plano

    def getParameterInfo(self):
        """Define the tool parameters."""
        in_folder = arcpy.Parameter(
            displayName="Input Images Folder",
            name="in_folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input",
            # filter={
            #     'list': ['Folder'] # No es necesario para DEFolder, pero un ejemplo si fuera FeatureClass
            # }
        )
        
        # Parámetro para la carpeta de salida, opcional para mayor flexibilidad
        out_folder = arcpy.Parameter(
            displayName="Output Folder (Optional, defaults to input folder)",
            name="out_folder",
            datatype="DEFolder",
            parameterType="Optional",
            direction="Input",
        )
        
        # Parámetro para la licencia de Spatial Analyst
        spatial_analyst_licensed = arcpy.Parameter(
            displayName="Spatial Analyst License Available",
            name="spatial_analyst_licensed",
            datatype="GPBoolean",
            parameterType="Derived", # Este parámetro es solo informativo, no lo establece el usuario
            direction="Output",
            multiValue=False
        )

        params = [in_folder, out_folder, spatial_analyst_licensed]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        # Verificar la licencia de Spatial Analyst
        if arcpy.CheckExtension("Spatial") == "Available":
            arcpy.CheckOutExtension("Spatial")
            return True
        else:
            arcpy.AddError("Spatial Analyst extension is not licensed. This tool requires Spatial Analyst.")
            return False

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed. This method is called whenever a parameter has been changed."""
        # Establecer el valor predeterminado para la carpeta de salida si no se proporciona
        if parameters[1].valueAsText is None and parameters[0].valueAsText is not None:
            parameters[1].value = parameters[0].value
            
        # Actualizar el estado de la licencia de Spatial Analyst
        if arcpy.CheckExtension("Spatial") == "Available":
            parameters[2].value = True
        else:
            parameters[2].value = False
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter. This method is called after internal validation."""
        # Mensaje de advertencia si la carpeta de salida no está definida y la de entrada sí
        if parameters[0].valueAsText is not None and parameters[1].valueAsText is None:
            parameters[1].setWarningMessage("Output folder not specified. Results will be saved in the input folder.")
        
        # Mensaje si la licencia de Spatial Analyst no está disponible
        if not parameters[2].value:
            parameters[0].setErrorMessage("Spatial Analyst extension is required but not available.")
            parameters[1].setErrorMessage("Spatial Analyst extension is required but not available.")
        return

    def execute(self, parameters, messages):
        arcpy.AddMessage("Starting image index calculation...")
        input_folder = parameters[0].valueAsText
        output_folder = parameters[1].valueAsText
        
        # Asegurarse de que la extensión Spatial Analyst esté disponible y activada
        if arcpy.CheckExtension("Spatial") == "Available":
            arcpy.CheckOutExtension("Spatial")
        else:
            arcpy.AddError("Spatial Analyst extension is not licensed or available. Please enable it.")
            return

        index_to_calculate = ["ndvi", "gndvi", "ndwi", "msavi", "evi", "ndvi_re"]
        image_counter = 0
        merged_polygon_list = []  # List to store paths of individual index polygons

        arcpy.env.overwriteOutput = True # Sobreescribir automáticamente si los archivos existen
        arcpy.env.workspace = output_folder # Establecer el workspace para salidas temporales o intermedias

        def ensure_clean_folder(folder_path):
            if os.path.exists(folder_path):
                try:
                    shutil.rmtree(folder_path)
                    arcpy.AddMessage(f"Cleaned existing folder: {folder_path}")
                except OSError as e:
                    arcpy.AddWarning(f"Could not remove folder {folder_path}: {e}. Trying to proceed.")
            os.makedirs(folder_path, exist_ok=True) # Crear la carpeta si no existe

        # Recorrer las carpetas para encontrar las imágenes
        for root, dirs, files in os.walk(input_folder):
            for name in files:
                _, ext = os.path.splitext(name)
                # Modificación aquí para asegurar que solo procese imágenes Planet SuperDove de 8 bandas
                if ext.lower() == ".tif" and "AnalyticMS_SR" in name:
                    image_counter += 1
                    image_path = os.path.join(root, name)
                    arcpy.AddMessage(f"Processing image: {image_path}")
                    
                    # Determinar las rutas de salida para esta imagen específica
                    # Crear una estructura de salida dentro de la carpeta de salida general, o de la de entrada
                    relative_path = os.path.relpath(root, input_folder)
                    current_output_path = os.path.join(output_folder, relative_path)
                    
                    indexes_folder = os.path.join(current_output_path, "idxs")

                    ensure_clean_folder(indexes_folder)

                    for index in index_to_calculate:
                        ensure_clean_folder(os.path.join(indexes_folder, index))

                    # Calcular NDVI, GNDVI, NDWI, MSAVI, EVI, and NDVI-RE
                    # Ajustar los nombres de las bandas según la documentación de Planet SuperDove si fuera necesario.
                    # Asumo que 8=NIR, 6=Red, 4=Green, 2=Blue, 5=RedEdge según tu código.
                    # Es buena práctica documentar o verificar esto con la documentación de Planet.
                    arcpy.AddMessage("Calculating NDVI (NIR 8, Red 6)...")
                    NDVI_raster = arcpy.ia.NDVI(image_path, 8, 6)
                    NDVI_raster.save(os.path.join(indexes_folder, "ndvi", "NDVI.tif"))

                    arcpy.AddMessage("Calculating GNDVI (NIR 8, Green 4)...")
                    GNDVI_raster = GNDVI(image_path, 8, 4)
                    GNDVI_raster.save(os.path.join(indexes_folder, "gndvi", "GNDVI.tif"))

                    arcpy.AddMessage("Calculating NDWI (NIR 8, Green 4)...")
                    NDWI_raster = NDWI(image_path, 8, 4) # NDWI para agua
                    NDWI_raster.save(os.path.join(indexes_folder, "ndwi", "NDWI.tif"))

                    arcpy.AddMessage("Calculating MSAVI (NIR 8, Red 6)...")
                    MSAVI_raster = arcpy.ia.MSAVI(image_path, 8, 6)
                    MSAVI_raster.save(os.path.join(indexes_folder, "msavi", "MSAVI.tif"))

                    arcpy.AddMessage("Calculating EVI (NIR 8, Red 6, Blue 2)...")
                    EVI_raster = EVI(image_path, 8, 6, 2)
                    EVI_raster.save(os.path.join(indexes_folder, "evi", "EVI.tif"))

                    arcpy.AddMessage("Calculating NDVI-RE (NIR 8, Red Edge 5)...")
                    NDVI_RE_raster = arcpy.ia.NDVIre(image_path, 8, 5)
                    NDVI_RE_raster.save(os.path.join(indexes_folder, "ndvi_re", "NDVI_RE.tif"))
                    
                    arcpy.AddMessage("Reclassifying rasters and converting to polygons...")
                    rasters = {
                        "ndvi": NDVI_raster,
                        "gndvi": GNDVI_raster,
                        "ndwi": NDWI_raster,
                        "msavi": MSAVI_raster,
                        "evi": EVI_raster,
                        "ndvi_re": NDVI_RE_raster
                    }

                    def reclassify_and_convert_to_polygon(rasters_dict, vectorization_folder, image_name):
                        parent_folder = os.path.basename(os.path.dirname(image_name)) # Re-extraer para seguridad
                        image_date = image_name.split('_')[0] # Extraer la fecha del nombre del archivo

                        for index, raster in rasters_dict.items():
                            arcpy.AddMessage(f"  Processing index: {index}")
                            # Reclasificar el ráster
                            reclassified = arcpy.sa.Slice(raster, 4, "NATURAL_BREAKS")
                            
                            # Ejecutar FocalStatistics para suavizar
                            outFocalStatistics = arcpy.sa.FocalStatistics(
                                reclassified, "Rectangle 3 3 CELL", "MAJORITY", "DATA"
                            )
                            
                            # Simplificar el nombre de salida para evitar caracteres inválidos o nombres muy largos
                            # Usar un nombre único para cada shapefile intermedio
                            unique_id = os.path.splitext(image_name)[0].replace('-', '_') # Usar el nombre base del archivo como parte del ID
                            polygon_path = os.path.join(vectorization_folder, f"{index}_{unique_id}.shp")
                            
                            arcpy.conversion.RasterToPolygon(
                                outFocalStatistics,
                                polygon_path,
                                "NO_SIMPLIFY",
                                "Value",
                            )

                            # Añadir atributos "carpeta" y "fecha" al shapefile
                            arcpy.AddField_management(polygon_path, "carpeta", "TEXT", field_length=50) # Añadir longitud
                            arcpy.AddField_management(polygon_path, "fecha", "TEXT", field_length=20)
                            arcpy.AddField_management(polygon_path, "indice", "TEXT", field_length=15) # Corregir el campo "índice" si lleva tilde

                            with arcpy.da.UpdateCursor(polygon_path, ["carpeta", "fecha", "indice"]) as cursor:
                                for row in cursor:
                                    row[0] = parent_folder
                                    row[1] = image_date
                                    row[2] = index
                                    cursor.updateRow(row)

                            # Añadir la ruta del polígono a la lista para la fusión
                            merged_polygon_list.append(polygon_path)
                            arcpy.AddMessage(f"  Generated polygon: {polygon_path}")

                    vectorization_folder = os.path.join(indexes_folder, "vec")
                    ensure_clean_folder(vectorization_folder)
                    reclassify_and_convert_to_polygon(rasters, vectorization_folder, name) # Pasar 'name' para extraer fecha/carpeta

        # Fusionar todos los polígonos en una sola clase de entidad
        if merged_polygon_list:
            arcpy.AddMessage("Merging all generated polygons...")
            # La salida de la fusión irá directamente a la carpeta de salida principal
            output_merge_shp = os.path.join(output_folder, "merged_indices_polygons.shp")
            arcpy.management.Merge(merged_polygon_list, output_merge_shp)
            arcpy.AddMessage(f"All polygons merged into: {output_merge_shp}")
        else:
            arcpy.AddWarning("No polygons were generated to merge.")
        
        arcpy.AddMessage(f"Process completed! The following indexes were calculated for {image_counter} images: {', '.join(index_to_calculate)}")
        
        # Check out Spatial Analyst extension
        arcpy.CheckInExtension("Spatial")
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and added to the display."""
        # Puedes añadir la capa de salida final al mapa activo aquí
        output_merge_shp = os.path.join(parameters[1].valueAsText, "merged_indices_polygons.shp")
        if arcpy.Exists(output_merge_shp):
            aprx = arcpy.mp.ArcGISProject("CURRENT")
            map = aprx.activeMap
            map.addDataFromPath(output_merge_shp)
            arcpy.AddMessage(f"Merged polygon layer '{os.path.basename(output_merge_shp)}' added to the map.")
        return