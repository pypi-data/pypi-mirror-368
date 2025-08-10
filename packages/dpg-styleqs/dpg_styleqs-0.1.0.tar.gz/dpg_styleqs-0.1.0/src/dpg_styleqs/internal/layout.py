import dearpygui.dearpygui as dpg
from . import theme
import traceback

#+----------------------------------------------------------------+
#|                          LAYOUT DATA                           |
#+----------------------------------------------------------------+

#=========== LayoutData ===========
#Almacena los datos necesarios para la ejecucion del layout
class LayoutData():
    def __init__(self):
        self._structure_layout = {}
        self._custom_layout = []

    #============ STRUCTURE LAYOUT ============
    def add_structure_layout(self, layout_map):
        self._structure_layout = layout_map

    def get_structure_layout(self):
        return self._structure_layout

    #============== CUSTOM LAYOUT ==============
    def add_custom_layout(self, childwindow_layout: list):
        self._custom_layout.append(childwindow_layout)
    
    def get_custom_layout(self):
        return self._custom_layout
    
    def get_next_custom_layout(self):
        if self._custom_layout:
            return self._custom_layout.pop(0)

layout_data = LayoutData()

#+----------------------------------------------------------------+
#|                        EXTERNAL FUCTION                        |
#+----------------------------------------------------------------+

#=========== wait_rendering ===========
"""
Esta funcion espera el renderizado de los widgets para ejecutar las funcion del layout
si no se espera el renderizado es posible que el layout se realice manera inesperada.
"""
def wait_rendering(tags: list, callback):
    #---------- Validacion de datos de los parametros ----------
    if not isinstance(tags, (str, list)):
        raise ValueError("Parameter 'tags' must be either a string or a list.")

    #Convierte un string a una lista
    if isinstance(tags, str):                                  
        tags = [tags]

    previous_sizes = {tag : None for tag in tags}

    #---------- Verifica el estado de los widgets ----------
    def verify():
        try:
            #---------- Verificando la existencia de todos los tags ----------
            for tag in tags:
                #si aun no existe se vuelve a llamar la funcion "verify" un frame despues
                if not dpg.does_item_exist(tag):
                    dpg.set_frame_callback(dpg.get_frame_count() + 1, verify)
                    return

            all_stable = True

            #---------- Despues de verificar la existencia de los tags, se recorren ----------
            for tag in tags:
                #Toma el tamaño del widget
                current_size = dpg.get_item_rect_size(tag)

                #---------- Si el tamaño es (0,0) aun no se considera terminado la renderizacion ----------
                if current_size == (0,0):
                    all_stable = False
                    break

                previous_size = previous_sizes[tag]

                #---------- Si no se consigue el tamaño o si el tamaño no es igual al anterior no se considera renderizado ----------
                if previous_size is None or current_size != previous_size:
                    previous_sizes[tag] = current_size
                    all_stable = False
                    break

            #---------- Si todos los widgets son estables se ejecuta la funcion dada, si no se vuelve a verificar ----------
            if all_stable:
                callback()
            else:
                dpg.set_frame_callback(dpg.get_frame_count() + 1, verify)

        #---------- Si hay un error lo imprime ----------
        except Exception:
            traceback.print_exc()
            dpg.set_frame_callback(dpg.set_frame_callback(dpg.get_frame_count() + 1, verify))

    #Ejecuta la funcion "verify" despues del frame actual
    dpg.set_frame_callback(dpg.get_frame_count() + 1, verify)

