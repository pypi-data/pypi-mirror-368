from sqlalchemy import Column, Integer, Float, String
from .parameter_table import ParameterTable

class SoilLookup(ParameterTable):
    __tablename__ = 'SoilLookup'  # Name of the table
    SOILCODE = Column(Integer, primary_key=True)
    SNAM = Column(String)
    KS0 = Column(Float)
    DEPTH0 = Column(Integer)
    POROSITY0 = Column(Float)
    FC0 = Column(Float)
    P_INDEX0 = Column(Float)
    RM0 = Column(Float)
    WP0 = Column(Float)
    B_DENSITY0 = Column(Float)
    SAND0 = Column(Float)
    CLAY0 = Column(Float)
    SILT0 = Column(Float)
    USLE_K0 = Column(Float)
    INTERFLOW_SCALE_FACTOR0 = Column(Float)
    KS1 = Column(Float)
    DEPTH1 = Column(Float)
    POROSITY1 = Column(Float)
    FC1 = Column(Float)
    P_INDEX1 = Column(Float)
    RM1 = Column(Float)
    WP1 = Column(Float)
    B_DENSITY1 = Column(Float)
    SAND1 = Column(Float)
    CLAY1 = Column(Float)
    SILT1 = Column(Float)
    USLE_K1 = Column(Float)
    INTERFLOW_SCALE_FACTOR1 = Column(Float)
    KS2 = Column(Float)
    POROSITY2 = Column(Float)
    FC2 = Column(Float)
    P_INDEX2 = Column(Float)
    RM2 = Column(Float)
    WP2 = Column(Float)
    B_DENSITY2 = Column(Float)
    SAND2 = Column(Float)
    CLAY2 = Column(Float)
    SILT2 = Column(Float)
    USLE_K2 = Column(Float)
    INTERFLOW_SCALE_FACTOR2 = Column(Float)
    TEXTURE = Column(Float)
    HG = Column(Float)

    @property
    def AverageK(self)->float:
        return (getattr(self, "KS1") + getattr(self, "KS2")) / 2
    
    @property
    def AveragePorosity(self)->float:
        return (getattr(self, "POROSITY1") + getattr(self, "POROSITY2")) / 2    