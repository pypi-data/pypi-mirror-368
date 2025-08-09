# servicetitan_pyapi/models/responses.py
"""
Data models for ServiceTitan API responses.

These are optional type hints to improve IDE support and code documentation.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class BaseModel:
    """Base model with common fields"""
    id: int
    createdOn: Optional[str] = None
    modifiedOn: Optional[str] = None
    active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {k: v for k, v in self.__dict__.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create model from dictionary"""
        # Filter only valid fields for this class
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)


@dataclass
class Customer(BaseModel):
    """Customer data model"""
    name: str
    type: Optional[str] = None
    email: Optional[str] = None
    phoneNumber: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    balance: float = 0.0
    tagTypeIds: List[int] = field(default_factory=list)
    customFields: List[Dict[str, Any]] = field(default_factory=list)
    membershipTypeId: Optional[int] = None
    hasActiveMembership: bool = False


@dataclass
class Location(BaseModel):
    """Location data model"""
    name: str
    customerId: int
    address: Optional[Dict[str, Any]] = None
    phoneNumber: Optional[str] = None
    email: Optional[str] = None
    taxZoneId: Optional[int] = None
    zoneId: Optional[int] = None
    tagTypeIds: List[int] = field(default_factory=list)
    customFields: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Contact(BaseModel):
    """Contact data model"""
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    phoneNumber: Optional[str] = None
    type: Optional[str] = None
    isPrimary: bool = False
    customerId: Optional[int] = None
    locationId: Optional[int] = None


@dataclass
class Job(BaseModel):
    """Job data model"""
    jobNumber: str
    customerId: int
    locationId: int
    businessUnitId: int
    jobTypeId: Optional[int] = None
    priority: Optional[str] = None
    status: str = "New"
    summary: Optional[str] = None
    campaignId: Optional[int] = None
    completedOn: Optional[str] = None
    jobGeneratedLeadSource: Optional[Dict[str, Any]] = None
    tagTypeIds: List[int] = field(default_factory=list)
    leadCallId: Optional[int] = None
    bookingId: Optional[int] = None
    soldById: Optional[int] = None
    noCharge: bool = False
    notificationsEnabled: bool = True
    customFields: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Invoice(BaseModel):
    """Invoice data model"""
    invoiceNumber: str
    jobId: int
    customerId: int
    locationId: int
    businessUnitId: int
    status: str
    subtotal: float = 0.0
    tax: float = 0.0
    total: float = 0.0
    balance: float = 0.0
    invoiceDate: Optional[str] = None
    dueDate: Optional[str] = None
    items: List[Dict[str, Any]] = field(default_factory=list)
    payments: List[Dict[str, Any]] = field(default_factory=list)
    adjustments: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Estimate(BaseModel):
    """Estimate data model"""
    estimateNumber: str
    jobId: Optional[int] = None
    customerId: int
    locationId: int
    businessUnitId: int
    status: str = "Open"
    summary: Optional[str] = None
    subtotal: float = 0.0
    tax: float = 0.0
    total: float = 0.0
    soldById: Optional[int] = None
    technicianId: Optional[int] = None
    items: List[Dict[str, Any]] = field(default_factory=list)
    expiresOn: Optional[str] = None


@dataclass
class Appointment(BaseModel):
    """Appointment data model"""
    jobId: int
    appointmentNumber: str
    start: str
    end: str
    arrivalWindowStart: Optional[str] = None
    arrivalWindowEnd: Optional[str] = None
    status: str = "Scheduled"
    technicianIds: List[int] = field(default_factory=list)
    specialInstructions: Optional[str] = None


@dataclass
class Lead(BaseModel):
    """Lead data model"""
    customerId: Optional[int] = None
    locationId: Optional[int] = None
    businessUnitId: int
    jobTypeId: Optional[int] = None
    priority: Optional[str] = None
    campaignId: Optional[int] = None
    summary: Optional[str] = None
    callReasonId: Optional[int] = None
    leadCallId: Optional[int] = None
    bookingId: Optional[int] = None
    status: str = "New"
    followUpDate: Optional[str] = None
    tagTypeIds: List[int] = field(default_factory=list)


@dataclass
class Booking(BaseModel):
    """Booking data model"""
    name: str
    summary: Optional[str] = None
    phoneNumber: Optional[str] = None
    email: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    businessUnitId: Optional[int] = None
    jobTypeId: Optional[int] = None
    priority: Optional[str] = None
    campaignId: Optional[int] = None
    source: Optional[str] = None
    status: str = "Pending"
    isFirstTimeClient: bool = False
    preferredArrivalWindow: Optional[Dict[str, Any]] = None


@dataclass
class Call(BaseModel):
    """Call data model"""
    direction: str  # Inbound/Outbound
    phoneNumber: Optional[str] = None
    customerId: Optional[int] = None
    locationId: Optional[int] = None
    callReasonId: Optional[int] = None
    campaignId: Optional[int] = None
    jobId: Optional[int] = None
    bookingId: Optional[int] = None
    leadId: Optional[int] = None
    duration: int = 0  # seconds
    recordingUrl: Optional[str] = None
    callDateTime: Optional[str] = None
    agentId: Optional[int] = None


@dataclass
class Campaign(BaseModel):
    """Campaign data model"""
    name: str
    categoryId: int
    isActive: bool = True
    phoneNumbers: List[str] = field(default_factory=list)
    costs: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class BusinessUnit(BaseModel):
    """Business Unit data model"""
    name: str
    officialName: Optional[str] = None
    phoneNumber: Optional[str] = None
    email: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = None
    defaultTaxRate: float = 0.0


@dataclass
class Employee(BaseModel):
    """Employee data model"""
    firstName: str
    lastName: str
    email: Optional[str] = None
    phoneNumber: Optional[str] = None
    role: Optional[str] = None
    businessUnitId: Optional[int] = None
    departmentId: Optional[int] = None
    managerId: Optional[int] = None
    employeeTypeId: Optional[int] = None
    active: bool = True


@dataclass
class Technician(BaseModel):
    """Technician data model"""
    name: str
    employeeId: int
    businessUnitId: int
    phoneNumber: Optional[str] = None
    email: Optional[str] = None
    color: Optional[str] = None  # For dispatch board
    teamIds: List[int] = field(default_factory=list)
    skillIds: List[int] = field(default_factory=list)


@dataclass
class TagType(BaseModel):
    """Tag Type data model"""
    name: str
    color: Optional[str] = None
    isAddressTag: bool = False
    isEquipmentTag: bool = False
    isJobTag: bool = False
    isCustomerTag: bool = False