#=========== window_layout_reading ===========
"""
Lee la estructura del window de manera recursiva
pasando por los childwindows
"""
def window_layout_reading(tag: str) -> dict:
    #Contiene la estructura del window
    layout_map = {}

    #=========== _recursively_read ===========
    #Funcion que se utiliza para leer de forma recursiva
    def _recursively_read(current_tag):
        #Toma los hijos
        all_slots = dpg.get_item_children(current_tag)
        #Si hay al menos dos tipos de hijos, entonces toma los del índice 1, si no, deja una lista vacía.
        slot_widgets = all_slots[1] if all_slots and len(all_slots) > 1 else []
        #Crea una lista con el tag del contenedor(window o childwindow)
        layout_map[current_tag] = []

        #---------- Recorreo los widgets hijos ----------
        for w in slot_widgets:
            #Verifica la existencia de un widget
            if not dpg.does_item_exist(w):
                continue                                         

            #Agrega los tags asignados por dearpygui
            layout_map[current_tag].append(w)
            #Obtiene la info del widget
            info = dpg.get_item_info(w)

            #Si el hijo también es un mvChildWindow, llamar recursivamente
            if info["type"] == "mvAppItemType::mvChildWindow":
                _recursively_read(w)

    _recursively_read(current_tag= tag)
    return layout_map

#+----------------------------------------------------------------+
#|                         EXECUTE LAYOUT                         |
#+----------------------------------------------------------------+

