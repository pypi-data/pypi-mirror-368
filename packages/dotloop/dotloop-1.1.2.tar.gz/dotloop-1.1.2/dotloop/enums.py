"""Enums for the Dotloop API wrapper."""

from enum import Enum


class TransactionType(Enum):
    """Transaction type options."""

    PURCHASE_OFFER = "PURCHASE_OFFER"
    LISTING_FOR_SALE = "LISTING_FOR_SALE"
    PURCHASED = "PURCHASED"
    SOLD = "SOLD"
    LEASE = "LEASE"
    LEASED = "LEASED"


class LoopStatus(Enum):
    """Loop status options."""

    PRE_OFFER = "PRE_OFFER"
    PRE_LISTING = "PRE_LISTING"
    OFFER_SUBMITTED = "OFFER_SUBMITTED"
    UNDER_CONTRACT = "UNDER_CONTRACT"
    SOLD = "SOLD"
    ARCHIVED = "ARCHIVED"
    CANCELLED = "CANCELLED"


class ParticipantRole(Enum):
    """Participant role options."""

    BUYER = "BUYER"
    SELLER = "SELLER"
    LISTING_AGENT = "LISTING_AGENT"
    BUYING_AGENT = "BUYING_AGENT"
    AGENT = "AGENT"
    LENDER = "LENDER"
    TITLE_COMPANY = "TITLE_COMPANY"
    ATTORNEY = "ATTORNEY"
    INSPECTOR = "INSPECTOR"
    APPRAISER = "APPRAISER"
    OTHER = "OTHER"


class SortDirection(Enum):
    """Sort direction options."""

    ASC = "ASC"
    DESC = "DESC"


class ProfileType(Enum):
    """Profile type options."""

    INDIVIDUAL = "INDIVIDUAL"
    TEAM = "TEAM"
    BROKERAGE = "BROKERAGE"


class LoopSortCategory(Enum):
    """Loop sort category options."""

    DEFAULT = "default"
    ADDRESS = "address"
    CREATED = "created"
    UPDATED = "updated"
    PURCHASE_PRICE = "purchase_price"
    LISTING_DATE = "listing_date"
    EXPIRATION_DATE = "expiration_date"
    CLOSING_DATE = "closing_date"
    REVIEW_SUBMISSION_DATE = "review_submission_date"


class WebhookEventType(Enum):
    """Webhook event type options."""

    LOOP_CREATED = "loop.created"
    LOOP_UPDATED = "loop.updated"
    LOOP_DELETED = "loop.deleted"
    PARTICIPANT_ADDED = "participant.added"
    PARTICIPANT_UPDATED = "participant.updated"
    PARTICIPANT_REMOVED = "participant.removed"
    DOCUMENT_UPLOADED = "document.uploaded"
    DOCUMENT_UPDATED = "document.updated"
    DOCUMENT_DELETED = "document.deleted"
    TASK_COMPLETED = "task.completed"
    TASK_UPDATED = "task.updated"
