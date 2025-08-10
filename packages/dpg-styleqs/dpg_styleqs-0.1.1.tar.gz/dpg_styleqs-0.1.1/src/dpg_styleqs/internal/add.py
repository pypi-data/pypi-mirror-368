import dearpygui.dearpygui as dpg
from typing import Literal, Union, List, Tuple

#==================== register_image ====================
#Funcion para registrar imagen con su ruta
def register_image(route):
    width, height, _, data = dpg.load_image(route)
    with dpg.texture_registry():
        img = dpg.add_static_texture(width, height, data)
    return img, width, height