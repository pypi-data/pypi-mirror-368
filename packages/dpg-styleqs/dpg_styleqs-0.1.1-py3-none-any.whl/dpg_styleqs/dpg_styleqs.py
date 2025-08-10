from typing import Literal, Union, List, Tuple
from .internal import layout, theme, more, add
from dataclasses import dataclass
import dearpygui.dearpygui as dpg
from pathlib import Path
import traceback

#+----------------------------------------------------------------+
#|                           DATA CLASS                           |
#+----------------------------------------------------------------+

#============ POSITION ============
@dataclass
class StaticPosition:
    position_static: Literal["start", "center", "end"] = "start"
    position_type = "static"

    def __post_init__(self):
        if self.position_static not in {"start", "center", "end"}:
            raise ValueError("Parameter 'position_static' must be one of: 'start', 'center', or 'end'.")

@dataclass
class RelativePosition:
    position_relative: Tuple[int, int] = (0,0)
    position_type = "relative"

    def __post_init__(self):
        if not isinstance(self.position_relative, tuple) or len(self.position_relative) != 2:
            raise ValueError("Parameter 'position_relative' must be a tuple of exactly 2 integers (x, y).")
        if not all(isinstance(val, int) for val in self.position_relative):
            raise ValueError("Parameter 'position_relative' must be a tuple of exactly 2 integers (x, y).")

@dataclass
class AbsolutePosition:
    position_absolute:  Union[Tuple[int, int], 
                        Literal["top", "bottom", "left", "right", "center",
                                "top_left", "top_right", "bottom_left", "bottom_right"]] = (0,0)
    position_type = "absolute"

    def __post_init__(self):
        if isinstance(self.position_absolute, tuple):
            if len(self.position_absolute) != 2 or not all(isinstance(val, int) for val in self.position_absolute):
                raise ValueError("Parameter 'position_absolute' must be a tuple of exactly 2 integers (x, y).")
        elif isinstance(self.position_absolute, str):
            if self.position_absolute not in {  "top", "bottom", "left", "right", "center",
                                                "top_left", "top_right", "bottom_left", "bottom_right"}:
                raise ValueError(
                    "Parameter 'position_absolute' must be one of: "
                    "'top', 'bottom', 'left', 'right', 'center', "
                    "'top_left', 'top_right', 'bottom_left', or 'bottom_right'."
                )
        else:
            raise ValueError("Parameter 'position_absolute' must be either a tuple of 2 integers or a valid position string.")

#============== SIZE ==============
@dataclass
class FixedSize:
    pixels: int
    size_type: Literal["fixed"] = "fixed"

    def __post_init__(self):
        if not (1 <= self.pixels):
            raise ValueError("Parameter 'pixels' must be an integer greater than or equal to 1.")

@dataclass
class PercentageSize:
    value: int
    size_type: Literal["percentage"] = "percentage"

    def __post_init__(self):
        if not (1 <= self.value <= 100):
            raise ValueError("Parameter 'value' must be an integer between 1 and 100 (inclusive).")

@dataclass
class GridSize:
    space: int
    size_type: Literal["grid"] = "grid"

    def __post_init__(self):
        if not (1 <= self.space):
            raise ValueError("Parameter 'space' must be an integer greater than or equal to 1.")

#=========== GRID TYPES ===========
@dataclass
class DefineRow:
    row: int
    height: FixedSize
    define: str = "row"

    def __post_init__(self):
        if self.row < 1:
            raise ValueError("Parameter 'row' must be an integer greater than or equal to 1.")
        if not isinstance(self.height, FixedSize):
            raise ValueError("Parameter 'height' must be an instance of FixedSize.")

@dataclass
class DefineColumn:
    column: int
    width: FixedSize
    define: str = "column"

    def __post_init__(self):
        if self.column < 1:
            raise ValueError("Parameter 'column' must be an integer greater than or equal to 1.")
        if not isinstance(self.width, FixedSize):
            raise ValueError("Parameter 'width' must be an instance of FixedSize.")

#+----------------------------------------------------------------+
#|                             LAYOUT                             |
#+----------------------------------------------------------------+

