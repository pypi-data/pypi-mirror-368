import dearpygui.dearpygui as dpg
from pathlib import Path
from io import BytesIO
from PIL import Image
from . import image, more
import numpy as np
import zipfile
import json
import copy

#+----------------------------------------------------------------+
#|                           THEME DATA                           |
#+----------------------------------------------------------------+

#=========== ThemeData ===========
#Almacena los datos necesarios para la ejecucion de los themes
class ThemeData():
    def __init__(self):
        self._themes = []
        self._bind_theme = []

    #============== THEMES ==============
    def add_theme(self, theme: dict):
        self._themes.append(theme)

    def get_theme(self):
        return self._themes

    #============== BIND THEME ==============
    def add_bind_theme(self, bind_theme: dict):
        self._bind_theme.append(bind_theme)

    def get_bind_theme(self):
        return self._bind_theme

theme_data = ThemeData()

#+----------------------------------------------------------------+
#|                         EXECUTE THEME                          |
#+----------------------------------------------------------------+

#=========== ExecuteThemes ===========
#Ejecuta las ordenes del theme
class ExecuteThemes():
    def __init__(self):
        self._theme = theme_data.get_theme()
        self._bind_theme = theme_data.get_bind_theme()
        self._theme_manager()

    #==================== _theme_manager ====================
    #Inicia y reparte el proceso de los themes
    def _theme_manager(self):
        #Lista de llaves 
        used_keys = []

        #---------- Bucle que recorre la orden para aplicar los temas ----------
        for element_bind in self._bind_theme:
            #Toma el tag de la orden
            tag = element_bind["tag"]
            #Toma el theme dependiendo del tag_theme asignado en el bind_theme
            themes = copy.deepcopy(next((thems for thems in self._theme if thems['id'] == element_bind["tag_theme"]), None))
            register = image.ImageValidation.create_register(tag, themes)

            key_theme = list(register.keys())[0]  # Guarda la key usada
            used_keys.append(key_theme)
            themes = image.ImageValidation.JSON_validation(register, themes)

            if themes["themes"]:
                self._create_image(themes, tag)

        # Luego de todo, elimina las keys no usadas 
        image.ImageValidation.delete_keys(used_keys)

        self._apply_themes()

    #==================== _create_image ====================
    #Da las ordenes para crear las imagenes
    def _create_image(self, themes, tag):
        #---------- Recorre los temas de las imagenes a crear ----------
        for t in themes["themes"]:
            #Para crear la imagen es necesario tomar el tamaño de los widgets
            width, height = dpg.get_item_rect_size(tag)
            #---------- Realiza las imagenes dependiendo de su tipo ----------
            theme_type = t["theme"]
            match theme_type:
                #---------- Crea la imagen de background gradiente ----------
                case "background_gradiant":
                    #Crea la imagen gradiante
                    img = image.ImageStyleQs.CreateImage.background_gradiants(  gradiant_type=t["gradiant_type"], 
                                                                                width=width,
                                                                                height=height,
                                                                                start_color=t["start_color"],
                                                                                end_color=t["end_color"])
                    #Agrega efectos (rounded_corners)
                    img = image.ImageStyleQs.EffectsImage(img).rounded_corners(t["rounded_corners"])\
                        .image_return()
                    #Guarda la imagen en el zip
                    image.ImageStyleQs.save(img, tag, "core_effects", "background_gradiant")

                #---------- Crea la imagen de background color ----------
                case "background_color":
                    #Crea la imagen de color
                    img = image.ImageStyleQs.CreateImage.backgroud_color(width=width,
                                                                        height= height,
                                                                        color=t["color"])
                    #Agrega efectos (rounded_corners)
                    img = image.ImageStyleQs.EffectsImage(img).rounded_corners(t["rounded_corners"])\
                        .image_return()
                    #Guarda la imagen en el zip
                    image.ImageStyleQs.save(img, tag, "core_effects", "background_color")

                #---------- Crea la imagen de sombreado ----------
                case "shadow":
                    widget_type = themes["widget_type"]
                    match widget_type:
                        #---------- Crea la sombra para los childwindows ----------
                        case "mvChildWindow":
                            #Toma la imgen base(background grandiant o color)
                            try:
                                img = image.ImageStyleQs.load_image(tag, "core_effects", "core.png")
                            except:
                                print(f"The widget with the tag {tag} does not have a base to create the shadow, previously add a background color or gradient for example")
                            else:
                                #Agrega efectos (silhouette_fill, outline, blur, opacity)
                                img = image.ImageStyleQs.EffectsImage(img)\
                                    .silhouette_fill(color=t["color"])\
                                    .outline(color=t["color"], thickness=t["thickness"])\
                                    .blur(t["blur_level"])\
                                    .opacity(t["opacity"])\
                                    .image_return()
                                #Guarda la imagen en el zip
                                image.ImageStyleQs.save(img, tag, "image_layer", "shadow")

                        #---------- Crea la sombra para los widgets de imagenes ----------
                        case "mvImage":
                            #Toma el user data de la imagen(debe ser creada por styleqs)
                            user_data = dpg.get_item_user_data(tag)
                            #Toma la ruta de la imagen
                            img = Image.open(user_data["route"])
                            #Agrega efectos (silhouette_fill, outline, blur, opacity)
                            img = image.ImageStyleQs.EffectsImage(img)\
                                    .silhouette_fill(color=t["color"])\
                                    .outline(color=t["color"], thickness=t["thickness"])\
                                    .blur(t["blur_level"])\
                                    .opacity(t["opacity"])\
                                    .image_return()
                            #Guarda la imagen en el zip
                            image.ImageStyleQs.save(img, tag, "image_layer", "shadow")

    #==================== _register_img_zip ====================
    #Registra la imagen que se encuentra en el zip
    def _register_img_zip(self, router):
        #Consigue la carpeta en donde se encuentra el zip
        base_dir = Path(__file__).resolve().parent.parent
        compressed_images = base_dir / "archives" / "compressed_images.zip"

        #Abre el zip en modo lectura
        with zipfile.ZipFile(compressed_images, "r") as zipimg:
            #Ubica la imagen a utilizar
            with zipimg.open(router) as img_file:
                #Abre la imagen con BytesIO
                image_data = BytesIO(img_file.read())

        #Convierte la imagen en formato RGBA de Pillow
        image_dpg = Image.open(image_data).convert("RGBA")
        #Obtiene el tamaño
        width, height = image_dpg.size
        #Convierte con numpy el formato de pillow a el formato de lectura de dearpygui
        image_np = np.array(image_dpg).flatten() / 255.0

        #Registra la imagen
        with dpg.texture_registry():
            img = dpg.add_static_texture(width, height, image_np)
        return img, width, height

    #==================== _apply_themes ====================
    #Aplica los temas a los widgets
    def _apply_themes(self):
        #Consigue la carpeta en donde se encuentra el JSON
        base_dir = Path(__file__).resolve().parent.parent
        image_registration = base_dir / "data" / "image_registration.json"

        #Abre el JSON en modo de lectura
        with open(image_registration, "r") as archive_JSON:
            #Carga el JSON a la variable content
            content = json.load(archive_JSON)

            #---------- Recorre las llaves (tambien carpetas en el zip y tags de los widgets) del JSON ----------
            for c in content:
                #consigue valores de los widgets (tag, tamaño y pos(posicion))
                tag = c
                width_w, height_w = dpg.get_item_rect_size(c)
                pos = dpg.get_item_pos(c)

                #core_effects(imagen principal, normalmente backgrounds)
                core_effects = content[c]["core_effects"]
                #image_layer(capas de imagenes como pueden ser los sombreados)
                image_layer = content[c]["image_layer"]
                #widget_type(agarra el tipo de widget almacenado en el JSON)
                widget_type = content[c]["widget_type"]

                #Si core_effects no esta vacio significa que hay temas que aplicar
                if core_effects:
                    #Recorre los temas de core
                    for ce in core_effects:
                        #ruta de todos los core en el zip
                        router = f"{tag}/core.png"
                        #Toma la imgen registrada
                        img_ce, _, _ = self._register_img_zip(router)

                        #Adquiere el tema
                        theme_ce = ce["theme"]

                        #---------- Si la palabra "background" esta en el tema se aplica su respectiva configuracion ----------
                        if "background" in theme_ce:
                            children = dpg.get_item_children(tag, 1)
                            #Si existe mas de un widget en el contenedor se aplica antes del primer
                            if children and len(children) > 0:
                                first_child = children[0]
                                dpg.add_image(img_ce, width=width_w, height=height_w, pos=(0,0), parent=tag, before=first_child)
                            #Si no, simplemente se agrega como el primero
                            else:
                                dpg.add_image(img_ce, width=width_w, height=height_w, pos=(0,0), parent=tag)

                #Si image_layer no esta vacio significa que hay temas que aplicar
                if image_layer:
                    #Recorre los temas de image layer
                    for il in image_layer:
                        #ruta de todos las imagen layer en el zip
                        router = f"{tag}/image_layer/{il["theme"]}.png"
                        #Toma la imgen registrada y su tamaño
                        img_il, width, height = self._register_img_zip(router)
                        #Adquiere el tema
                        theme_il = il["theme"]

                        #---------- Agrega casos para los tipos de temas ----------
                        match theme_il:
                            #---------- Aplica el tema shadow(sombreado) ----------
                            case "shadow":
                                match widget_type:
                                    #---------- Caso de aplicacion para los widgets image ----------
                                    case "mvImage":
                                        #Toma el tamaño original del img
                                        width_img, height_img = dpg.get_item_user_data(tag)["size_img"]

                                        #Calcula el tamaño del sombreado dependiendo del tamaño original de la imagen, tamaño del widgets, y tamaño de la imagen shadow
                                        width_shadow = (width_w / width_img) * width
                                        height_shadow = (height_w / height_img) * height

                                        #Posicion del sombreado dado por el usuario
                                        pos_shadow = il["pos"]

                                        #Calcula la posicion
                                        x, y = pos
                                        x -= (width_shadow - width_w) / 2
                                        y -= (height_shadow - height_w) / 2
                                        #Agrega el widget con la imagen de sombreado
                                        dpg.add_image(img_il,   width=width_shadow + pos_shadow[0], 
                                                                height=height_shadow + pos_shadow[1], 
                                                                before=tag, pos=(x, y))

                                    #---------- Caso de aplicacion para los widgets childwindow ----------
                                    case "mvChildWindow":
                                        #Posicion del sombreado dado por el usuario
                                        pos_shadow = il["pos"]

                                        #Calcula la posicion
                                        x, y = pos
                                        x -= (width - width_w) / 2
                                        y -= (height - height_w) / 2

                                        #Agrega el widget con la imagen de sombreado
                                        dpg.add_image(img_il,   width=width + pos_shadow[0], 
                                                                height=height + pos_shadow[1], 
                                                                before=tag, pos=(x, y))
                                        
                more.execute_after()