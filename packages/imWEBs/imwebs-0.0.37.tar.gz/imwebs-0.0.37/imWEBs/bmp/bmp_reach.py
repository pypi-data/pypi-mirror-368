from .bmp import BMP
from whitebox_workflows import Vector, Raster
from .bmp_type import BMPType, ReachBMPColumnNames
from ..database.bmp.reach_bmp import ReachBMPDistribution 
import pandas as pd

class ReachBMP(BMP):
    def __init__(self, bmp_vector:Vector, subbasin_raster:Raster):
        super().__init__(bmp_vector, subbasin_raster)

    @staticmethod
    def bmp_type_to_name(bmp_type:BMPType)->str:
        if bmp_type not in ReachBMPColumnNames:
            raise ValueError(f"BMP type: {bmp_type} is not a reach bmp.")
        
        return ReachBMPColumnNames[bmp_type]
    
    @staticmethod
    def create_reach_bmp_df(subbasin_ids:list, reach_bmp_type_id_subbasin_dict:dict)->pd.DataFrame:
        """create reach_bmp table"""

        #create empty object
        reach_bmps = {sub: ReachBMPDistribution(sub) for sub in subbasin_ids}
        
        #assign the id assuming the type is same as the column name
        for type, bmp_id_subbasins in reach_bmp_type_id_subbasin_dict.items():
            if len(bmp_id_subbasins) <= 0:
                continue

            #assign the id     
            for id, sub in bmp_id_subbasins.items():
                setattr(reach_bmps[sub], ReachBMP.bmp_type_to_name(type), id)
            
        return pd.DataFrame([vars(rb) for rb in reach_bmps.values()])
