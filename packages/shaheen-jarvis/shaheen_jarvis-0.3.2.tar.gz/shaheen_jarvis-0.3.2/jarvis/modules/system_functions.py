"""
System-related functions for Shaheen-Jarvis framework.
Includes system information, IP address, and shell command execution.
"""

import os
import platform
import psutil
import subprocess
import requests
from typing import Optional


def system_info() -> str:
    """Get system information."""
    try:
        # Basic system info
        info = []
        info.append(f"System: {platform.system()}")
        info.append(f"OS: {platform.platform()}")
        info.append(f"Architecture: {platform.architecture()[0]}")
        info.append(f"Processor: {platform.processor()}")
        info.append(f"Python Version: {platform.python_version()}")
        
        # Memory info
        memory = psutil.virtual_memory()
        info.append(f"Total RAM: {memory.total / (1024**3):.1f} GB")
        info.append(f"Available RAM: {memory.available / (1024**3):.1f} GB")
        info.append(f"RAM Usage: {memory.percent}%")
        
        # Disk info
        disk = psutil.disk_usage('/')
        info.append(f"Total Disk: {disk.total / (1024**3):.1f} GB")
        info.append(f"Free Disk: {disk.free / (1024**3):.1f} GB")
        info.append(f"Disk Usage: {(disk.used / disk.total) * 100:.1f}%")
        
        # CPU info
        info.append(f"CPU Cores: {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count()} logical")
        info.append(f"CPU Usage: {psutil.cpu_percent(interval=1)}%")
        
        return "System Information:\n" + "\n".join(info)
    
    except Exception as e:
        return f"Error getting system information: {str(e)}"


def get_ip_address() -> str:
    """Get the current IP address."""
    try:
        # Get public IP
        public_ip_services = [
            "https://api.ipify.org",
            "https://icanhazip.com",
            "https://httpbin.org/ip"
        ]
        
        public_ip = None
        for service in public_ip_services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    if "ipify" in service:
                        public_ip = response.text.strip()
                    elif "icanhazip" in service:
                        public_ip = response.text.strip()
                    elif "httpbin" in service:
                        public_ip = response.json().get('origin', '').split(',')[0].strip()
                    break
            except:
                continue
        
        # Get local IP
        import socket
        local_ip = None
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            pass
        
        result = []
        if local_ip:
            result.append(f"Local IP: {local_ip}")
        if public_ip:
            result.append(f"Public IP: {public_ip}")
        
        if result:
            return "IP Address Information:\n" + "\n".join(result)
        else:
            return "Could not determine IP address"
    
    except Exception as e:
        return f"Error getting IP address: {str(e)}"


def run_shell_command(command: str, safe_mode: bool = True) -> str:
    """
    Execute a shell command.
    
    Args:
        command: Shell command to execute
        safe_mode: If True, only allow safe commands
        
    Returns:
        Command output or error message
    """
    if safe_mode:
        # List of potentially dangerous commands to block
        dangerous_commands = [
            'rm', 'del', 'format', 'shutdown', 'reboot', 'halt',
            'sudo', 'su', 'passwd', 'chmod', 'chown', 'mkfs',
            'fdisk', 'dd', 'killall', 'pkill'
        ]
        
        # Check if command contains dangerous keywords
        command_lower = command.lower()
        for dangerous in dangerous_commands:
            if dangerous in command_lower:
                return f"Command blocked for security reasons: '{command}' contains potentially dangerous operation '{dangerous}'"
    
    try:
        # Execute command with timeout
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = []
        if result.stdout:
            output.append(f"Output:\n{result.stdout}")
        if result.stderr:
            output.append(f"Errors:\n{result.stderr}")
        if result.returncode != 0:
            output.append(f"Return code: {result.returncode}")
        
        if output:
            return "\n".join(output)
        else:
            return "Command executed successfully (no output)"
    
    except subprocess.TimeoutExpired:
        return "Command timed out after 10 seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"


def get_network_info() -> str:
    """Get network interface information."""
    try:
        import psutil
        
        info = []
        info.append("Network Interfaces:")
        
        # Get network interfaces
        interfaces = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        
        for interface_name, addresses in interfaces.items():
            if interface_name in stats:
                stat = stats[interface_name]
                info.append(f"\n{interface_name}:")
                info.append(f"  Status: {'Up' if stat.isup else 'Down'}")
                info.append(f"  Speed: {stat.speed} Mbps" if stat.speed > 0 else "  Speed: Unknown")
                
                for addr in addresses:
                    if addr.family == 2:  # IPv4
                        info.append(f"  IPv4: {addr.address}")
                        if addr.netmask:
                            info.append(f"  Netmask: {addr.netmask}")
                    elif addr.family == 17:  # MAC address
                        info.append(f"  MAC: {addr.address}")
        
        # Get network I/O statistics
        net_io = psutil.net_io_counters()
        if net_io:
            info.append(f"\nNetwork Statistics:")
            info.append(f"  Bytes sent: {net_io.bytes_sent / (1024**2):.1f} MB")
            info.append(f"  Bytes received: {net_io.bytes_recv / (1024**2):.1f} MB")
            info.append(f"  Packets sent: {net_io.packets_sent}")
            info.append(f"  Packets received: {net_io.packets_recv}")
        
        return "\n".join(info)
    
    except Exception as e:
        return f"Error getting network information: {str(e)}"


def get_process_info(process_name: Optional[str] = None) -> str:
    """
    Get information about running processes.
    
    Args:
        process_name: Specific process name to search for (optional)
        
    Returns:
        Process information
    """
    try:
        import psutil
        
        if process_name:
            # Search for specific process
            matching_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                if process_name.lower() in proc.info['name'].lower():
                    matching_processes.append(proc.info)
            
            if matching_processes:
                info = [f"Processes matching '{process_name}':"]
                for proc in matching_processes[:10]:  # Limit to 10 results
                    info.append(f"  PID {proc['pid']}: {proc['name']} (CPU: {proc['cpu_percent']:.1f}%, Memory: {proc['memory_percent']:.1f}%)")
                return "\n".join(info)
            else:
                return f"No processes found matching '{process_name}'"
        
        else:
            # Show top processes by CPU usage
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                processes.append(proc.info)
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            info = ["Top processes by CPU usage:"]
            for proc in processes[:10]:
                info.append(f"  PID {proc['pid']}: {proc['name']} (CPU: {proc['cpu_percent']:.1f}%, Memory: {proc['memory_percent']:.1f}%)")
            
            return "\n".join(info)
    
    except Exception as e:
        return f"Error getting process information: {str(e)}"


# For compatibility with the module loading system
__all__ = [
    "system_info",
    "get_ip_address",
    "run_shell_command",
    "get_network_info",
    "get_process_info"
]
