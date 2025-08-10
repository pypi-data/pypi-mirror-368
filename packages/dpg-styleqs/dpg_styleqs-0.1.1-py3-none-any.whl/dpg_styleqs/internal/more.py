from typing import Literal, Union, List, Tuple
import dearpygui.dearpygui as dpg
import traceback

#+----------------------------------------------------------------+
#|                           MORE DATA                            |
#+----------------------------------------------------------------+

#=========== MoreData ===========
#Almacena los datos necesarios para la ejecucion del layout
class MoreData():
    def __init__(self):
        self._execute_after = []

    #============ EXECUTE AFTER ============
    def add_execute_after(self, callback):
        self._execute_after.append(callback)

    def get_execute_after(self):
        return self._execute_after

more_data = MoreData()

#+----------------------------------------------------------------+
#|                             MORE                               |
#+----------------------------------------------------------------+

def execute_after():
    callbacks = more_data.get_execute_after()
    for call in callbacks:
        call()