#=========== ExecuteLayout ===========
#Ejecuta las ordenes del layout
class ExecuteLayout():
    def __init__(self):
        self._structure_layout = layout_data.get_structure_layout()
        self._custom_layout = layout_data.get_custom_layout()
        self._layout_manager()

    #==================== _layout_manager ====================
    #Inicia y reparte el proceso de los layout
    def _layout_manager(self):
        #---------- Verfica si la lista de custom layout esta vacia, si es asi, termina todo ----------
        if not self._custom_layout:
            theme.ExecuteThemes()
            return

        #Toma la primera orden del custom layout
        next_layout = self._custom_layout.pop(0)
        #Reemplaza el tag por el id que asigna dearpygui
        next_layout["tag"] = dpg.get_alias_id(next_layout["tag"])
        #Toma los widgets hijo del contenedor donde se aplicara el layout
        widgets_layout = self._structure_layout.get(next_layout["tag"])
        #Toman los llaves de next_layout
        parent_tag = next_layout["tag"]
        elements_layout = next_layout["elements_layout"]

        #Convierte todos los tags en id de dearpygui
        for layout in elements_layout:
            layout["tag"] = dpg.get_alias_id(layout["tag"])

        #==================== _main ====================
        #Reparte las tareas de los layout
        def _main():
            match next_layout["type"]:
                case "flex_vertical_layout":
                    self._apply_flex_vertical_layout(widgets_layout, next_layout, parent_tag)
                case "flex_horzizontal_layout":
                    self._apply_flex_horizontal_layout(widgets_layout, next_layout, parent_tag)
                case "grid_layout":
                    self._apply_grid_layout(widgets_layout, next_layout, parent_tag)

        #Espera el renderizado de los widgets y ejecuta la funcion "_main"
        wait_rendering(widgets_layout, _main)

    #==================== _calculate_size ====================
    #Calcula el ancho y alto de los contenedores(childWindow, Window)
    def _calculate_size(self, type_size, calculate):
        #Tag del contenedor
        parent_tag = calculate["parent_tag"]
        #Esta variable almacena un valor de 0 o 1 es decir agarra en size el 0(width) y 1(height)
        w_h_int = calculate["w_h_int"]

        #---------- Deja el valor actual del contenedor ----------
        if type_size == "default":
            size = dpg.get_item_rect_size(parent_tag)
            return size[w_h_int]

        #---------- Calcula el tamaño dependiendo de los widgets (existen 2 tipos) ----------
        elif type_size == "auto":
            match calculate["calculate_type"]:
                #---------- Toma el tamaño recorriendo los widgets y agregando el gap ----------
                case "cycle_through_widgets":
                    parameters = calculate["calculation_type_parameters"]

                    widgets_layout = parameters["widgets_layout"]
                    padding = parameters["padding"]
                    gap = parameters["gap"]

                    w_or_h = padding
                    for widget in widgets_layout:
                        size_widget = dpg.get_item_rect_size(widget)
                        width_or_height = size_widget[w_h_int]
                        w_or_h += width_or_height + gap
                    return w_or_h

                #---------- Toma el tamaño dependiendo del widget con mas tamaño ----------
                case "get_maximum":
                    parameters = calculate["calculation_type_parameters"]

                    widgets_layout = parameters["widgets_layout"]
                    padding = parameters["padding"]

                    w_or_h = 0
                    for widget in widgets_layout:
                        size_widget = dpg.get_item_rect_size(widget)
                        w_or_h = max(w_or_h, size_widget[w_h_int])
                    return w_or_h + (padding * 2)

    #==================== _pos_absolute ====================
    #Agrega la posicion absoluta a los widgets, tiene diversas opciones por defecto
    def _pos_absolute(self, position_absolute, parent_width, parent_height, width, height):
        match position_absolute:
            case "top":
                return ((parent_width / 2) - (width / 2) , 0)
            case "bottom":
                return ((parent_width / 2) - (width / 2) , parent_height - height)
            case "left":
                return (0 , (parent_height / 2) - (height / 2))
            case "right":
                return (parent_width - width , (parent_height / 2) - (height / 2))
            case "center":
                return ((parent_width / 2) - (width / 2) , (parent_height / 2) - (height / 2))
            case "top_left":
                return (0, 0)
            case "top_right":
                return (parent_width - width, 0)
            case "bottom_left":
                return (0, parent_height - height)
            case "bottom_right":
                return (parent_width - width, parent_height - height)
            case (int(x), int(y)):
                return (x, y)

    #==================== _pos_relative ====================
    #<<<<<<<<<<<<<<<<<<< AUN NO AGREGADO >>>>>>>>>>>>>>>>>>>
    def _pos_relative(self):
        print("The _pos_relative function is not yet available.")

    #==================== _apply_flex_vertical_layout ====================
    #realiza el proceso de aplicacion del flex layout de manera vertical
    def _apply_flex_vertical_layout(self, widgets_layout, layout_data, parent_tag):
        #Toma los elementos (widgets) que tiene layout personalizado
        elements_layout = layout_data["elements_layout"]
        #Toma los parametros del contenedor(widget padre o childwindow, window)
        layout_parent = layout_data["layout"]

        #Variables con los elementos de layout_parent
        width_layout = layout_parent["width"]
        height_layout = layout_parent["height"]
        gap = layout_parent["gap"]
        padding = layout_parent["padding"]
        alling_widgets = layout_parent["alling_widgets"]
        no_scrollbar = layout_parent["no_scrollbar"]

        #---------- Consigue el ancho del padre ----------
        if isinstance(width_layout, int):
            #Si es int significa que el usuario agrego un valor
            width_parent = width_layout
        else:
            #Si no lo es, debe ser "auto" o "default" se llama la funcion que lo calcula
            width_parent = self._calculate_size(width_layout, { "parent_tag": parent_tag,
                                                                "w_h_int": 0,
                                                                "calculate_type": "get_maximum",
                                                                "calculation_type_parameters": {
                                                                    "widgets_layout": widgets_layout,
                                                                    "padding": padding
                                                                }})

        #---------- Consigue el alto del padre ----------
        if isinstance(height_layout, int):
            #Si es int significa que el usuario agrego un valor
            height_parent = height_layout
        else:
            #Si no lo es, debe ser "auto" o "default" se llama la funcion que lo calcula
            height_parent = self._calculate_size(height_layout, { "parent_tag": parent_tag,
                                                                "w_h_int": 1,
                                                                "calculate_type": "cycle_through_widgets",
                                                                "calculation_type_parameters": {
                                                                    "widgets_layout": widgets_layout,
                                                                    "padding": padding,
                                                                    "gap": gap
                                                                }})

        #Edita los parametros del padre
        dpg.configure_item( parent_tag,
                            width=width_parent,
                            height=height_parent,
                            no_scrollbar=no_scrollbar,
                            no_scroll_with_mouse=no_scrollbar)

        #Posicion inicial
        y_pos = padding

        #---------- Bucle que recorre todos los widgets y los organiza ----------
        for widget_id in widgets_layout:
            #Tamaño del widget
            width, height = dpg.get_item_rect_size(widget_id)
            #Toma la confirugacion con su tag
            config = next((el for el in elements_layout if el.get("tag") == widget_id), None)
            #posicion inicial del widget
            pos_widget = (0,0)

            #---------- Si configuracion no es None, significa que se agregaron valores modificables ----------
            if config:
                #Varibles que toman el tamaño
                width_widget = config["width"]
                height_widget = config["height"]
                #Toma el tipo de posicionamiento
                position = config["position"]

                #---------- Cambia el ancho del widget ----------
                #Si no es "user" se calcula su valor "percentage" o "fixed", si lo es deja su valor
                if width_widget != "user":
                    size_type = width_widget.size_type
                    #Calcula ancho con el porcentaje 
                    if size_type == "percentage":
                        width = (width_widget.value / 100) * width_parent - (padding * 2)
                        dpg.configure_item(widget_id, width=width)

                    #Ingresa el valor fixed agregado
                    elif size_type == "fixed":
                        width = width_widget.pixels
                        dpg.configure_item(widget_id, width=width)
                    width, height = dpg.get_item_rect_size(widget_id)

                #---------- Cambia el alto del widget ----------
                #Si no es "user" se calcula su valor "percentage" o "fixed", si lo es deja su valor
                if height_widget != "user":
                    size_type = height_widget.size_type

                    #<<<<<<<<<<<<<<<<<<< AUN NO AGREGADO >>>>>>>>>>>>>>>>>>>
                    if size_type == "percentage":
                            print("The application of the percentage with the height in a vertical flex layout is not yet available.")

                    #Ingresa el valor fixed agregado
                    elif size_type == "fixed":
                        height = height_widget.pixels
                        dpg.configure_item(widget_id, height=height)
                    width, height = dpg.get_item_rect_size(widget_id)

                #---------- Aplica el tipo de posicionamiento ----------
                if position.position_type == "static":
                    type_static = position.position_static
                    match type_static:
                        case "start":
                            pos_widget = (padding, y_pos)
                        case "center":
                            pos_widget = ((width_parent / 2) - (width / 2), y_pos)
                        case "end":
                            pos_widget = ((width_parent - width) - padding, y_pos)

            #---------- Si no agrego configuracion del widget, se le agrega el posicionamiento de alling ----------
            else:
                match alling_widgets:
                    case "alling_start":
                        pos_widget = (padding, y_pos)
                    case "alling_center":
                        pos_widget = ((width_parent / 2) - (width / 2), y_pos)
                    case "alling_end":
                        pos_widget = ((width_parent - width) - padding, y_pos)

            #---------- Verifica si se agrego un tipo de posicion en especifico (se agrego aqui por el tipo de posicion relativa) ----------
            if config:
                position = config["position"]
                if position.position_type == "relative":
                    pos_widget = self._pos_relative()
                elif position.position_type == "absolute":
                    pos_widget = self._pos_absolute(position.position_absolute, 
                                                    width_parent, 
                                                    height_parent ,
                                                    width, 
                                                    height)

            #aplica el posicionamiento
            dpg.set_item_pos(widget_id, pos_widget)

            #---------- Identifica si es el ultimo widget para asi no agregarle gap ----------
            if widget_id == widgets_layout[-1]:
                y_pos += height
            else:
                y_pos += height + gap

        #Ejecuta la siguiente orden
        dpg.set_frame_callback(dpg.get_frame_count() + 1, self._layout_manager)

    #==================== _apply_flex_horizontal_layout ====================
    #realiza el proceso de aplicacion del flex layout de manera horizontal
    def _apply_flex_horizontal_layout(self, widgets_layout, layout_data, parent_tag):
        #Toma los elementos (widgets) que tiene layout personalizado
        elements_layout = layout_data["elements_layout"]
        #Toma los parametros del contenedor(widget padre o childwindow, window)
        layout_parent = layout_data["layout"]

        #Variables con los elementos de layout_parent
        width_layout = layout_parent["width"]
        height_layout = layout_parent["height"]
        gap = layout_parent["gap"]
        padding = layout_parent["padding"]
        alling_widgets = layout_parent["alling_widgets"]
        no_scrollbar = layout_parent["no_scrollbar"]

        #---------- Consigue el ancho del padre ----------
        if isinstance(width_layout, int):
            #Si es int significa que el usuario agrego un valor
            width_parent = width_layout
        else:
            #Si no lo es, debe ser "auto" o "default" se llama la funcion que lo calcula
            width_parent = self._calculate_size(width_layout, { "parent_tag": parent_tag,
                                                                "w_h_int": 0,
                                                                "calculate_type": "cycle_through_widgets",
                                                                "calculation_type_parameters": {
                                                                    "widgets_layout": widgets_layout,
                                                                    "padding": padding,
                                                                    "gap": gap
                                                                }})

        #---------- Consigue el alto del padre ----------
        if isinstance(height_layout, int):
            #Si es int significa que el usuario agrego un valor
            height_parent = height_layout
        else:
            #Si no lo es, debe ser "auto" o "default" se llama la funcion que lo calcula
            height_parent = self._calculate_size(height_layout, { "parent_tag": parent_tag,
                                                                "w_h_int": 1,
                                                                "calculate_type": "get_maximum",
                                                                "calculation_type_parameters": {
                                                                    "widgets_layout": widgets_layout,
                                                                    "padding": padding,
                                                                }})

        #Posicion inicial
        x_pos = padding

        #Edita los parametros del padre
        dpg.configure_item( parent_tag,
                            width=width_parent,
                            height=height_parent,
                            no_scrollbar=no_scrollbar,
                            no_scroll_with_mouse=no_scrollbar)

        #---------- Bucle que recorre todos los widgets y los organiza ----------
        for widget_id in widgets_layout:
            #Tamaño del widget
            width, height = dpg.get_item_rect_size(widget_id)
            #Toma la confirugacion con su tag
            config = next ((cfg for cfg in elements_layout if cfg.get("tag") == widget_id), None)
            #Posicion inicial del widget
            pos_widget = (0,0)

            #---------- Si configuracion no es None, significa que se agregaron valores modificables ----------
            if config:
                #Varibles que toman el tamaño
                width_widget = config["width"]
                height_widget = config["height"]
                #Toma el tipo de posicionamiento
                position = config["position"]

                #---------- Cambia el alto del widget ----------
                #Si no es "user" se calcula su valor "percentage" o "fixed", si lo es deja su valor
                if height_widget != "user":
                    size_type = height_widget.size_type

                    #Calcula el alto con el percentage
                    if size_type == "percentage":
                        height = int((height_widget.value / 100) * height_parent - (padding * 2))
                        dpg.configure_item(widget_id, height=height)
                    
                    #Ingresa el valor fixed agregado
                    elif size_type == "fixed":
                        height = height_widget.pixels
                        dpg.configure_item(widget_id, height=height)
                    width, height = dpg.get_item_rect_size(widget_id)

                #---------- Cambia el ancho del widget ----------
                #Si no es "user" se calcula su valor "percentage" o "fixed", si lo es deja su valor
                if width_widget != "user":
                    size_type = width_widget.size_type

                    #<<<<<<<<<<<<<<<<<<< AUN NO AGREGADO >>>>>>>>>>>>>>>>>>>
                    if size_type == "percentage":
                        print("The application of the percentage with the width in a horizontal flex layout is not yet available.")

                    #Ingresa el valor fixed agregado
                    elif size_type == "fixed":
                        width = width_widget.pixels
                        dpg.configure_item(widget_id, width=width)
                    width, height = dpg.get_item_rect_size(widget_id)

                #---------- Aplica el tipo de posicionamiento ----------
                if position.position_type == "static":
                    type_static = position.position_static
                    match type_static:
                        case "start":
                            pos_widget = (x_pos, padding)
                        case "center":
                            pos_widget = (x_pos, (height_parent / 2) - (height / 2))
                        case "end":
                            pos_widget = (x_pos, (height_parent - height) - padding)

            #---------- Si no agrego configuracion del widget, se le agrega el posicionamiento de alling ----------
            else:
                match alling_widgets:
                    case "alling_start":
                        pos_widget = (x_pos, padding)
                    case "alling_center":
                        pos_widget = (x_pos, (height_parent / 2) - (height / 2))
                    case "alling_end":
                        pos_widget = (x_pos, (height_parent - height) - padding)

            #---------- Verifica si se agrego un tipo de posicion en especifico (se agrego aqui por el tipo de posicion relativa) ----------
            if config:
                position = config["position"]
                if position.position_type == "relative":
                    pos_widget = self._pos_relative()
                elif position.position_type == "absolute":
                    pos_widget = self._pos_absolute(position.position_absolute, 
                                                    width_parent, 
                                                    height_parent,
                                                    width, 
                                                    height)

            #aplica el posicionamiento
            dpg.set_item_pos(widget_id, pos_widget)

            #---------- Identifica si es el ultimo widget para asi no agregarle gap ----------
            if widget_id == widgets_layout[-1]:
                x_pos += width
            else:
                x_pos += width + gap

        #Ejecuta la siguiente orden
        dpg.set_frame_callback(dpg.get_frame_count() + 1, self._layout_manager)

    #==================== _apply_grid_layout ====================
    #realiza el proceso de aplicacion del grid layout
    def _apply_grid_layout(self, widgets_layout, layout_data, parent_tag):
        #Tipos de widgets que no permiten modificar el alto
        widgets_without_height = {  "mvAppItemType::mvText", "mvAppItemType::mvCheckbox",
                                    "mvAppItemType::mvRadioButton", "mvAppItemType::mvSelectable",
                                    "mvAppItemType::mvMenuItem", "mvAppItemType::mvListbox",
                                    "mvAppItemType::mvCombo", "mvAppItemType::mvTabButton",
                                    "mvAppItemType::mvTab", "mvAppItemType::mvCollapsingHeader",
                                    "mvAppItemType::mvTreeNode"}
        #Toma los elementos (widgets) que tiene layout personalizado
        elements_layout = layout_data["elements_layout"]
        #Toma los parametros del contenedor(widget padre o childwindow, window)
        layout_parent = layout_data["layout"]
        #Toma los parametros que definen el ancho y alto de las filas o columnas
        define_rows_columns = layout_data["define_rows_columns"]

        #Variables con los elementos de layout_parent
        rows = layout_parent["rows"]
        columns = layout_parent["columns"]
        gap = layout_parent["gap"]
        padding = layout_parent["padding"]
        no_scrollbar = layout_parent["no_scrollbar"]

        #consigue el total de espacios en el grid
        total_space_grid = (rows * columns) + 1

        #Variables que importantes
        #Almacena la ubicacion de los widgets
        place_widgets = []
        #Almacena el ancho y alto de las columnas y filas
        defines = []

        #---------- almacena en un list las columnas y filas definidas ----------
        for define in define_rows_columns:
            define_type = define.define
            match define_type:
                case "row":
                    defines.append({"height": define.height.pixels,
                                    "row": define.row})
                case "column":
                    defines.append({"width": define.width.pixels,
                                    "column": define.column})

        #Variable de columnas y filas que no estan disponibles
        undefined_columns = columns
        undefined_rows = rows

        #---------- Toma el ancho y alto disponible, quitando el padding y gap ----------
        width_space, height_space = dpg.get_item_rect_size(parent_tag)
        available_width_space = (width_space - (padding * 2)) - ((gap - 1) * columns)
        available_height_space = (height_space - (padding * 2)) - ((gap - 1) * rows)

        #---------- Recta el ancho que ya fue definido anteriormente ----------
        unavailable_width_space = next((item for item in defines if item.get("column")), None)
        if unavailable_width_space:
            available_width_space -= unavailable_width_space["width"]
            undefined_columns -= 1

        #---------- Recta el alto que ya fue definido anteriormente ----------
        unavailable_height_space = next((item for item in defines if item.get("row")), None)
        if unavailable_height_space:
            available_height_space -= unavailable_height_space["height"]
            undefined_rows -= 1

        #---------- divide el espacio disponible para las columnas y filas que no fueron definidas ----------
        available_width_space /= undefined_columns
        available_height_space /= undefined_rows

        #Almacena el espacio y las ubicaciones en el eje XY
        space_column = 1
        space_row = 1
        x_pos = padding
        y_pos = padding

        #---------- Bucle que asigna los valores en place_widgets ----------
        for space_grid in range(total_space_grid):
            if space_grid == 0:
                pass
            else:
                #---------- maneja el ancho de los widgets ----------
                width = available_width_space
                current_column_width = next((item for item in defines if item.get("column") == space_column), None)
                if current_column_width:
                    width = current_column_width["width"]

                #---------- maneja el bajado de espacio de widgets ----------
                if (space_grid - 1) % rows == 0 and space_grid != 1:
                    space_column = 1
                    space_row += 1
                    #agrega la posicion de manera vertical
                    y_pos += height + gap
                    #se reinicia el x_pos(posicionamiento de manera vertical) al bajar
                    x_pos = padding

                #---------- maneja el ancho alto de los widgets ----------
                height = available_height_space
                current_row_height = next((item for item in defines if item.get("row") == space_row), None)
                if current_row_height:
                    if current_row_height["row"] == space_row:
                        height = current_row_height["height"]

                #Crea la estructura de los datos
                structure = {space_grid:{"pos": (x_pos, y_pos),
                                        "width": width,
                                        "height": height}}

                #Agrega la posicion de manera horizontal
                x_pos += width + gap
                #Agrega space column
                space_column += 1
                #Agrega la estructura a place_widgets
                place_widgets.append(structure)

        #---------- Agrega los elementos que ya habian definido su posicion ----------
        for element in elements_layout:
            element_place_widget = {}
            for place_w in place_widgets:
                if element["pos"] in place_w:
                    element_x = place_widgets.pop(element["pos"] - 1)
                    element_place_widget = element_x.get(element["pos"])
            #---------- Aplica el tamaño dependiendo del widget ----------
            widget_type = dpg.get_item_type(widget)
            #agrega el elemento con su pos y tamaño
            if widget_type in widgets_without_height:
                dpg.configure_item( element["tag"], 
                                    pos=element_place_widget["pos"], 
                                    width=element_place_widget["width"])
            else:
                dpg.configure_item( element["tag"],
                                    pos=element_place_widget["pos"],
                                    width=element_place_widget["width"],
                                    height=element_place_widget["height"])

            widgets_layout.remove(element["tag"])

        #---------- Agrega los elementos que no han sido definidos ----------
        for widget, place in zip(widgets_layout, place_widgets):
            _, element_place_widget = next(iter(place.items()))

            #---------- Aplica el tamaño dependiendo del widget ----------
            widget_type = dpg.get_item_type(widget)
            #Hay widgets como el texto que no se le puede agregar un alto y su tamaño depende de la fuente
            if widget_type in widgets_without_height:
                dpg.configure_item( widget, 
                                pos=element_place_widget["pos"], 
                                width=element_place_widget["width"])
            else:
                dpg.configure_item( widget, 
                                    pos=element_place_widget["pos"], 
                                    width=element_place_widget["width"], 
                                    height=element_place_widget["height"])

        #Ejecuta la siguiente orden
        dpg.set_frame_callback(dpg.get_frame_count() + 1, self._layout_manager)