#=========== WindowLayout ===========
"""
Clase principal para el proceso de ejecucion de los layout
Esta clase da la orden de ejecucion de los layout

IMPORTANTE: 
CASO 1: las clases como FlexLayoutBuilder y GridLayoutBuilder
deben de ser ejecutados dentro del contexto de esta clase, si no lo hacen las ordenes
seran ignoradas.

CASO 2: Esta clase inicia el proceso de ejecucion de todo el funcionamiento del modulo
es decir que si no se utiliza, las ordenes del ThemeWidgets y algunas cosas del funcionamiento
de add widget no podrian funcionar, por que? se tomo esta decision por que los modulos como
theme se basan en agregar otro widget y como este modulo utiliza la posicion absoluta para el orden
de los widgets, si no se utiliza, los widgets agregados por las otras funciones o clases no se agregarian como
deberian, por lo cual no tiene sentido ejecutarlos si no se utiliza el layout.
"""
class WindowLayout():
    def __init__(self, tag: Union[str, int]):
        #Validacion
        if not isinstance(tag, (str, int)):
            raise TypeError("Parameter 'tag' must be a string or an integer.")

        self._tag = dpg.get_alias_id(tag)

    def __enter__(self):
        #Agrega la estructura de todos los widgets
        layout.layout_data.add_structure_layout(layout.window_layout_reading(self._tag))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_val, exc_tb)
        #Ejecuta la funcion que agrega el nuevo layout
        else : layout.ExecuteLayout()


#=========== FlexLayoutBuilder ===========
"""
Da la orden del flex layout, ordena los widgets de manera horizontal y vertical
tambien maneja los tamaños de los widgets y de su contenedor
"""
class FlexLayoutBuilder():
    def __init__(self, *,
                tag: Union[str, int],
                height: Union[Literal["auto", "default"], int] = "auto",
                width: Union[Literal["auto", "default"], int] = "auto",
                horizontal: bool = False,
                gap: int = 0,
                padding: Union[int, Tuple[int, int], Tuple[int, int, int, int]] = 0,
                alling_widgets: Literal["alling_start", "alling_center", "alling_end"] = "alling_start",
                no_scrollbar: bool = True
                ) -> None:

        #---------- Validacion de datos de los parametros ----------
        if not isinstance(tag, (str, int)):
            raise TypeError("Parameter 'tag' must be a string or an integer.")

        if isinstance(height, str):
            if height not in {"auto", "default"}:
                raise ValueError("Parameter 'height' must be either 'auto', 'default', or a positive integer.")
        elif isinstance(height, int):
            if height <= 0:
                raise ValueError("Parameter 'height' must be a positive integer.")
        else:
            raise ValueError("Parameter 'height' must be either 'auto', 'default', or a positive integer.")
        
        if isinstance(width, str):
            if width not in {"auto", "default"}:
                raise ValueError("Parameter 'width' must be either 'auto', 'default', or a positive integer.")
        elif isinstance(width, int):
            if width <= 0:
                raise ValueError("Parameter 'width' must be a positive integer.")
        else:
            raise ValueError("Parameter 'width' must be either 'auto', 'default', or a positive integer.")

        if not isinstance(horizontal, bool):
            raise ValueError("Parameter 'horizontal' must be a boolean value (True or False).")

        if not isinstance(gap, int) or gap < 0:
            raise ValueError("Parameter 'gap' must be a non-negative integer.")

        if not  (isinstance(padding, int) or 
                (isinstance(padding, tuple) and len(padding) in {2, 4} and all(isinstance(x, int) for x in padding))):
            raise ValueError("Parameter 'padding' must be either an integer, or a tuple of 2 or 4 integers.")

        if alling_widgets not in {"alling_start", "alling_center", "alling_end"}:
            raise ValueError("Parameter 'alling_widgets' must be one of: 'alling_start', 'alling_center', or 'alling_end'.")

        if not isinstance(no_scrollbar, bool):
            raise ValueError("Parameter 'no_scrollbar' must be a boolean value (True or False).")

        #Indica el tipo de layout
        type_layout = "flex_vertical_layout"
        if horizontal:
            type_layout = "flex_horzizontal_layout"

        #Estructura de flex layout
        self._structure_layout = {  "type": type_layout,
                                    "tag": tag,
                                    "layout": { "width": width,
                                                "height": height,
                                                "gap": gap,
                                                "padding": padding,
                                                "alling_widgets": alling_widgets,
                                                "no_scrollbar": no_scrollbar},
                                    "elements_layout": []}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_val, exc_tb)
        #Ejecuta la funcion que agrega la nueva instruccion al custom layout
        else : 
            layout.layout_data.add_custom_layout(self._structure_layout)

    #Funcion que agrega diseño unico a widget indicado
    def add_widget( self, *, tag: Union[str, int], 
                    position: Union[StaticPosition, RelativePosition, AbsolutePosition] = StaticPosition(),
                    width: Union[FixedSize, PercentageSize, Literal["user"]] = "user",
                    height: Union[FixedSize, PercentageSize, Literal["user"]] = "user"):

        #---------- Validacion de datos de los parametros ----------
        if not isinstance(tag, (str, int)):
            raise TypeError("Parameter 'tag' must be a string or an integer.")

        if not isinstance(position, (StaticPosition, RelativePosition, AbsolutePosition)):
            raise ValueError("Parameter 'position' must be an instance of StaticPosition, RelativePosition, or AbsolutePosition.")

        if not all(isinstance(val, (FixedSize, PercentageSize, str)) for val in (width, height)):
            raise ValueError("Parameters 'width' and 'height' must each be an instance of FixedSize, PercentageSize, or a string.")

        #Toma los datos en un dict y los envia a "self._structure_layout["elements_layout"]"
        self._structure_layout["elements_layout"].append({  "tag": tag, 
                                                            "position": position, 
                                                            "width": width, "height": height})

