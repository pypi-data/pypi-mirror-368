# Copyright: Contributors to the sts project
# SPDX-License-Identifier: GPL-3.0-or-later

"""NVMe device management.

This module provides functionality for managing NVMe devices:
- Device discovery using modern nvme-cli JSON output
- Device information from controllers and namespaces
- Device operations and management

NVMe (Non-Volatile Memory Express) is a protocol designed for:
- High-performance SSDs
- Low latency access
- Parallel operations
- Advanced management features

Key advantages over SCSI/SATA:
- Higher queue depths
- Lower protocol overhead
- Better error handling
- More detailed device information

Discovery Strategy:
- Uses 'nvme list -o json -v' for comprehensive device information
- Provides complete metadata: model, serial, firmware, size, transport, address, NQNs
- Handles both controller-level and subsystem-level namespace locations
- Filters devices by controller name for targeted discovery
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sts.base import StorageDevice
from sts.utils.cmdline import CommandResult, run
from sts.utils.packages import ensure_installed

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path


@dataclass
class NvmeDevice(StorageDevice):
    """NVMe device representation.

    NVMe devices are identified by:
    - Controller number (e.g. nvme0)
    - Namespace ID (e.g. n1)
    - Combined name (e.g. nvme0n1)

    Device information includes:
    - Model and serial number from controller
    - Firmware version from controller
    - Capacity and block size from namespace
    - Transport and addressing information

    Args:
        name: Device name (optional, e.g. 'nvme0n1')
        path: Device path (optional, defaults to /dev/<name>)
        size: Device size in bytes (optional, discovered from namespace)
        model: Device model (optional, discovered from controller)
        serial: Device serial number (optional, discovered from controller)
        firmware: Device firmware version (optional, discovered from controller)
        controller: Controller name (optional, e.g. 'nvme0')
        nsid: Namespace ID (optional, e.g. 1)
        transport: Transport type (optional, e.g. 'pcie')
        address: Device address (optional, e.g. '0000:24:00.0')
        sector_size: Sector size in bytes (optional, defaults to 512)
        host_nqn: Host NQN identifier (optional)
        host_id: Host ID (optional)
        subsystem: Subsystem name (optional)
        subsystem_nqn: Subsystem NQN identifier (optional)
        physical_size: Physical device size (optional)
        used_bytes: Used space in bytes (optional)
        maximum_lba: Maximum LBA count (optional)

    Example:
        ```python
        device = NvmeDevice(name='nvme0n1')  # Discovers other values
        ```
    """

    # Optional parameters from parent classes
    name: str | None = None
    path: Path | str | None = None
    size: int | None = None
    model: str | None = None

    # Optional parameters for this class
    serial: str | None = None  # Device serial number
    firmware: str | None = None  # Firmware version
    controller: str | None = None  # Controller name (e.g. nvme0)
    nsid: int | None = None  # Namespace ID
    transport: str | None = None  # Transport type (pcie, fc, rdma, tcp)
    address: str | None = None  # Device address
    sector_size: int = 512  # Sector size in bytes
    host_nqn: str | None = None  # Host NQN
    host_id: str | None = None  # Host ID
    subsystem: str | None = None  # Subsystem name
    subsystem_nqn: str | None = None  # Subsystem NQN
    physical_size: int | None = None  # Physical device size
    used_bytes: int | None = None  # Used space
    maximum_lba: int | None = None  # Maximum LBA count

    def __post_init__(self) -> None:
        """Initialize NVMe device.

        Discovery process:
        1. Ensure nvme-cli is installed
        2. Set device path if needed
        3. Get device information from nvme list JSON output
        4. Filter by controller name to find target device
        """
        if not ensure_installed('nvme-cli'):
            logging.critical('Failed to install nvme-cli package')

        if not self.path and self.name:
            self.path = f'/dev/{self.name}'

        if not self.controller and self.name:
            match = re.match(r'(nvme\d+)n\d+', self.name)
            self.controller = match.group(1) if match else None

        super().__post_init__()

        # Discover device info using nvme list with JSON output
        if self.name:
            self._discover_from_nvme_list()

    def _discover_from_nvme_list(self) -> bool:
        """Discover device information from nvme list JSON output."""
        result = run('nvme list -o json -v')
        if not result.succeeded or not result.stdout:
            logging.warning('Failed to run nvme list command')
            return False

        data = {}
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            logging.warning('Failed to parse nvme list JSON output')
            return False

        # Search through the JSON structure
        for device_info in data.get('Devices', []):
            # Get host information
            if 'HostNQN' in device_info:
                self.host_nqn = device_info['HostNQN']
            if 'HostID' in device_info:
                self.host_id = device_info['HostID']

            # Search through subsystems
            for subsystem in device_info.get('Subsystems', []):
                # Search through controllers
                for controller in subsystem.get('Controllers', []):
                    # Check controller and its namespaces
                    if 'Controller' in controller and controller.get('Controller') == self.controller:
                        self._extract_controller_info(controller)
                        if 'Subsystem' in subsystem:
                            self.subsystem = subsystem['Subsystem']
                        if 'SubsystemNQN' in subsystem:
                            self.subsystem_nqn = subsystem['SubsystemNQN']
                        for namespace in controller.get('Namespaces', []):
                            self._extract_namespace_info(namespace)
                        break

                # Also check namespaces at subsystem level
                for namespace in subsystem.get('Namespaces', []):
                    if 'NameSpace' in namespace and namespace.get('NameSpace') == self.name:
                        self._extract_namespace_info(namespace)
                        break
        return True

    def _extract_controller_info(self, controller: dict) -> None:
        """Extract controller information and store in device attributes."""
        if 'SerialNumber' in controller:
            self.serial = controller['SerialNumber']
        if 'ModelNumber' in controller:
            self.model = controller['ModelNumber']
        if 'Firmware' in controller:
            self.firmware = controller['Firmware']
        if 'Transport' in controller:
            self.transport = controller['Transport']
        if 'Address' in controller:
            self.address = controller['Address']

    def _extract_namespace_info(self, namespace: dict) -> None:
        """Extract information from a namespace."""
        if 'NSID' in namespace:
            self.nsid = namespace['NSID']
        if 'UsedBytes' in namespace:
            self.used_bytes = namespace['UsedBytes']
        if 'MaximumLBA' in namespace:
            self.maximum_lba = namespace['MaximumLBA']
        if 'PhysicalSize' in namespace:
            self.physical_size = namespace['PhysicalSize']
        if 'SectorSize' in namespace:
            self.sector_size = namespace['SectorSize']
        if self.physical_size:
            self.size = self.physical_size

    def _run(
        self,
        command: str,
        device: str | Path | None = None,
        arguments: Mapping[str, str | None] | None = None,
    ) -> CommandResult:
        """Run nvme command.

        Builds and executes nvme command with:
        - Specified command
        - Given arguments
        - Optional verbose output
        - Auto-selects device target

        Args:
            command: nvme command (e.g. 'smart-log', 'format', 'list')
            device: nvme device
            arguments: Dictionary of arguments

        Returns:
            CommandResult instance

        Example:
            ```python
            device._run('smart-log', '/dev/nvme0n1', arguments={'-o': 'json'})
            ```
        """
        command_list: list[str] = ['nvme', command]

        if device:
            command_list.append(str(device))

        # Add arguments
        if arguments is not None:
            # Handle different argument formats
            for k, v in arguments.items():
                if v is not None:
                    # Check if key already contains '=' for combined format
                    if '=' in k:
                        command_list.append(k)
                    # Check if this should be combined format (long options often use =)
                    elif k.startswith('--') and len(k) > 3:
                        # Use combined format for long options: --key=value
                        command_list.append(f'{k}={v}')
                    else:
                        # Use space-separated format for short options: -k value
                        command_list.extend([k, v])
                elif k.startswith('-'):
                    # Flag argument without value
                    command_list.append(k)

        command_str: str = ' '.join(command_list)
        return run(command_str)

    @classmethod
    def has_nvme(cls) -> bool:
        """Check if system contains any NVMe devices.

        Returns:
            True if NVMe devices found, False otherwise

        Example:
            ```python
            if NvmeDevice.has_nvme():
                devices = NvmeDevice.get_all()
            else:
                print('No NVMe devices found')
            ```
        """
        result = run('nvme list')
        if result.failed or not result.stdout:
            return False

        return any(line.strip().startswith('/dev/nvme') for line in result.stdout.splitlines())

    @classmethod
    def get_all(cls) -> list[NvmeDevice]:
        """Get list of all NVMe devices.

        Returns:
            A list of NvmeDevice instances representing all detected NVMe devices.
            If no devices are found or an error occurs, an empty list is returned.

        Examples:
            ```python
            NvmeDevice.get_all()
            ```
        """
        result = run('nvme list')
        if result.failed:
            logging.warning(f'Running "nvme list" failed:\n{result.stderr}')
            return []

        devices = []
        for line in result.stdout.splitlines():
            # Parse lines like: /dev/nvme0n1     238.47  GB / 238.47  GB    512   B +  0 B
            #                   Samsung SSD 970 EVO 250GB               1.0
            if line.strip().startswith('/dev/nvme') and 'n' in line:
                device_path = line.strip().split()[0]
                device_name = device_path.replace('/dev/', '')
                if device_name:
                    devices.append(cls(name=device_name))

        return devices

    @classmethod
    def get_by_attribute(cls, attribute: str, value: str) -> list[NvmeDevice]:
        """Get devices by attribute value.

        Finds devices matching a specific attribute value:
        - Searches through all available devices
        - Case-sensitive match on attribute value
        - Returns multiple devices if found
        - Empty list if none found

        Args:
            attribute: Device attribute name (e.g. 'model', 'serial', 'transport', 'firmware')
            value: Attribute value to match

        Returns:
            List of NvmeDevice instances matching the attribute value

        Examples:
            ```python
            # Find devices by model
            NvmeDevice.get_by_attribute('model', 'Samsung SSD 970 EVO 250GB')

            # Find devices by transport type
            NvmeDevice.get_by_attribute('transport', 'pcie')

            # Find devices by firmware version
            NvmeDevice.get_by_attribute('firmware', '2B2QEXM7')
            ```
        """
        if not attribute or not value:
            return []

        devices = []
        for device in cls.get_all():
            device_value = getattr(device, attribute, None)
            if device_value and str(device_value) == str(value):
                devices.append(device)

        return devices

    def format(self, **kwargs: str | None) -> bool:
        """Format device.

        Performs a low-level format:
        - Erases all data
        - Resets metadata
        - May take significant time
        - Requires admin privileges

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device.format()
            True
            ```
        """
        if not self.path:
            logging.error('Device path not available')
            return False

        return self._run('format', device=self.path, arguments=kwargs).succeeded

    def sanitize(self, **kwargs: str | None) -> bool:
        """Sanitize device.

        Performs a secure erase:
        - Block erase: Erases all user data by resetting all blocks
        - Crypto erase: Changes encryption keys, making data unrecoverable
        - Overwrite: Overwrites all user data with a data pattern
        - May take significant time
        - Requires admin privileges
        - Some devices may not support all erase methods

        Returns:
            True if successful, False otherwise

        Examples:
            ```python
            # Block erase sanitize
            device.sanitize(**{'--sanact': '0x01'})

            # No-deallocate after sanitize
            device.sanitize(**{'--sanact': '0x01', '--nodas': None})
            ```
        """
        if not self.path:
            logging.error('Device path not available')
            return False

        return self._run('sanitize', device=f'/dev/{self.controller}', arguments=kwargs).succeeded

    def reset(self, **kwargs: str | None) -> bool:
        """Reset NVMe controller.

        Performs a controller-level reset:
        - Resets the NVMe controller
        - Clears any error states
        - Reinitializes the controller
        - May cause temporary device unavailability

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device.reset()
            True
            ```
        """
        if not self.path:
            return False

        return self._run('reset', device=f'/dev/{self.controller}', arguments=kwargs).succeeded

    def flush(self, **kwargs: str | None) -> bool:
        """Flush device cache.

        Commits data and metadata associated with given namespaces to nonvolatile media.
        Applies to all commands finished before the flush was submitted. Additional data
        may also be flushed by the controller, from any namespace, depending on controller
        and associated namespace status.

        Returns:
            True if successful, False otherwise

        Examples:
            ```python
            # Basic flush
            device.flush()

            # Flush with specific namespace ID
            device.flush(**{'--namespace-id': '1'})

            # Flush with timeout
            device.flush(**{'--timeout': '5000'})
            ```
        """
        if not self.path:
            return False

        return self._run('flush', device=self.path, arguments=kwargs).succeeded

    def get_smart_log(self, **kwargs: str | None) -> dict:
        """Get SMART log.

        Retrieves device health information:
        - Critical warnings
        - Temperature
        - Available spare
        - Media errors
        - Read/write statistics

        Returns:
            Dictionary of SMART log entries

        Example:
            ```python
            device.get_smart_log()
            {'critical_warning': '0x0', 'temperature': '35 C', ...}
            ```
        """
        if not self.path:
            return {}

        arguments = {'--output-format': 'json', **kwargs}

        result = self._run('smart-log', device=self.path, arguments=arguments)
        if result.failed or not result.stdout:
            return {}

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            logging.warning('Failed to parse smart-log JSON output')
            return {}

    def get_error_log(self, **kwargs: str | None) -> dict:
        """Get error log.

        Retrieves device error history:
        - Error count
        - Error types
        - Error locations
        - Timestamps

        Returns:
            Dictionary of error log entries

        Example:
            ```python
            device.get_error_log()
            {errors: [{'error_count': 76,...}, ..., {...}]}

            device.get_error_log(**{'-e':'1'})
            {'errors': [{'error_count': 76,...}]}
            ```
        """
        if not self.path:
            return {}

        arguments = {'--output-format': 'json', **kwargs}

        result = self._run('error-log', device=self.path, arguments=arguments)
        if result.failed or not result.stdout:
            return {}

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            logging.warning('Failed to parse error-log JSON output')
            return {}

    def get_fw_log(self, **kwargs: str | None) -> dict:
        """Get firmware log.

        Retrieves firmware event log:
        - Firmware slot information
        - Activation status
        - Firmware revisions
        - Boot partition information

        Returns:
            Dictionary of firmware log entries

        Example:
            ```python
            device.get_fw_log()
            {'afi': 1, 'frs1': 'KB4QEXHA', 'frs2': '', ...}
            ```
        """
        if not self.path:
            return {}

        arguments = {'--output-format': 'json', **kwargs}

        result = self._run('fw-log', device=self.path, arguments=arguments)
        if result.failed or not result.stdout:
            return {}

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            logging.warning('Failed to parse fw-log JSON output')
            return {}

    def get_id_ctrl(self, **kwargs: str | None) -> dict:
        """Get controller identification.

        Retrieves detailed controller information:
        - Vendor and model information
        - Controller capabilities
        - Supported features
        - Command set support

        Returns:
            Dictionary of controller identification data

        Example:
            ```python
            device.get_id_ctrl()
            {'vid': 5197, 'ssvid': 5197, 'mn': 'Samsung SSD 980 PRO 1TB', ...}
            ```
        """
        if not self.path:
            return {}

        arguments = {'--output-format': 'json', **kwargs}

        result = self._run('id-ctrl', device=self.path, arguments=arguments)
        if result.failed or not result.stdout:
            return {}

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            logging.warning('Failed to parse id-ctrl JSON output')
            return {}

    def get_id_ns(self, **kwargs: str | None) -> dict:
        """Get namespace identification.

        Retrieves detailed namespace information:
        - Namespace size and capacity
        - Data protection capabilities
        - Multi-path I/O capabilities
        - Namespace features

        Returns:
            Dictionary of namespace identification data

        Example:
            ```python
            device.get_id_ns()
            {'nsze': 1953525168, 'ncap': 1953525168, 'nuse': 1953525168, ...}
            ```
        """
        if not self.path:
            return {}

        arguments = {'--output-format': 'json', **kwargs}

        result = self._run('id-ns', device=self.path, arguments=arguments)
        if result.failed or not result.stdout:
            return {}

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            logging.warning('Failed to parse id-ns JSON output')
            return {}

    def list_ns(self, **kwargs: str | None) -> dict:
        """List namespaces.

        Lists all namespaces attached to the controller:
        - Active namespaces
        - Allocated namespaces
        - Namespace identifiers

        Returns:
            Dictionary of namespace list

        Example:
            ```python
            device.list_ns()
            [1, 0, 0, 0, ...]
            ```
        """
        if not self.controller:
            return {}

        arguments = {'--output-format': 'json', **kwargs}

        result = self._run('list-ns', device=f'/dev/{self.controller}', arguments=arguments)
        if result.failed or not result.stdout:
            return {}

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            logging.warning('Failed to parse list-ns JSON output')
            return {}

    def get_feature(self, feature_id: str, **kwargs: str | None) -> dict:
        """Get device feature.

        Retrieves current feature settings:
        - Power management
        - Temperature threshold
        - Error recovery
        - Volatile write cache

        Args:
            feature_id: Feature ID to retrieve (e.g., '0x01', '0x02')

        Returns:
            Dictionary of feature data

        Example:
            ```python
            # Get power management feature
            device.get_feature('0x02')
            {'fid': 2, 'cdw11': 0, 'cdw12': 0, ...}

            # Get temperature threshold
            device.get_feature('0x04')
            ```
        """
        if not self.path:
            return {}

        arguments = {'--feature-id': feature_id, '--output-format': 'json', **kwargs}

        result = self._run('get-feature', device=self.path, arguments=arguments)
        if result.failed or not result.stdout:
            return {}

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            logging.warning('Failed to parse get-feature JSON output')
            return {}

    def set_feature(self, feature_id: str, value: str, **kwargs: str | None) -> bool:
        """Set device feature.

        Configures device features:
        - Power management settings
        - Temperature thresholds
        - Error recovery parameters
        - Cache settings

        Args:
            feature_id: Feature ID to set (e.g., '0x01', '0x02')
            value: Feature value to set

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            # Set power management feature
            device.set_feature('0x02', '0x00')
            True

            # Set temperature threshold
            device.set_feature('0x04', '85')
            ```
        """
        if not self.path:
            return False

        arguments = {'--feature-id': feature_id, '--value': value, **kwargs}

        return self._run('set-feature', device=self.path, arguments=arguments).succeeded

    def device_self_test(self, test_code: str = '1', **kwargs: str | None) -> bool:
        """Perform device self-test.

        Initiates device self-test operation:
        - Short self-test (test_code='1')
        - Extended self-test (test_code='2')
        - Abort self-test (test_code='15')

        Args:
            test_code: Self-test code ('1'=short, '2'=extended, '15'=abort)

        Returns:
            True if test initiated successfully, False otherwise

        Example:
            ```python
            # Start short self-test
            device.device_self_test('1')
            True

            # Start extended self-test
            device.device_self_test('2')
            ```
        """
        if not self.path:
            return False

        arguments = {'--self-test-code': test_code, **kwargs}

        return self._run('device-self-test', device=self.path, arguments=arguments).succeeded

    def get_self_test_log(self, **kwargs: str | None) -> dict:
        """Get self-test log.

        Retrieves device self-test results:
        - Test completion status
        - Test results
        - Failure information
        - Test history

        Returns:
            Dictionary of self-test log entries

        Example:
            ```python
            device.get_self_test_log()
            {'current_operation': 0, 'completion': 0, 'result': [...]}
            ```
        """
        if not self.path:
            return {}

        arguments = {'--output-format': 'json', **kwargs}

        result = self._run('self-test-log', device=self.path, arguments=arguments)
        if result.failed or not result.stdout:
            return {}

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            logging.warning('Failed to parse self-test-log JSON output')
            return {}

    def fw_download(self, firmware_file: str, **kwargs: str | None) -> bool:
        """Download firmware to device.

        Downloads new firmware to the device:
        - Transfers firmware image
        - Validates firmware
        - Prepares for activation

        Args:
            firmware_file: Path to firmware file

        Returns:
            True if download successful, False otherwise

        Example:
            ```python
            device.fw_download('/path/to/firmware.bin')
            True
            ```
        """
        if not self.path:
            return False

        arguments = {'--fw': firmware_file, **kwargs}

        return self._run('fw-download', device=self.path, arguments=arguments).succeeded

    def fw_commit(self, slot: str, action: str = '1', **kwargs: str | None) -> bool:
        """Commit/activate firmware.

        Activates downloaded firmware:
        - Commits firmware to slot
        - Activates firmware
        - May require reset

        Args:
            slot: Firmware slot number ('0'-'7')
            action: Commit action ('0'=download, '1'=commit+activate, '2'=activate, '3'=commit+activate+reset)

        Returns:
            True if commit successful, False otherwise

        Example:
            ```python
            # Commit and activate firmware in slot 1
            device.fw_commit('1', '1')
            True
            ```
        """
        if not self.path:
            return False

        arguments = {'--slot': slot, '--action': action, **kwargs}

        return self._run('fw-commit', device=self.path, arguments=arguments).succeeded

    def get_lba_status(self, start_lba: str, block_count: str, **kwargs: str | None) -> dict:
        """Get LBA status information.

        Retrieves logical block status:
        - Block allocation status
        - Block state information
        - Error status

        Args:
            start_lba: Starting LBA
            block_count: Number of blocks to check

        Returns:
            Dictionary of LBA status information

        Example:
            ```python
            device.get_lba_status('0', '1024')
            {'lba_status': [...]}
            ```
        """
        if not self.path:
            return {}

        arguments = {'--start-lba': start_lba, '--block-count': block_count, '--output-format': 'json', **kwargs}

        result = self._run('get-lba-status', device=self.path, arguments=arguments)
        if result.failed or not result.stdout:
            return {}

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            logging.warning('Failed to parse get-lba-status JSON output')
            return {}

    def dsm(self, range_list: str, **kwargs: str | None) -> bool:
        """Data Set Management (TRIM/Deallocate).

        Performs data set management operations:
        - TRIM/deallocate unused blocks
        - Optimize performance
        - Improve wear leveling

        Args:
            range_list: Comma-separated list of LBA ranges to deallocate

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            # Deallocate blocks 0-1023
            device.dsm('0,1024')
            True
            ```
        """
        if not self.path:
            return False

        arguments = {'--ad': 1, '--range': range_list, **kwargs}

        return self._run('dsm', device=self.path, arguments=arguments).succeeded

    def show_regs(self, **kwargs: str | None) -> dict:
        """Show controller registers.

        Displays controller register values:
        - Controller capabilities
        - Controller configuration
        - Controller status
        - Admin/IO queue attributes

        Returns:
            Dictionary of register values

        Example:
            ```python
            device.show_regs()
            {'cap': '0x2014030300b0', 'vs': '0x10300', 'cc': '0x460001', ...}
            ```
        """
        if not self.controller:
            return {}

        arguments = {'--output-format': 'json', **kwargs}

        result = self._run('show-regs', device=f'/dev/{self.controller}', arguments=arguments)
        if result.failed or not result.stdout:
            return {}

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            logging.warning('Failed to parse show-regs JSON output')
            return {}

    def ns_rescan(self, **kwargs: str | None) -> bool:
        """Rescan namespaces.

        Rescans for namespace changes:
        - Detects new namespaces
        - Updates namespace list
        - Refreshes kernel state

        Returns:
            True if successful, False otherwise

        Example:
            ```python
            device.ns_rescan()
            True
            ```
        """
        if not self.controller:
            return False

        return self._run('ns-rescan', device=f'/dev/{self.controller}', arguments=kwargs).succeeded

    def discover(self, **kwargs: str | None) -> dict:
        """Discover NVMeoF subsystems.

        Discovers available NVMe over Fabrics subsystems:
        - TCP transport discovery
        - RDMA transport discovery
        - Fibre Channel discovery
        - Discovery controller queries

        Returns:
            Dictionary of discovered subsystems

        Examples:
            ```python
            # Discover TCP subsystems
            device.discover(**{'--transport': 'tcp', '--traddr': '192.168.1.100', '--trsvcid': '4420'})

            # Discover RDMA subsystems
            device.discover(**{'--transport': 'rdma', '--traddr': '192.168.1.100', '--trsvcid': '4420'})

            # Discover with specific host NQN
            device.discover(
                **{
                    '--transport': 'tcp',
                    '--traddr': '192.168.1.100',
                    '--hostnqn': 'nqn.2014-08.org.nvmexpress:uuid:01234567-89ab-cdef-0123-456789abcdef',
                }
            )
            ```
        """
        arguments = {'--output-format': 'json', **kwargs}

        # Use device's host NQN if available and not provided
        if self.host_nqn and '--hostnqn' not in arguments:
            arguments['--hostnqn'] = self.host_nqn

        result = self._run('discover', arguments=arguments)
        if result.failed or not result.stdout:
            return {}

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            logging.warning('Failed to parse discover JSON output')
            return {}

    def connect_all(self, **kwargs: str | None) -> bool:
        """Discover and connect to all NVMeoF subsystems.

        Discovers and connects to all available subsystems:
        - Automatic discovery and connection
        - Multiple transport support
        - Batch connection operations

        Returns:
            True if successful, False otherwise

        Examples:
            ```python
            # Connect to all TCP subsystems
            device.connect_all(**{'--transport': 'tcp', '--traddr': '192.168.1.100', '--trsvcid': '4420'})

            # Connect with authentication
            device.connect_all(
                **{'--transport': 'tcp', '--traddr': '192.168.1.100', '--dhchap-secret': 'DHHC-1:00:...'}
            )
            ```
        """
        arguments = kwargs.copy()

        # Use device's host NQN if available and not provided
        if self.host_nqn and '--hostnqn' not in arguments:
            arguments['--hostnqn'] = self.host_nqn

        return self._run('connect-all', arguments=arguments).succeeded

    def connect(self, **kwargs: str | None) -> bool:
        """Connect to specific NVMeoF subsystem.

        Connects to a specific NVMe over Fabrics subsystem:
        - Manual subsystem connection
        - Transport-specific parameters
        - Authentication support
        - Quality of Service settings

        Returns:
            True if successful, False otherwise

        Examples:
            ```python
            # Connect to TCP subsystem
            device.connect(
                **{
                    '--transport': 'tcp',
                    '--traddr': '192.168.1.100',
                    '--trsvcid': '4420',
                    '--nqn': 'nqn.2016-06.io.spdk:cnode1',
                }
            )

            # Connect with authentication
            device.connect(
                **{
                    '--transport': 'tcp',
                    '--traddr': '192.168.1.100',
                    '--nqn': 'nqn.2016-06.io.spdk:cnode1',
                    '--dhchap-secret': 'DHHC-1:00:...',
                }
            )

            # Connect with duplicate path detection
            device.connect(
                **{
                    '--transport': 'tcp',
                    '--traddr': '192.168.1.100',
                    '--nqn': 'nqn.2016-06.io.spdk:cnode1',
                    '--duplicate-connect': None,
                }
            )
            ```
        """
        arguments = kwargs.copy()

        # Use device's host NQN if available and not provided
        if self.host_nqn and '--hostnqn' not in arguments:
            arguments['--hostnqn'] = self.host_nqn

        return self._run('connect', arguments=arguments).succeeded

    def disconnect(self, nqn: str, **kwargs: str | None) -> bool:
        """Disconnect from specific NVMeoF subsystem.

        Disconnects from a specific NVMe over Fabrics subsystem:
        - Graceful disconnection
        - Subsystem-specific targeting
        - Connection cleanup

        Args:
            nqn: NVMe Qualified Name of subsystem to disconnect

        Returns:
            True if successful, False otherwise

        Examples:
            ```python
            # Disconnect specific subsystem
            device.disconnect('nqn.2016-06.io.spdk:cnode1')

            # Force disconnect
            device.disconnect('nqn.2016-06.io.spdk:cnode1', **{'--force': None})
            ```
        """
        arguments = {'--nqn': nqn, **kwargs}

        return self._run('disconnect', arguments=arguments).succeeded

    def disconnect_all(self, **kwargs: str | None) -> bool:
        """Disconnect from all NVMeoF subsystems.

        Disconnects from all connected NVMe over Fabrics subsystems:
        - Bulk disconnection operation
        - Complete cleanup
        - All transport types

        Returns:
            True if successful, False otherwise

        Examples:
            ```python
            # Disconnect all subsystems
            device.disconnect_all()

            # Force disconnect all
            device.disconnect_all(**{'--force': None})
            ```
        """
        return self._run('disconnect-all', arguments=kwargs).succeeded
