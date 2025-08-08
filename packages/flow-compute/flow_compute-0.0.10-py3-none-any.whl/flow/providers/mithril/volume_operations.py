"""Shared volume operations for Mithril provider.

This module provides DRY volume mounting logic used by both:
1. Startup scripts (for volumes attached at instance creation)
2. Runtime mount operations (for hot-mounting to running instances)

The abstraction handles:
- Device detection (both /dev/vd* and /dev/xvd* naming)
- Filesystem detection and formatting
- Mount operations with proper error handling
- Permission setting
"""

import textwrap


class VolumeOperations:
    """Encapsulates volume mount operations for Mithril instances."""

    @staticmethod
    def generate_mount_script(
        volume_index: int,
        mount_path: str,
        volume_id: str | None = None,
        format_if_needed: bool = True,
        add_to_fstab: bool = True,
        is_file_share: bool = False,
    ) -> str:
        """Generate shell script for mounting a volume.

        Args:
            volume_index: Index of the volume (0-based), determines device letter
            mount_path: Path where volume should be mounted
            volume_id: Optional volume ID for file shares
            format_if_needed: Whether to format unformatted volumes
            add_to_fstab: Whether to add to /etc/fstab for persistence
            is_file_share: Whether this is a file share (NFS) vs block storage

        Returns:
            Shell script that mounts the volume
        """
        if is_file_share:
            return VolumeOperations._generate_file_share_mount(volume_index, mount_path, volume_id)
        else:
            return VolumeOperations._generate_block_mount(
                volume_index, mount_path, format_if_needed, add_to_fstab
            )

    @staticmethod
    def _generate_block_mount(
        volume_index: int, mount_path: str, format_if_needed: bool, add_to_fstab: bool
    ) -> str:
        """Generate mount script for block storage."""
        device_letter = chr(100 + volume_index)  # d, e, f, ...

        # Core device detection and mount logic
        device_detection = textwrap.dedent(f"""
            # Detect device name (AWS Nitro uses /dev/vd*, older instances use /dev/xvd*)
            DEVICE=""
            for device in /dev/vd{device_letter} /dev/xvd{device_letter}; do
                if [ -b "$device" ]; then
                    DEVICE="$device"
                    break
                fi
            done
            
            # Wait for device if not immediately available
            if [ -z "$DEVICE" ]; then
                echo "Waiting for volume device to appear..."
                TIMEOUT=60
                ELAPSED=0
                while [ -z "$DEVICE" ] && [ $ELAPSED -lt $TIMEOUT ]; do
                    for device in /dev/vd{device_letter} /dev/xvd{device_letter}; do
                        if [ -b "$device" ]; then
                            DEVICE="$device"
                            break
                        fi
                    done
                    if [ -z "$DEVICE" ]; then
                        sleep 5
                        ELAPSED=$((ELAPSED + 5))
                        echo "  Waiting... ($ELAPSED/$TIMEOUT seconds)"
                    fi
                done
            fi
            
            if [ -z "$DEVICE" ]; then
                echo "ERROR: Volume device not found after $TIMEOUT seconds"
                echo "  Expected: /dev/vd{device_letter} or /dev/xvd{device_letter}"
                exit 1
            fi
            
            echo "Found volume device: $DEVICE"
        """).strip()

        # Formatting logic (conditional)
        format_logic = ""
        if format_if_needed:
            format_logic = textwrap.dedent("""
                # Check if volume needs formatting
                if ! blkid "$DEVICE" >/dev/null 2>&1; then
                    echo "Formatting new volume $DEVICE..."
                    mkfs.ext4 -F "$DEVICE"
                else
                    echo "Volume $DEVICE already formatted"
                fi
            """).strip()

        # fstab logic (conditional)
        fstab_logic = ""
        if add_to_fstab:
            fstab_logic = textwrap.dedent(f"""
                # Add to fstab for persistence
                if ! grep -q "$DEVICE" /etc/fstab; then
                    echo "$DEVICE {mount_path} ext4 defaults,nofail,x-systemd.device-timeout=10 0 2" >> /etc/fstab
                    echo "Added $DEVICE to /etc/fstab"
                fi
            """).strip()

        # Combine all parts
        script_parts = [
            f"# Mount volume to {mount_path}",
            f"echo 'Mounting volume at {mount_path}...'",
            "",
            device_detection,
            "",
        ]

        if format_logic:
            script_parts.extend([format_logic, ""])

        script_parts.extend(
            [
                "# Create mount point and mount volume",
                f"mkdir -p {mount_path}",
                f'mount "$DEVICE" {mount_path}',
                f"chmod 755 {mount_path}",
                "",
            ]
        )

        if fstab_logic:
            script_parts.extend([fstab_logic, ""])

        script_parts.extend(
            [
                "# Verify mount succeeded",
                f"if mountpoint -q {mount_path}; then",
                f"    echo 'Volume mounted successfully at {mount_path}'",
                f"    df -h {mount_path}",
                "else",
                f"    echo 'ERROR: Failed to mount volume at {mount_path}'",
                "    exit 1",
                "fi",
            ]
        )

        return "\n".join(script_parts)

    @staticmethod
    def _generate_file_share_mount(
        volume_index: int, mount_path: str, volume_id: str | None
    ) -> str:
        """Generate mount script for file shares (NFS)."""
        nfs_endpoint = (
            f"fileshare-{volume_id}.mithril.internal"
            if volume_id
            else f"fileshare-{volume_index}.mithril.internal"
        )

        return textwrap.dedent(f"""
            # Mount file share to {mount_path}
            echo 'Mounting file share at {mount_path}...'
            
            # Install NFS client if needed
            if ! command -v mount.nfs >/dev/null; then
                echo "Installing NFS client..."
                export DEBIAN_FRONTEND=noninteractive
                apt-get update -qq && apt-get install -y -qq nfs-common
            fi
            
            # Create mount point
            mkdir -p {mount_path}
            
            # Mount with optimized NFS options
            mount -t nfs4 -o nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2 \\
                {nfs_endpoint}:/ {mount_path}
            
            # Add to fstab for persistence
            if ! grep -q "{nfs_endpoint}" /etc/fstab; then
                echo "{nfs_endpoint}:/ {mount_path} nfs4 nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,_netdev 0 0" >> /etc/fstab
            fi
            
            # Verify mount
            if mountpoint -q {mount_path}; then
                echo 'File share mounted successfully at {mount_path}'
                chmod 755 {mount_path}
            else
                echo 'ERROR: Failed to mount file share at {mount_path}'
                exit 1
            fi
        """).strip()

    @staticmethod
    def get_device_letter_from_volumes(existing_volumes: list) -> str:
        """Calculate next available device letter based on existing volumes.

        Args:
            existing_volumes: List of currently attached volumes

        Returns:
            Next available device letter (d, e, f, ...)
        """
        # Start at 'd' and increment based on volume count
        return chr(100 + len(existing_volumes))
