"""
File: /main/models/smart_policy_block.py
Author: Jonathan Carr
Date: July 2025
Description: Smart Policy data block
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PolicyForm:
    method: Optional[str] = None
    length: int = 0


@dataclass
class Services:
    type: Optional[str] = None
    version: Optional[str] = None


@dataclass
class ServiceForm:
    policy_engine: dict = field(default_factory=dict)
    comms_manager: dict = field(default_factory=dict)


@dataclass
class PolicyItem:
    protocol: str
    resource: Optional[str] = None
    target: List[Optional[str]] = field(default_factory=list)
    auto: bool = True
    form: dict = field(default_factory=dict)
    action: Optional[str] = None
    condition: Optional[str] = None


@dataclass
class ReceiptTiming:
    on_request: bool = False
    on_delivery: bool = False


@dataclass
class Receipt:
    receipt_timing: dict = field(default_factory=dict)
    resource: Optional[str] = None
    service: Optional[str] = None
    target: List[str] = field(default_factory=list)


@dataclass
class SmartPolicyBlock:
    id: Optional[str]
    date_time: str  # ISO format datetime string
    service: ServiceForm
    policy: List[dict]
    receipt: dict
    certificate_fingerprint: Optional[str] = None
    pdo_fingerprint: Optional[str] = None
    audit_fingerprint: Optional[str] = None


"""
{
'id': STRING(len_256),
'date_time': STRING(datetime),
'service': {'policy_engine': {'type': 'pe',
                              'version': '2.1.0'},
            'comms_manager': {'type': 'cm',
                              'version': '2.1.0'},
		},
						
'policy': [{'protocol': STRING(len_64),		            #‘do_not_open_before’
            'resource': STRING(len_16),			        #Email, SMS
            'target': [LIST],				            #jcarr@arcanecyber.com
            'auto': BOOL,
            'form': {'method': STRING(len_12),	        #PIN
                     'length': INT},
            'action': STRING(len_16)			        #Greater, Less, Equal…
            'condition': STRING(len_256)
        }
		],

'receipt': {'receipt_timing': {'on_request': BOOL,
					           'on_delivery': BOOL},
            'resource': STRING(len_16),
            'service': STRING(len_16),
            'target': [LIST]
	    },
'certificate_fingerprint': STRING(len_128),
'pdo_fingerprint': STRING(len_128),
'audit_fingerprint': STRING(len_128),
}
"""