"""
File: /main/models/smart_policy_block.py
Author: Jonathan Carr
Date: May 2025
Description: Smart Policy data block
"""

from typing import Optional

@smartpolicyblock
class PolicyID:
    """Smart Policy ID"""
    id: str

@smartpolicyblock
class Service:
    """Smart Policy ID"""
    id: str

class SmartPolicyBlock:
    policy_block_signature: Optional[str] = None
    date_time: Optional[str] = None
    encrypted_file_signature: Optional[str] = None

    def __init__(self):
        pass

    def set_policy_block_signature(self, policy_block_signature):
        self.policy_block_signature = policy_block_signature

    def set_date(self, date):
        self.date = date

    def set_encrypted_file_signature(self, encrypted_file_signature):
        self.encrypted_file_signature = encrypted_file_signature




"""
{
'id': {	‘id’: STRING(len_256),
'date_time': STRING(len_32),
'service': {'policy_engine': {'type': 'pe',
                              'version': '2.1.0'},
            'comms_manager': {'type': 'cm',
                              'version': '2.1.0'},
		},
						
'policy': [{'protocol': STRING(len_64),		#‘do_not_open_before’
            'resource': STRING(len_16),			#Email, SMS
            'target': [LIST],				#jcarr@arcanecyber.com
            'auto': BOOL,
            'form': {'method': STRING(len_12),	#PIN
                     'length': INT},
            'action': STRING(len_16)			#Greater, Less, Equal…
            'condition': STRING(len_256)
        }
		],

'receipt': {'receipt_timing': {'on_request': BOOL,
					           'on_delivery': BOOL},
            'resource': STRING(len_16),
            'service': STRING(len_16),
            'target': [LIST]
	    }

"""