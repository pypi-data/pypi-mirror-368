from typing import Any
from sqlalchemy import Column, Integer, TEXT, REAL
from .bmp_table import BMPTable
from .bmp_management_base import BMPManagementBaseWithYear
from ...names import Names

class ManureFeedlot(BMPTable):
    """Parameter Table for BMP: Manure feedlot (29)"""
    __tablename__ = Names.bmp_table_name_manure_feed_lot_parameter
    """ID"""
    ID = Column(Integer, primary_key = True)
    """Name"""
    Name = Column(TEXT)
    """Description"""
    Description = Column(TEXT)
    """Producer ID. Not used in the module"""
    ProducerID = Column(Integer)
    """Subbasin. Not used in the module"""
    Subbasin = Column(Integer)
    """The id of animal whose parameter could be found in livestok_parameter table"""
    AniID = Column(Integer)
    """The id of catch basin which the feedlot would drains to."""
    CatBasID = Column(Integer)
    """Initial manure storage of the feedlot"""
    ManInitial = Column(REAL)
    """Average CN increase fraction compare to non-feedlot area"""
    CN_change = Column(REAL)
    """Average PRC increase fraction compare to non-feedlot area"""
    PRC_change = Column(REAL)
    """Manure event mean concentration"""
    Manure_EMC = Column(REAL)

    def __init__(self, id:int, animal_id:int, subbasin:int, catch_basin_id:int):
        self.ID = id
        self.ProducerID = self.ID
        self.Subbasin = subbasin
        self.CatBasID = catch_basin_id
        self.AniID = animal_id
        self.ManInitial = 0
        self.CN_change = 0.2
        self.PRC_change = 0.2
        self.Manure_EMC = 100000

class ManureFeedlotManagement(BMPManagementBaseWithYear):
    """
    Distribution Table for BMP: Manure feedlot (29)
    It has two operations:
    1. Accumulate: FDLMon,FDLDay,Days,AniAdult,AniNonAdult
    2. Remove: ManStoID,ManStoDis,ManRemMon,ManRemDay,ManRemFra
    """
    
    def __init__(self, feedlot_id:int, adult:int, non_adult:int, manure_stroage_id:str, manure_storage_distribution:str):
        """All data will be read from feedlot boundary shapefile"""
        super().__init__()

        self.Location = feedlot_id

        self.FDLMon = 1
        self.FDLDay = 1
        self.Days = 120

        """Number of adult animals"""
        self.AniAdult = adult
        """Number of non-adult animals"""
        self.AniNonAdult = non_adult

        """Manure storage id spearate by /"""
        self.ManStoID = manure_stroage_id

        """
        Manure storage distribution ratio separated by /
        The total should be <= 1
        The number of ratio is same as the number of manure storage        
        """
        self.ManStoDis = manure_storage_distribution
        self.ManRemMon = 10
        self.ManRemDay = 31
        self.ManRemFra = 1

    @staticmethod
    def column_types()->dict:
        feedlot = ManureFeedlotManagement(0,0,0,"","")
        return {col:(REAL if col == "ManRemFra" else (TEXT if col in ["ManStoID","ManStoDis"] else Integer)) for col in dir(feedlot) if "__" not in col}
