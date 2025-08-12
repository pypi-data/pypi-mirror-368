"""
RD Station API Helper
"""
from .rd_station import RDStationAPI
from .dataclasses import (
    Segmentation,
    SegmentationContact,
    Contact,
    ContactFunnelStatus,
    Lead,
    ConversionEvents
)
from .exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    DataProcessingError,
    MetaAdsReportError,
    ValidationError,
)

# Main exports
__all__ = [
    "RDStationAPI",
    # Dataclasses
    "Segmentation",
    "SegmentationContact",
    "Contact",
    "ContactFunnelStatus",
    "Lead",
    "ConversionEvents",
    # Exceptions
    "MetaAdsReportError",
    "AuthenticationError",
    "ValidationError",
    "APIError",
    "DataProcessingError",
    "ConfigurationError",
]
