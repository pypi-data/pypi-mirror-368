from enum import Enum, auto

class InstanceType(str, Enum):
    """Enum representing available instance types for model deployment"""
    G4DN_XLARGE = "G4DN_XLARGE"
    TPU_MEDIUM = "TPU_MEDIUM"
    G5_XLARGE = "G5_XLARGE"
