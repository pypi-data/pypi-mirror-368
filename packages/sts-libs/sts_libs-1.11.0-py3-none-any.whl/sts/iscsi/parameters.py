# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""iSCSI parameter management.

This module provides utilities for managing iSCSI parameters:
- Parameter validation
- Parameter negotiation

iSCSI parameters control:
- Data integrity (digests)
- Performance (burst lengths)
- Data transfer behavior
- Session characteristics
"""

from __future__ import annotations

import logging
from typing import Final

# Parameter name mapping between iscsiadm and our API
# iscsiadm uses hierarchical names (node.conn[0].iscsi.*)
# We use simpler names for better usability
PARAM_MAP: Final[dict[str, str]] = {
    'HeaderDigest': 'node.conn[0].iscsi.HeaderDigest',  # CRC32C/None
    'MaxRecvDataSegmentLength': 'node.conn[0].iscsi.MaxRecvDataSegmentLength',  # Bytes
    'MaxXmitDataSegmentLength': 'node.conn[0].iscsi.MaxXmitDataSegmentLength',  # Bytes
    'MaxBurstLength': 'node.session.iscsi.MaxBurstLength',  # Bytes
    'FirstBurstLength': 'node.session.iscsi.FirstBurstLength',  # Bytes
    'ImmediateData': 'node.session.iscsi.ImmediateData',  # Yes/No
    'InitialR2T': 'node.session.iscsi.InitialR2T',  # Yes/No
}


def verify_parameter(
    param: str,
    target_value: str,
    initiator_value: str,
    negotiated_value: str,
    max_burst_length: tuple[str, str] | None = None,
) -> bool:
    """Verify negotiated parameter value.

    Parameter negotiation follows RFC 7143 rules

    Args:
        param: Parameter name
        target_value: Target's offered value
        initiator_value: Initiator's offered value
        negotiated_value: Actually negotiated value
        max_burst_length: (target, initiator) MaxBurstLength values for FirstBurstLength validation

    Returns:
        True if negotiated value is correct, False otherwise
    """
    try:
        if param == 'HeaderDigest':
            # HeaderDigest negotiation:
            # - Both must support CRC32C for it to be used
            # - None is always supported
            # - Order of preference matters
            expected = 'CRC32C' if 'None' not in initiator_value or 'None' not in target_value else 'None'

            if 'CRC32C' not in initiator_value or 'CRC32C' not in target_value:
                expected = 'None'

            # Handle different preference orders
            if initiator_value == 'CRC32C,None' and target_value == 'None,CRC32C':
                expected = 'CRC32C'

            if initiator_value == 'CRC32C,None' and target_value == 'CRC32C,None':
                expected = 'CRC32C'

            if initiator_value == 'None,CRC32C' and target_value == 'CRC32C,None':
                expected = 'None'

            if initiator_value == 'None,CRC32C' and target_value == 'None,CRC32C':
                expected = 'None'

        elif param == 'MaxRecvDataSegmentLength':
            # Receiver controls its buffer size
            expected = initiator_value

        elif param in {'MaxXmitDataSegmentLength', 'MaxBurstLength'}:
            # Use minimum of offered values for data sizes
            expected = target_value if int(target_value) < int(initiator_value) else initiator_value

        elif param == 'ImmediateData':
            # Both must support immediate data for it to be enabled
            expected = 'Yes' if target_value == 'Yes' and initiator_value == 'Yes' else 'No'

        elif param == 'InitialR2T':
            # Both must support disabled R2T for it to be disabled
            expected = 'No' if target_value == 'No' and initiator_value == 'No' else 'Yes'

        elif param == 'FirstBurstLength':
            # First use minimum of offered values
            expected = target_value if int(target_value) < int(initiator_value) else initiator_value

            # Then ensure FirstBurstLength <= MaxBurstLength
            if max_burst_length:
                target_mbl, initiator_mbl = max_burst_length
                exp_max_burst = target_mbl if int(target_mbl) < int(initiator_mbl) else initiator_mbl
                if int(expected) > int(exp_max_burst):
                    expected = exp_max_burst

        else:
            logging.warning(f'Unknown parameter: {param}')
            return False

    except (ValueError, TypeError):
        logging.exception(f'Parameter validation error for {param}')
        return False

    # Log validation failures with details
    if expected != negotiated_value:
        logging.warning(
            f"""
            Parameter {param} validation failed:
            target={target_value}
            initiator={initiator_value}
            negotiated={negotiated_value} expected={expected}
            """
        )
        return False

    return True