#=========== GridLayoutBuilder ===========
"""
Da la orden del grid layout, maneja el orden de los widgets como si fueran una cuadricula
se puede modificar las cuadriculas indicando el tamaño de la fila o columna
los widgets adquieren el tamaño de las cuadriculas que fueron asignadas
"""
class GridLayoutBuilder():
    def __init__(self, *,
                tag: Union[str, int],
                rows: Union[int, None] = None,
                columns: int = 1,
                gap: int = 0,
                padding: Union[int, Tuple[int, int], Tuple[int, int, int, int]] = 0,
                no_scrollbar: bool = True
                ) -> None:

        #---------- Validacion de datos de los parametros ----------
        if not isinstance(tag, (str, int)):
            raise TypeError("Parameter 'tag' must be a string or an integer.")
        
        if rows is not None and (not isinstance(rows, int) or rows < 1):
            raise ValueError("Parameter 'rows' must be an integer greater than or equal to 1, or None.")
        
        if not isinstance(columns, int) or columns < 1:
            raise ValueError("Parameter 'columns' must be an integer greater than or equal to 1.")
        
        if not isinstance(gap, int) or gap < 0:
            raise ValueError("Parameter 'gap' must be a non-negative integer.")
        
        if not  (isinstance(padding, int) or 
                (isinstance(padding, tuple) and len(padding) in {2, 4} and all(isinstance(x, int) for x in padding))):
            raise ValueError("Parameter 'padding' must be either an integer, or a tuple of 2 or 4 integers.")
        
        if not isinstance(no_scrollbar, bool):
            raise ValueError("Parameter 'no_scrollbar' must be a boolean value (True or False).")

        #Estructura de grid layout
        self._structure_layout = {  "type": "grid_layout",
                                    "tag": tag,
                                    "layout": { "rows": rows,
                                                "columns": columns,
                                                "gap": gap,
                                                "padding": padding,
                                                "no_scrollbar": no_scrollbar},
                                    "define_rows_columns": [],
                                    "elements_layout": []}
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_val, exc_tb)
        #Ejecuta la funcion que agrega la nueva instruccion al custom layout
        else : layout.layout_data.add_custom_layout(self._structure_layout)
    
    #Esta funcion define un tamaño para las columnas y filas
    def define(self, define: Union[DefineColumn, DefineRow]):

        #---------- Validacion de datos de los parametros ----------
        if not isinstance(define, (DefineColumn, DefineRow)):
            raise ValueError("Parameter 'define' must be an instance of either DefineColumn or DefineRow.")

        #Toma los datos de "define" y los envia a "self._structure_layout["define_row_columns"]"
        self._structure_layout["define_rows_columns"].append(define)

    #Funcion que agrega diseño unico a widget indicado
    def place_widget(self, *,
                    tag: Union[str, int],
                    pos: int):

        #---------- Validacion de datos de los parametros ----------
        if not isinstance(tag, (str, int)):
            raise TypeError("Parameter 'tag' must be a string or an integer.")
        
        if not isinstance(pos, int) or pos < 1:
            raise ValueError("Parameter 'pos' must be an integer greater than or equal to 1.")

        #Toma los datos en un dict y los envia a "self._structure_layout["elements_layout"]"
        self._structure_layout["elements_layout"].append({  "tag": tag, 
                                                            "pos" : pos})
        
#+----------------------------------------------------------------+
#|                          THEME WIDGETS                         |
#+----------------------------------------------------------------+

