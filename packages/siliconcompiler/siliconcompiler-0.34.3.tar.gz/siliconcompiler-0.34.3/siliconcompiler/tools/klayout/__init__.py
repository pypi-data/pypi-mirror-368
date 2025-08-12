from typing import List, Union

from siliconcompiler import StdCellLibrarySchema
from siliconcompiler import PDKSchema


class KLayoutPDK(PDKSchema):
    """
    Schema for defining technology-specific parameters for the KLayout tool.

    This class extends the base PDKSchema to manage settings related to
    KLayout, such as stream units and which layers to hide on initial display.
    """
    def __init__(self):
        super().__init__()

        self.define_tool_parameter("klayout", "units", "float",
                                   "The stream units for KLayout.")
        self.define_tool_parameter("klayout", "hide_layers", "{str}",
                                   "A list of layer names to initially hide when "
                                   "displaying a layout.")
        self.define_tool_parameter("klayout", "drc_params", "{(str,str)}",
                                   "Set of parameters to include for a particular drc deck, in the "
                                   "form (deck name, parameter).")

    def set_klayout_units(self, units: float):
        """
        Sets the stream units for KLayout.

        Args:
            units (float): The stream unit value.
        """
        self.set("tool", "klayout", "units", units)

    def add_klayout_hidelayers(self, layer: Union[str, List[str]], clobber: bool = False):
        """
        Adds one or more layers to the list of layers to be hidden.

        Args:
            layer (Union[str, List[str]]): The layer name or a list of layer names.
            clobber (bool, optional): If True, overwrites the existing list of hidden layers.
                                      If False, appends to the list. Defaults to False.
        """
        if clobber:
            self.set("tool", "klayout", "hide_layers", layer)
        else:
            self.add("tool", "klayout", "hide_layers", layer)

    def add_klayout_drcparam(self, deck: str, param: Union[str, List[str]], clobber: bool = False):
        """
        Adds one or more parameter to the DRC deck definition.

        Args:
            deck (str): name of the DRC deck.
            param (Union[str, List[str]]): Parameters for a the specified deck.
            clobber (bool, optional): If True, overwrites the existing list of parameters.
                                      If False, appends to the list. Defaults to False.
        """
        if isinstance(param, str):
            param = [param]
        if clobber:
            self.unset("tool", "klayout", "drc_params")

        for p in param:
            self.add("tool", "klayout", "drc_params", (deck, p))


class KLayoutLibrary(StdCellLibrarySchema):
    """
    Schema for defining standard cell library parameters for the KLayout tool.

    This class extends the base StdCellLibrarySchema to manage settings for
    KLayout, such as defining cells that are allowed to be missing from the
    final stream file without generating an error.
    """
    def __init__(self):
        super().__init__()

        self.define_tool_parameter("klayout", "allow_missing_cell", "{str}",
                                   "A list of cells that are allowed to be empty "
                                   "in the final stream file.")

    def add_klayout_allowmissingcell(self, cell: Union[str, List[str]], clobber: bool = False):
        """
        Adds one or more cell names to the list of cells allowed to be missing.

        Args:
            cell (Union[str, List[str]]): The cell name or a list of cell names.
            clobber (bool, optional): If True, overwrites the existing list.
                                      If False, appends to the list. Defaults to False.
        """
        if clobber:
            self.set("tool", "klayout", "allow_missing_cell", cell)
        else:
            self.add("tool", "klayout", "allow_missing_cell", cell)
