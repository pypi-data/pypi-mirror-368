from typing import Any
from sqlalchemy import Column, Integer, REAL
from .bmp_table import BMPTable
from ...names import Names

class SubbasinMultiplier(BMPTable):
    __tablename__ = Names.bmp_table_name_subbasin_multiplier

    ID = Column(Integer, primary_key=True)
    SHC = Column(REAL)
    SOIL_T10 = Column(REAL)
    INTERC_MAX = Column(REAL)
    INTERC_MIN = Column(REAL)
    USLE_C = Column(REAL)
    ROOT_DEPTH = Column(REAL)
    MANNING = Column(REAL)
    FIMP = Column(REAL)
    FCIMP = Column(REAL)
    CURBDEN = Column(REAL)
    URBCOEF = Column(REAL)
    DIRTMX = Column(REAL)
    THALF = Column(REAL)
    TNCONC = Column(REAL)
    TPCONC = Column(REAL)
    TNO3CONC = Column(REAL)
    URBCN2 = Column(REAL)
    PET_LAI_COEFFICIENT = Column(REAL)
    CONDUCTIVITY = Column(REAL)
    DEPTH = Column(REAL)
    POROSITY = Column(REAL)
    FIELD_CAPACITY = Column(REAL)
    WILTING_POINT = Column(REAL)
    RESIDUAL = Column(REAL)
    PORE_INDEX = Column(REAL)
    DENSITY = Column(REAL)
    SAND = Column(REAL)
    CLAY = Column(REAL)
    SLIT = Column(REAL)
    USLE_K = Column(REAL)
    CN2 = Column(REAL)
    RUNOFF_CO = Column(REAL)
    DEPRESSION = Column(REAL)
    SOIL_MOIST_IN = Column(REAL)
    SOIL_NO3_IN = Column(REAL)
    SOIL_ORGN_IN = Column(REAL)
    SOIL_SOLP_IN = Column(REAL)
    SOIL_ORGP_IN = Column(REAL)
    INTERFLOW_SCALE_FACTOR = Column(REAL)

    def __init__(self, id:int):
        self.ID = id
        self.SHC = 1
        self.SOIL_T10 = 1
        self.INTERC_MAX = 1
        self.INTERC_MIN = 1
        self.USLE_C = 1
        self.ROOT_DEPTH = 1
        self.MANNING = 1
        self.FIMP = 1
        self.FCIMP = 1
        self.CURBDEN = 1
        self.URBCOEF = 1
        self.DIRTMX = 1
        self.THALF = 1
        self.TNCONC = 1
        self.TPCONC = 1
        self.TNO3CONC = 1
        self.URBCN2 = 1
        self.PET_LAI_COEFFICIENT = 1
        self.CONDUCTIVITY = 1
        self.DEPTH = 1
        self.POROSITY = 1
        self.FIELD_CAPACITY = 1
        self.WILTING_POINT = 1
        self.RESIDUAL = 1
        self.PORE_INDEX = 1
        self.DENSITY = 1
        self.SAND = 1
        self.CLAY = 1
        self.SLIT = 1
        self.USLE_K = 1
        self.CN2 = 1
        self.RUNOFF_CO = 1
        self.DEPRESSION = 1
        self.SOIL_MOIST_IN = 1
        self.SOIL_NO3_IN = 1
        self.SOIL_ORGN_IN = 1
        self.SOIL_SOLP_IN = 1
        self.SOIL_ORGP_IN = 1
        self.INTERFLOW_SCALE_FACTOR = 1