#=========== ThemeWidgets ===========
"""
Da la orden del grid layout, maneja el orden de los widgets como si fueran una cuadricula
se puede modificar las cuadriculas indicando el tamaño de la fila o columna
los widgets adquieren el tamaño de las cuadriculas que fueron asignadas
"""
class ThemeWidgets():
    def __init__(self, widget_type: Literal["mvChildWindow", "mvImage", "mvImage", "mvImageButton"]):

        #---------- Validacion de datos de los parametros ----------
        if widget_type not in {"mvChildWindow", "mvImage", "mvImage", "mvImageButton"}:
            raise ValueError("Parameter 'widget_type' must be one of: 'mvChildWindow', 'mvImage', or 'mvImageButton'.")

        #Crea un tag unico
        self.tag = dpg.generate_uuid()

        #Crea la estructura de los temas widgets
        self.theme_w = {"widget_type": widget_type,
                        "id": self.tag,
                        "themes": []}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_val, exc_tb)
        else : 
            #Agrega los datos al submodulo theme
            theme.theme_data.add_theme(self.theme_w)

    def add_background_gradiant(self, *,
                                gradiant_type: Literal["Lineal_vertical", "Lineal_horizontal", "Radial"],
                                start_color: Tuple[int, int, int], 
                                end_color: Tuple[int, int, int],
                                rounded_corners: int = 0):

        #---------- Validacion de datos de los parametros ----------
        if gradiant_type not in {"Lineal_vertical", "Lineal_horizontal", "Radial"}:
            raise ValueError("Parameter 'gradiant_type' must be one of: 'Lineal_vertical', 'Lineal_horizontal', or 'Radial'.")

        if isinstance(start_color, tuple):
            if len(start_color) != 3 or not all(isinstance(val, int) for val in start_color):
                raise ValueError("Parameter 'color' must be a tuple of exactly 3 integers (R, G, B).")

        if isinstance(end_color, tuple):
            if len(end_color) != 3 or not all(isinstance(val, int) for val in end_color):
                raise ValueError("Parameter 'color' must be a tuple of exactly 3 integers (R, G, B).")
        
        if not isinstance(rounded_corners, int) or not 0 <= rounded_corners:
            raise ValueError("Parameter 'rounded_corners' must be a non-negative integer.")

        #Crea la estructura del tema
        structure = {   "theme": "background_gradiant",
                        "gradiant_type": gradiant_type,
                        "start_color": start_color,
                        "end_color": end_color,
                        "rounded_corners": rounded_corners}

        if self.theme_w["widget_type"] not in {"mvChildWindow"}:
            raise ValueError("ThemeWidgets.add_background_gradiant")

        #Es agregado a la lista de themes
        self.theme_w["themes"].append(structure)

    def add_background_color(self, *,
                            color: Tuple[int, int, int] = (0, 0, 0),
                            rounded_corners: int = 0):

        #---------- Validacion de datos de los parametros ----------
        if isinstance(color, tuple):
            if len(color) != 3 or not all(isinstance(val, int) for val in color):
                raise ValueError("Parameter 'color' must be a tuple of exactly 3 integers (R, G, B).")

        if not isinstance(rounded_corners, int) or not 0 <= rounded_corners:
            raise ValueError("Parameter 'rounded_corners' must be a non-negative integer.")

        #Crea la estructura del tema
        structure = {   "theme": "background_color",
                        "color": color,
                        "rounded_corners": rounded_corners}

        #Es agregado a la lista de themes
        self.theme_w["themes"].append(structure)

    def add_shadow( self, *, 
                    color: Tuple[int, int, int] = (0, 0, 0),
                    blur_level: int = 5,
                    opacity: float = 0.5,
                    thickness: int = 2,
                    pos: Tuple[int, int] = (0,4)):

        #---------- Validacion de datos de los parametros ----------
        if isinstance(color, tuple):
            if len(color) != 3 or not all(isinstance(val, int) for val in color):
                raise ValueError("Parameter 'color' must be a tuple of exactly 3 integers (R, G, B).")

        if not isinstance(blur_level, int) or not 1 <= blur_level:
            raise ValueError("Parameter 'blur_level' must be an integer greater than or equal to 1.")

        if not isinstance(opacity, float) or opacity < 0.0 or opacity > 1.0:
            raise ValueError("Parameter 'opacity' must be a float between 0.0 and 1.0 (inclusive).")

        if not isinstance(thickness, int) or not 0 <= thickness:
            raise ValueError("Parameter 'thickness' must be a non-negative integer.")
        
        if isinstance(pos, tuple):
            if len(pos) != 2 or not all(isinstance(val, int) for val in pos):
                raise ValueError("Parameter 'pos' must be a tuple of exactly 2 integers (x, y).")

        #Crea la estructura del tema
        structure = {   "theme": "shadow",
                        "color": color,
                        'blur_level': blur_level,
                        "opacity": opacity,
                        "thickness": thickness,
                        "pos": pos}

        #Es agregado a la lista de themes
        self.theme_w["themes"].append(structure)

