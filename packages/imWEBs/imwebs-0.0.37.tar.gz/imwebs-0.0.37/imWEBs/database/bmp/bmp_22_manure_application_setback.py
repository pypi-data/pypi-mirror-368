from .bmp_management_base import BMPManagementBase

class ManureApplicationSetbackManagement(BMPManagementBase):
    """Distribution Table for BMP: Manure application setback (22)"""
    def __init__(self, location:int):
        super().__init__(location)
