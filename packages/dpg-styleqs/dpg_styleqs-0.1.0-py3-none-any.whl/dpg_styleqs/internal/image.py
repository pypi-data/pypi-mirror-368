from PIL import Image, ImageFilter, ImageDraw, ImageChops
from typing import Literal, Tuple
from pathlib import Path
from io import BytesIO
import zipfile
import shutil
import json

#---------- Variables con las ubicaciones de los zip y el JSON ----------
base_dir = Path(__file__).resolve().parent.parent
image_registration = base_dir / "data" / "image_registration.json"
compressed_images = base_dir / "archives" / "compressed_images.zip"
compressed_images_temp = base_dir / "archives" / "compressed_images_temp.zip"

#+----------------------------------------------------------------+
#|                     CLASE IMAGEVALIDATION                      |
#+----------------------------------------------------------------+

#=========== ImageValidation ===========
#Clase de validacion, valida los archivos zip con el JSON
class ImageValidation():
    def __init__(self):
        pass

    #==================== create_register ====================
    #Toma la estructura del tema y lo convierte en el formato que se utiliza en el JSON 
    def create_register(tag: str, theme: dict) -> dict:
        #Estructura del formato de JSON
        structure = {
            tag : {
                "core_effects" : [],
                "image_layer": [],
                "widget_type": theme["widget_type"]
            }
        }

        #Ubica los temas en su respectivo parametros
        for t in theme["themes"]:
            theme_type = t["theme"]
            match theme_type:
                case "background_gradiant":
                    structure[tag]["core_effects"].append(t)
                case "background_color":
                    structure[tag]["core_effects"].append(t)
                case "shadow":
                    structure[tag]["image_layer"].append(t)

        return structure

    #==================== create_register ====================
    #Toma la estructura del tema y lo convierte en el formato que se utiliza en el JSON 
    def remove_files_from_zip(files_to_remove):

        #---------- Abre el zip en modo lectura ----------
        with zipfile.ZipFile(compressed_images, 'r') as zip_read:
            #---------- Crea un zip temporal ----------
            with zipfile.ZipFile(compressed_images_temp, 'w') as zip_write:
                for item in zip_read.infolist():
                    # Si el archivo NO está en la lista a eliminar, lo copiamos
                    if item.filename not in files_to_remove:
                        zip_write.writestr(item, zip_read.read(item.filename))

        # Reemplazar el ZIP original con el nuevo
        shutil.move(compressed_images_temp, compressed_images)

    #==================== JSON_validation ====================
    """
    Sistema de validacion del JSON, elimina ordenes que ya no se llaman, 
    elimina imagenes que no se utilizaran y evita el rehacer imagenes que ya estan creadas
    """
    def JSON_validation(theme_widget, themes):
        content = {}
        #---------- Verifica si el archivo JSON existe ----------
        if image_registration.exists():
            #---------- Abre el zip en modo lectura ----------
            with open(image_registration, "r") as archive:
                try:
                    content = json.load(archive)
                except:
                    content = {}

                key_theme = list(theme_widget)[0]
                theme_widget = json.loads(json.dumps(theme_widget))

                #---------- Verifica si la orden ya esta en el Registro ----------
                if key_theme in content:
                    parameters_theme_widget = theme_widget[key_theme]
                    parameters_content = content[key_theme]

                    #---------- Verifica si no ha cambiado nada ----------
                    if parameters_theme_widget == parameters_content:
                        #ES IGUAL, NO HACER NADA
                        themes["themes"].clear()
                    #---------- Si cambio, verifica que cambio ----------
                    else:
                        #---------- Session donde verifica si cambio algo en el core_effects ----------
                        pt_tm_wg_core_effects = parameters_theme_widget["core_effects"]
                        pt_ct_core_effects = parameters_content["core_effects"]

                        if pt_tm_wg_core_effects != pt_ct_core_effects:
                            for element in pt_ct_core_effects:
                                if element in pt_tm_wg_core_effects:
                                    #ES IGUAL, REMUEVE LA ORDEN DE HACER LA IMAGEN
                                    themes["themes"].remove(element)
                                else:
                                    ImageValidation.remove_files_from_zip(f"{key_theme}/core.png")
                                    #NOTA: ELIMINAR IMAGEN RELACIONAD
                                    content[key_theme]["core_effects"].remove(element)

                            for element in pt_tm_wg_core_effects:
                                if element in pt_ct_core_effects:
                                    print(f"elemento existe en el JSON")
                                else:
                                    #NOTA: AGREGAR IMAGEN RELACIONADA
                                    content[key_theme]["core_effects"].append(element)

                        #---------- Session donde verifica si cambio algo en el image_layer ----------
                        pt_tm_wg_image_layer = parameters_theme_widget["image_layer"]
                        pt_ct_image_layer = parameters_content["image_layer"]

                        if pt_tm_wg_image_layer != pt_ct_image_layer:
                            for element in pt_ct_image_layer:
                                if element in pt_tm_wg_image_layer:
                                    #ES IGUAL, REMUEVE LA ORDEN DE HACER LA IMAGEN
                                    themes["themes"].remove(element)
                                else:
                                    ImageValidation.remove_files_from_zip(f"{key_theme}/image_layer/{element["theme"]}.png")
                                    #NOTA: ELIMINAR IMAGEN RELACIONADA
                                    content[key_theme]["image_layer"].remove(element)

                            for element in pt_tm_wg_image_layer:
                                if element in pt_ct_image_layer:
                                    print(f"elemento existe en el JSON")
                                else:
                                    #NOTA: AGREGAR IMAGEN RELACIONADA
                                    content[key_theme]["image_layer"].append(element)
                        with open(image_registration, "w") as archive:
                            json.dump(content, archive, indent=4)

                        return themes

                    with open(image_registration, "w") as archive:
                        json.dump(content, archive, indent=4)

                    return themes
                else:
                    content.update(theme_widget)

            with open(image_registration, "w") as archive:
                json.dump(content, archive, indent=4)

            return themes
        #---------- Si el archivo no existe lo crea ----------
        else:
            with open(image_registration, "w") as archive:
                content = theme_widget
                json.dump(content, archive, indent=4)
            return themes

    #==================== delete_keys ====================
    #Elimina del archivo JSON todas las claves que no estén en used_keys.
    def delete_keys(used_keys):
        #---------- Verifica si el archivo de registro de imágenes existe ----------
        if image_registration.exists():
            # Abre el archivo en modo lectura
            with open(image_registration, "r") as archivo:
                try:
                    content = json.load(archivo)
                except:
                    content = {}

        #Crea un nuevo diccionario solo con las claves que están en used_keys
        nuevas_keys = {k: v for k, v in content.items() if k in used_keys}

        #Escribe el nuevo JSON sin las keys no utilizadas
        with open(image_registration, "w") as archivo:
            json.dump(nuevas_keys, archivo, indent=4)