#=========== bind_widget_theme ===========
"""
Esta funcion indica donde se deberia agregar los temas
IMPORTANTE:
Cada tema que creas contienen un tag propio
Se puede conseguir este tag al momento de asignarle un alias a un contexto de tema, Ejemplo:

with styleqs.ThemeWidgets(widget_type="mvChildWindow") as fondo:
    fondo.add_background_gradiant(  gradiant_type="Lineal_vertical", 
                                    start_color=(115, 250, 120), 
                                    end_color=(45, 75, 105))
tag_tema = fondo.tag    <------------------ Aqui se obtiene el tag

"""
def bind_widget_theme(tag: Union[str, int], tag_theme: int):

    #---------- Validacion de datos de los parametros ----------
    if not isinstance(tag, (str, int)):
        raise TypeError("Parameter 'tag' must be a string or an integer.")
    
    if not isinstance(tag_theme, int):
        raise TypeError("Parameter 'tag_theme' must be an integer that is created when creating a theme.")

    #Crea la estructura de los temas que seran asignados a los widgets
    structure = {"tag": tag, "tag_theme": tag_theme}

    #Es enviado a los datos del submodulo theme
    theme.theme_data.add_bind_theme(structure)

#+----------------------------------------------------------------+
#|                           ADD WIDGET                           |
#+----------------------------------------------------------------+
"""
Para poder agregarle temas a algunos widgets, se debe de tener unos parametros
pero dearpygui no proporciona estos parametros por lo cual se creo esta session
"""

#=========== add_image ===========
"""
Esta funcion agrega una imagen, se puede agregar de manera sencilla con el parametro route
el cual es la ruta de la imagen, adicional guarda en el user_data de dearpygui no de la funcion, 
datos necesarios para agregarle estilos al widget
"""
def add_image(*,route: str, 
                tag: Union[str, int] = 0, 
                width: int, 
                height: int, 
                user_data = None):

    #---------- Validacion de datos de los parametros ----------
    if not isinstance(route, str):
        raise TypeError("Parameter 'route' must be a string representing the image file path.")

    if not isinstance(tag, (str, int)):
        raise TypeError("Parameter 'tag' must be a string or an integer.")

    if not isinstance(width, int):
        raise TypeError("Parameter 'width' must be an integer.")
    if width <= 0:
        raise ValueError("Parameter 'width' must be a positive integer greater than zero.")

    if not isinstance(height, int):
        raise TypeError("Parameter 'height' must be an integer.")
    if height <= 0:
        raise ValueError("Parameter 'height' must be a positive integer greater than zero.")

    #Utiliza el submodulo add para registrar la imagen y obtener el tamaño de esta
    img, width_img, height_img = add.register_image(route)

    #Crea la imagen en dearpygui
    dpg.add_image(img, tag=tag, width=width, height=height, user_data={ "route": route,
                                                                        "size_img": (width_img, height_img),
                                                                        "user_data": user_data})

#=========== add_image_button ===========
#EN PROCESO...
"""
def add_image_button(*, route: str,
                        tag: str, 
                        width: int, 
                        height: int, 
                        user_data,
                        callback):
    pass
"""

#+----------------------------------------------------------------+
#|                               MORE                             |
#+----------------------------------------------------------------+
#Funciones importantes y necesarias para el uso de dearpygui y styleqs

#=========== clear_data ===========
#Funcion que elimina los datos(JSON - registro de imagenes y ZIP - imagenes guardadas)
def clear_data():
    #Variables que almacenan la ubicacion de los datos
    base_dir = Path(__file__).resolve().parent
    image_registration = base_dir / "data" / "image_registration.json"
    compressed_images = base_dir / "archives" / "compressed_images.zip"

    #Elimina el JSON
    if image_registration.exists():
        image_registration.unlink()

    #Elimina el ZIP
    if compressed_images.exists():
        compressed_images.unlink()

#=========== execute_after ===========
#Orden para ejecutar una funcion despues de que se ejecute todo el proceso de la funcion
def execute_after(callback):
    #Guarda la orden en los datos de more
    more.more_data.add_execute_after(callback)

#=========== copy_configuration ===========
#Funcion que copia el ancho y la posicion de un widget de otro widget
def copy_configuration(tag_widget, tag_widget_configuration):
    #Toma el tamaño y la posicion del widget a copiar
    width, height = dpg.get_item_rect_size(tag_widget_configuration)
    pos = dpg.get_item_pos(tag_widget_configuration)

    #Aplica el tamaño y la posicion
    dpg.configure_item(tag_widget, pos=pos, width=width, height=height)