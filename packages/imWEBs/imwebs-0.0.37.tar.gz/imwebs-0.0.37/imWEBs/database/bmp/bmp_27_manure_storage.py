
from typing import Any
from sqlalchemy import Column, Integer, TEXT, REAL
from .bmp_table import BMPTable
from .bmp_management_base import BMPManagementBaseWithYear
from ...names import Names

class ManureStorageParameter(BMPTable):
    """Parameter Table for BMP: Manure storage capacity and design (27)"""
    __tablename__ = Names.bmp_table_name_manure_storage_parameter
    """Manure storage ID"""    
    ID = Column(Integer,primary_key=True)
    """Name"""
    Name = Column(TEXT)
    """Description"""
    Description = Column(TEXT)
    """Producer ID"""
    ProducerID = Column(Integer)
    """Subbasin ID"""
    Subbasin = Column(Integer)
    """Corresponding feedlot ID"""
    FeedlotID = Column(Integer)
    """Length of the manure storage (m)"""
    ManLength_m = Column(REAL)
    """Width of the Manure storage (m)"""
    ManWidth_m = Column(REAL)
    """Area of the Manure storage (m2)"""
    ManArea_m2 = Column(REAL)
    """Drainage area of the manure storage (ha)"""
    DraArea_ha = Column(REAL)
    """Manure drainage area fraction of the subbasin area (-)"""
    DraFraction = Column(REAL)
    """Distance to the nearby stream"""
    DisReach_m = Column(REAL)
    """Height to the nearby stream"""
    HigReach_m = Column(REAL)
    """Threshold value of storage distance to the nearby stream (100m)"""
    ThDisReach = Column(REAL)
    """Threshold value of storage height to the nearby stream (10m)"""
    ThHigReach = Column(REAL)
    """Initial storage (kg)"""
    ManInitial = Column(REAL)
    """CN change fraction compared to non-storage area"""
    CN_change = Column(REAL)
    """PRC change fraction compared to non-storage area"""
    PRC_change = Column(REAL)
    """Manure event mean concentration (mg/l)"""
    Manure_EMC = Column(REAL)

    def __init__(self, 
                 id:int, 
                 subbasin:int, 
                 feedlot:int, 
                 contribution_area_ha:float, 
                 drainage_fraction:float, 
                 distance_to_reach:float, 
                 height_to_reach:float):
        
        self.ID = id
        self.ProducerID = id
        self.Subbasin = subbasin
        self.FeedlotID = feedlot
        self.DraArea_ha = contribution_area_ha
        self.DraFraction = drainage_fraction
        self.DisReach_m = distance_to_reach
        self.HigReach_m = height_to_reach

        self.ManLength_m = 20
        self.ManWidth_m = 20
        self.ManArea_m2 = 400

        self.ThDisReach = 0
        self.ThHigReach = 0

        self.ManInitial = 0
        self.CN_change = 0.3
        self.PRC_change = 0.3
        self.Manure_EMC = 10000

class ManureStorageManagement(BMPManagementBaseWithYear):
    def __init__(self):
        super().__init__()
        """Month of manure application"""
        self.ManAppMon = 11
        """Day of manure application"""
        self.ManAppDay = 15
        """Fraction of manure amount applied to the field"""
        self.ManAppFra = 1


