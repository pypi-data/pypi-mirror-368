from .binWaterFallclass import EnergyProcessor, SpectrumProcessor

'''
这种写法允许调用
from bin_waterfall import SpectrumProcessor
而不是
from bin_waterfall.binWaterFallclass import BinWaterFall
'''
__all__ = ["SpectrumProcessor","EnergyProcessor"]

