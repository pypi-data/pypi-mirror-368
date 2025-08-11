import pandas as pd


class DataFrameUtil:
    
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def get_variant_id(variants: pd.DataFrame, name: str) -> str:
        """ Gets the variant Id from a given name"""
        variants.set_index('name', inplace=True)
        return str(variants.loc[name][0])