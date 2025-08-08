from enum import Enum

__all__ = ['ProvisioningVariant']

class ProvisioningVariant(str, Enum):
    DEFAULT = 'DEFAULT'
    NCS_2000_LF1 = 'LF1'