#+----------------------------------------------------------------+
#|                      CLASE IMAGE STYLEQS                       |
#+----------------------------------------------------------------+

#==================== ImageStyleQs ====================
#Clase que crea imgenes, agrega efectos y guarda en el archivo zip
class ImageStyleQs():
    def __init__(self):
        self._image = None

    #==================== load_image ====================
    #Carga imagen que esten el zip para asi aplicarle efectos
    def load_image(tag: str, img_type: Literal["core_effects", "image_layer"], img: str):
        #---------- ruta de la imagen ----------
        router = ""
        if img_type == "core_effects":
            router = f"{tag}/core.png"
        elif img_type == "image_layer":
            router = f"{tag}/{img_type}/{img}"
        
        #---------- Abre el zip en modo lectura ----------
        with zipfile.ZipFile(compressed_images, "r") as zipimg:
            #---------- Toma la imagen ----------
            with zipimg.open(router) as img_file:
                #carga la imagen de manera interna
                img_bytes = BytesIO(img_file.read())
                #Abre la imagen como pillow
                img = Image.open(img_bytes)

                return img

    #==================== CreateImage ====================
    #Crea las imagenes
    class CreateImage():
        def __init__(self):
            pass

        #==================== backgroud_color ====================
        #Hace la imagen de un color con el ancho y alto de los widgets
        def backgroud_color(width: int,
                            height: int,
                            color: Tuple[int, int, int, int]):

            size = (width, height)
            image = Image.new("RGBA", size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)

            draw.rectangle((0,0, width, height), fill=color)
            return image

        #==================== background_gradiants ====================
        """
        Hace la imagen gradiante con el ancho y alto de los widgets, 
        tiene 3 tipos, lineal vertical, lineal horizontal y radial
        """
        def background_gradiants(gradiant_type: Literal["Lineal_vertical", "Lineal_horizontal", "Radial"],
                                width: int, height: int,
                                start_color: Tuple[int, int, int],
                                end_color: Tuple[int, int, int]):

            def lineal_vertical_gradiant():
                image = Image.new("RGB", (width, height))
                for y in range(height):
                    t = y / height

                    r = int(start_color[0] + (end_color[0] - start_color[0]) * t)
                    g = int(start_color[1] + (end_color[1] - start_color[1]) * t)
                    b = int(start_color[2] + (end_color[2] - start_color[2]) * t)

                    for x in range(width):
                        image.putpixel((x, y), (r, g, b))

                return image

            def lineal_horizontal_gradiant():
                image = Image.new("RGB", (width, height))
                for x in range(width):
                    t = x / height

                    r = int(start_color[0] + (end_color[0] - start_color[0]) * t)
                    g = int(start_color[1] + (end_color[1] - start_color[1]) * t)
                    b = int(start_color[2] + (end_color[2] - start_color[2]) * t)

                    for y in range(height):
                        image.putpixel((x, y), (r, g, b))

                return image

            def radial_gradient():
                from math import hypot
                image = Image.new("RGB", (width, height))
                center_x = width // 2
                center_y = height // 2
                max_dist = hypot(center_x, center_y)

                for y in range(height):
                    for x in range(width):

                        dist = hypot(x - center_x, y - center_y)
                        t = dist / max_dist
                        t = min(max(t, 0), 1)

                        r = int(start_color[0] + (end_color[0] - start_color[0]) * t)
                        g = int(start_color[1] + (end_color[1] - start_color[1]) * t)
                        b = int(start_color[2] + (end_color[2] - start_color[2]) * t)

                        image.putpixel((x, y), (r, g, b))

                return image

            match gradiant_type:
                case "Lineal_vertical":
                    return lineal_vertical_gradiant()
                case "Lineal_horizontal":
                    return lineal_horizontal_gradiant()
                case "Radial":
                    return radial_gradient()

    #==================== EffectsImage ====================
    #Agrega efectos a las imagenes
    class EffectsImage():
        def __init__(self, image):
            self.image = image

        #==================== silhouette_fill ====================
        #Recrea la silueta de una imagen png
        def silhouette_fill(self,color: Tuple[int, int, int]):
            self.image = self.image.convert("RGBA")
            pixels = self.image.load()

            for y in range(self.image.height):
                for x in range(self.image.width):
                    r, b, g, a = pixels[x, y]
                    if a > 0:
                        pixels[x, y] = (*color, a)
            
            return self

        #==================== silhouette_fill ====================
        #Recrea contorno
        def outline(self,color: Tuple[int, int, int], thickness: int = 2):
            margin = thickness
            width, height = self.image.size
            new_size = (width + margin * 2, height + margin * 2)

            expanded_image = Image.new("RGBA", new_size, (0, 0, 0, 0))
            expanded_image.paste(self.image, (margin, margin))
            self.image = expanded_image

            alpha = self.image.split()[-1]
            mask = alpha.point(lambda p: 255 if p > 0 else 0).convert("L")
            expanded = mask.filter(ImageFilter.MaxFilter(thickness * 2 + 1))
            border_mask = ImageChops.subtract(expanded, mask)

            outline_image = Image.new("RGBA", self.image.size, (0, 0, 0, 0))
            outline_pixels = outline_image.load()
            border_pixels = border_mask.load()

            for y in range(self.image.height):
                for x in range(self.image.width):
                    if border_pixels[x, y] > 0:
                        outline_pixels[x, y] = (*color, 255)

            self.image = Image.alpha_composite(outline_image, self.image)
            return self

        #==================== blur ====================
        #Agrega efecto de desenfoque
        def blur(self,radius: int):
            margin = radius * radius
            width, height = self.image.size
            new_size = (width + margin * 2, height + margin * 2)

            expanded_image = Image.new("RGBA", new_size, (0, 0, 0, 0))
            expanded_image.paste(self.image, (margin, margin))
            self.image = expanded_image

            self.image = self.image.filter(ImageFilter.GaussianBlur(radius=radius))
            return self

        #==================== rounded_corners ====================
        #Redondea las esquinas de las images
        def rounded_corners(self, radius: int):
            width, height = self.image.size

            mask = Image.new("L", (width, height), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle([(0, 0), (width, height)], radius=radius, fill=255)

            self.image.putalpha(mask)
            return self

        #==================== opacity ====================
        #Baja la opacidad de las imagenes
        def opacity(self,opacity: float):
            self.image = self.image.convert("RGBA")
            r, g, b, a = self.image.split()
            a = a.point(lambda p: int(p * opacity))
            self.image = Image.merge("RGBA", (r, b, g, a))
            return self

        #==================== image_return ====================
        #Retorna la imagen de pillow para que despues pueda ser guardada
        def image_return(self):
            return self.image

    #==================== show ====================
    #Muestra la imagen (util para pruebas)
    def show(image):
        image.show()

    #==================== save ====================
    #Guarda las imagenes en el zip
    def save(image, tag: str, site: Literal["core_effects", "image_layer"], img_type: str = ""):
        #---------- Comprueba si el zip existe ----------
        if compressed_images.exists():
            #---------- Abre el zip en modo append(agregar o añadir) ----------
            with zipfile.ZipFile(compressed_images, mode="a") as zipimg:
                #Utilizado para guarda la imagen en memoria
                buffer = BytesIO()
                #Guarda la imagen
                image.save(buffer, format="PNG")
                buffer.seek(0)

                #Ruta para guardar la imagen en el zip
                archive_site = ""
                if site == "core_effects":
                    archive_site = f"{tag}/core.png"
                elif site == "image_layer":
                    archive_site = f"{tag}/image_layer/{img_type}.png"

                #Guarda la imagen en el zip
                zipimg.writestr(archive_site , buffer.read())

        #---------- Si no existe la crea ----------
        else:
            #---------- Abre el zip en modo write(escribir o crear zip) ----------
            with zipfile.ZipFile(compressed_images, "w", zipfile.ZIP_DEFLATED) as zipimg:
                #Utilizado para guarda la imagen en memoria
                buffer = BytesIO()
                #Guarda la imagen
                image.save(buffer, format="PNG")
                buffer.seek(0)

                #Ruta para guardar la imagen en el zip
                archive_site = ""
                if site == "core_effects":
                    archive_site = f"{tag}/core.png"
                elif site == "image_layer":
                    archive_site = f"{tag}/image_layer/{img_type}.png"

                #Guarda la imagen en el zip
                zipimg.writestr(archive_site , buffer.read())

"""
prueba = ImageStyleQs.CreateImage.frame_backgroud_color(width=200, height=200, color=(255,0,0,255))
prueba = ImageStyleQs.EffectsImage(prueba)\
    .silhouette_fill(color=(0,0,0))\
    .rounded_corners(100)\
    .outline(color=(255,255,255), thickness=2)\
    .blur(10)\
    .image_return()
ImageStyleQs.save(prueba, "Nose", "image_layer", "shadow")
"""