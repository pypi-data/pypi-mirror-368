"""
Schema definitions for FPGA-related configurations in SiliconCompiler.

This module defines classes and functions for managing FPGA-specific
parameters, such as part names, LUT sizes, and vendor information,
within the SiliconCompiler schema. It includes schemas for both
tool-library and temporary configurations.
"""

from siliconcompiler.schema import BaseSchema
from siliconcompiler.schema import EditableSchema, Parameter, Scope
from siliconcompiler.schema.utils import trim

from siliconcompiler import ToolLibrarySchema


class FPGASchema(ToolLibrarySchema):
    """
    A schema for configuring FPGA-related parameters.

    This class extends ToolLibrarySchema to provide a structured way
    to define and access FPGA-specific settings like part name and LUT size.
    """
    def __init__(self, name: str = None):
        """
        Initializes the FPGASchema.

        Args:
            name (str, optional): The name of the schema. Defaults to None.
        """
        super().__init__()
        self.set_name(name)

        schema = EditableSchema(self)
        schema.insert(
            "fpga", 'partname',
            Parameter(
                'str',
                scope=Scope.GLOBAL,
                shorthelp="FPGA: part name",
                switch="-fpga_partname <str>",
                example=["cli: -fpga_partname fpga64k",
                         "api: chip.set('fpga', 'partname', 'fpga64k')"],
                help=trim("""
                Complete part name used as a device target by the FPGA compilation
                tool. The part name must be an exact string match to the partname
                hard coded within the FPGA EDA tool.""")))

        schema.insert(
            "fpga", 'lutsize',
            Parameter(
                'int',
                scope=Scope.GLOBAL,
                shorthelp="FPGA: lutsize",
                switch="-fpga_lutsize 'partname <int>'",
                example=["cli: -fpga_lutsize 'fpga64k 4'",
                         "api: chip.set('fpga', 'fpga64k', 'lutsize', '4')"],
                help=trim("""
                Specify the number of inputs in each lookup table (LUT) for the
                FPGA partname.  For architectures with fracturable LUTs, this is
                the number of inputs of the unfractured LUT.""")))

    def set_partname(self, name: str):
        """
        Sets the FPGA part name.

        Args:
            name (str): The name of the FPGA part.

        Returns:
            Any: The result of the `set` operation.
        """
        return self.set("fpga", "partname", name)

    def set_lutsize(self, lut: int):
        """
        Sets the LUT size for the FPGA.

        Args:
            lut (int): The number of inputs for the lookup table.

        Returns:
            Any: The result of the `set` operation.
        """
        return self.set("fpga", "lutsize", lut)

    @classmethod
    def _getdict_type(cls) -> str:
        """
        Returns the meta data for getdict.

        Returns:
            str: The name of the class.
        """

        return FPGASchema.__name__


class FPGASchemaTmp(BaseSchema):
    """
    A temporary schema for FPGA configurations.

    This class is used for temporary storage of FPGA-related settings.
    It extends BaseSchema and uses the `schema_fpga` function to populate
    its fields.
    """
    def __init__(self):
        """
        Initializes the FPGASchemaTmp.
        """
        super().__init__()

        schema_fpga(self)

    @classmethod
    def _getdict_type(cls) -> str:
        """
        Returns the meta data for getdict.

        Returns:
            str: The name of the class.
        """

        return FPGASchemaTmp.__name__


###############################################################################
# FPGA
###############################################################################
def schema_fpga(schema):
    """
    Adds FPGA-related parameters to a given schema.

    This function defines and inserts various FPGA configuration parameters
    into the provided schema object.

    Args:
        schema: The schema object to which the parameters will be added.
    """
    schema = EditableSchema(schema)

    partname = 'default'
    key = 'default'

    schema.insert(
        'partname',
        Parameter(
            'str',
            scope=Scope.GLOBAL,
            shorthelp="FPGA: part name",
            switch="-fpga_partname <str>",
            example=["cli: -fpga_partname fpga64k",
                     "api: chip.set('fpga', 'partname', 'fpga64k')"],
            help=trim("""
            Complete part name used as a device target by the FPGA compilation
            tool. The part name must be an exact string match to the partname
            hard coded within the FPGA EDA tool.""")))

    schema.insert(
        partname, 'vendor',
        Parameter(
            'str',
            scope=Scope.GLOBAL,
            shorthelp="FPGA: vendor name",
            switch="-fpga_vendor 'partname <str>'",
            example=["cli: -fpga_vendor 'fpga64k acme'",
                     "api: chip.set('fpga', 'fpga64k', 'vendor', 'acme')"],
            help=trim("""
            Name of the FPGA vendor for the FPGA partname.""")))

    schema.insert(
        partname, 'lutsize',
        Parameter(
            'int',
            scope=Scope.GLOBAL,
            shorthelp="FPGA: lutsize",
            switch="-fpga_lutsize 'partname <int>'",
            example=["cli: -fpga_lutsize 'fpga64k 4'",
                     "api: chip.set('fpga', 'fpga64k', 'lutsize', '4')"],
            help=trim("""
            Specify the number of inputs in each lookup table (LUT) for the
            FPGA partname.  For architectures with fracturable LUTs, this is
            the number of inputs of the unfractured LUT.""")))

    schema.insert(
        partname, 'file', key,
        Parameter(
            '[file]',
            scope=Scope.GLOBAL,
            shorthelp="FPGA: file",
            switch="-fpga_file 'partname key <file>'",
            example=["cli: -fpga_file 'fpga64k archfile my_arch.xml'",
                     "api: chip.set('fpga', 'fpga64k', 'file', 'archfile', 'my_arch.xml')"],
            help=trim("""
            Specify a file for the FPGA partname.""")))

    schema.insert(
        partname, 'var', key,
        Parameter(
            '[str]',
            scope=Scope.GLOBAL,
            shorthelp="FPGA: var",
            switch="-fpga_var 'partname key <str>'",
            example=["cli: -fpga_var 'fpga64k channelwidth 100'",
                     "api: chip.set('fpga', 'fpga64k', 'var', 'channelwidth', '100')"],
            help=trim("""
            Specify a variable value for the FPGA partname.""")))
