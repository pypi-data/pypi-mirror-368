#!/usr/bin/env python3
"""
Ping Sweeper - A CLI tool for subnet ping sweeping
Usage: python pingsweeper.py -s <subnet> [-text <filename>]
Example: python pingsweeper.py -s 192.168.1.0/24 -text results.txt
"""

import asyncio
import argparse
import ipaddress
import platform
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple, Set, Dict, Optional


class PingSweeper:
    def __init__(self):
        self.system = platform.system().lower()
        self.ping_cmd = self._get_ping_command()
        
    def _get_ping_command(self) -> List[str]:
        """Get the appropriate ping command for the current OS"""
        if self.system == "windows":
            return ["ping", "-n", "1", "-w", "500"]  # 1 ping, .500 second timeout
        else:  # Linux/Unix/macOS
            return ["ping", "-c", "1", "-W", "1"]     # 1 ping, 1 second timeout
    
    def _ping_host(self, ip: str) -> Tuple[str, bool]:
        """Ping a single host and return the result"""
        try:
            cmd = self.ping_cmd + [ip]
            result = subprocess.run(
                cmd, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL,
                timeout=3
            )
            return (ip, result.returncode == 0)
        except (subprocess.TimeoutExpired, OSError):
            return (ip, False)
    
    def _resolve_hostname(self, ip: str) -> Optional[str]:
        """Resolve hostname for an IP address using DNS lookup"""
        try:
            # Set a timeout for the DNS lookup
            socket.setdefaulttimeout(.5)
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except (socket.herror, socket.timeout, OSError):
            return None
        finally:
            socket.setdefaulttimeout(None)
    
    async def _ping_and_resolve_async(self, executor: ThreadPoolExecutor, ip: str) -> Tuple[str, bool, Optional[str]]:
        """Async wrapper for ping and hostname resolution"""
        loop = asyncio.get_event_loop()
        
        # First ping the host
        ip_addr, is_alive = await loop.run_in_executor(executor, self._ping_host, ip)
        
        # If alive, try to resolve hostname
        hostname = None
        if is_alive:
            hostname = await loop.run_in_executor(executor, self._resolve_hostname, ip)
        
        return (ip_addr, is_alive, hostname)
    
    async def sweep_subnet(self, subnet: str, max_workers: int = 50) -> Tuple[Dict[str, Optional[str]], Set[str], float]:
        """
        Sweep a subnet and return alive/dead hosts and execution time
        
        Args:
            subnet: Subnet in CIDR notation (e.g., '192.168.1.0/24')
            max_workers: Maximum number of concurrent ping operations
            
        Returns:
            Tuple of (alive_hosts_dict, dead_hosts, execution_time)
            alive_hosts_dict: {ip: hostname} where hostname can be None
        """
        try:
            network = ipaddress.IPv4Network(subnet, strict=False)
        except ipaddress.AddressValueError as e:
            raise ValueError(f"Invalid subnet format: {e}")
        
        hosts = [str(ip) for ip in network.hosts()]
        if not hosts:
            # Handle single host case (e.g., /32)
            hosts = [str(network.network_address)]
        
        print(f"Starting ping sweep of {subnet}")
        print(f"Scanning {len(hosts)} hosts with {max_workers} concurrent threads...")
        print("Performing DNS lookups for responding hosts...")
        print("-" * 60)
        
        start_time = time.time()
        alive_hosts = {}  # {ip: hostname}
        dead_hosts = set()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Create tasks for all hosts
            tasks = [
                self._ping_and_resolve_async(executor, host) 
                for host in hosts
            ]
            
            # Execute all pings and DNS lookups concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in results:
                if isinstance(result, Exception):
                    continue
                    
                ip, is_alive, hostname = result
                if is_alive:
                    alive_hosts[ip] = hostname
                    hostname_display = f" ({hostname})" if hostname else " (no hostname)"
                    print(f"✓ {ip}{hostname_display} - ALIVE")
                else:
                    dead_hosts.add(ip)
        
        execution_time = time.time() - start_time
        return alive_hosts, dead_hosts, execution_time
    
    def print_summary(self, alive_hosts: Dict[str, Optional[str]], dead_hosts: Set[str], execution_time: float):
        """Print a summary of the ping sweep results"""
        total_hosts = len(alive_hosts) + len(dead_hosts)
        hosts_with_names = sum(1 for hostname in alive_hosts.values() if hostname is not None)
        
        print("\n" + "=" * 60)
        print("PING SWEEP SUMMARY")
        print("=" * 60)
        print(f"Total hosts scanned: {total_hosts}")
        print(f"Hosts alive: {len(alive_hosts)}")
        print(f"Hosts dead: {len(dead_hosts)}")
        print(f"Hosts with hostnames: {hosts_with_names}")
        print(f"Execution time: {execution_time:.2f} seconds")
        print(f"Average time per host: {execution_time/total_hosts:.3f} seconds")
        
        if alive_hosts:
            print(f"\nAlive hosts ({len(alive_hosts)}):")
            # Sort by IP address
            sorted_hosts = sorted(alive_hosts.items(), key=lambda x: ipaddress.IPv4Address(x[0]))
            
            # Calculate column widths for nice formatting
            max_ip_len = max(len(ip) for ip in alive_hosts.keys())
            
            for ip, hostname in sorted_hosts:
                if hostname:
                    print(f"  {ip:<{max_ip_len}} -> {hostname}")
                else:
                    print(f"  {ip:<{max_ip_len}} -> (no hostname)")
    
    def save_results(self, filename: str, subnet: str, alive_hosts: Dict[str, Optional[str]], 
                    dead_hosts: Set[str], execution_time: float):
        """Save results to a text file"""
        try:
            hosts_with_names = sum(1 for hostname in alive_hosts.values() if hostname is not None)
            
            with open(filename, 'w') as f:
                f.write("PING SWEEP RESULTS\n")
                f.write("=" * 50 + "\n")
                f.write(f"Subnet: {subnet}\n")
                f.write(f"Scan date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total hosts scanned: {len(alive_hosts) + len(dead_hosts)}\n")
                f.write(f"Hosts alive: {len(alive_hosts)}\n")
                f.write(f"Hosts dead: {len(dead_hosts)}\n")
                f.write(f"Hosts with hostnames: {hosts_with_names}\n")
                f.write(f"Execution time: {execution_time:.2f} seconds\n")
                f.write("\n" + "-" * 30 + "\n")
                
                if alive_hosts:
                    f.write("ALIVE HOSTS:\n")
                    # Sort by IP address
                    sorted_hosts = sorted(alive_hosts.items(), key=lambda x: ipaddress.IPv4Address(x[0]))
                    
                    # Calculate column width for alignment
                    max_ip_len = max(len(ip) for ip in alive_hosts.keys())
                    
                    for ip, hostname in sorted_hosts:
                        if hostname:
                            f.write(f"{ip:<{max_ip_len}} -> {hostname}\n")
                        else:
                            f.write(f"{ip:<{max_ip_len}} -> (no hostname)\n")
                
                if dead_hosts:
                    f.write(f"\nDEAD HOSTS ({len(dead_hosts)} total):\n")
                    # Only write first 20 dead hosts to keep file manageable
                    dead_list = sorted(dead_hosts, key=lambda x: ipaddress.IPv4Address(x))
                    for host in dead_list[:20]:
                        f.write(f"{host}\n")
                    if len(dead_hosts) > 20:
                        f.write(f"... and {len(dead_hosts) - 20} more\n")
            
            print(f"\nResults saved to: {filename}")
            
        except IOError as e:
            print(f"Error saving to file: {e}", file=sys.stderr)


async def main():
    parser = argparse.ArgumentParser(
        description="Ping Sweeper - Efficiently scan subnets for alive hosts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pingsweeper.py -s 192.168.1.0/24
  python pingsweeper.py -s 10.0.0.0/16 -text results.txt
  python pingsweeper.py -s 172.16.1.0/24 -text scan_results.txt
        """
    )
    
    parser.add_argument(
        '-s', '--subnet',
        required=True,
        help='Subnet to scan in CIDR notation (e.g., 192.168.1.0/24)'
    )
    
    parser.add_argument(
        '-text',
        metavar='FILENAME',
        help='Save results to a text file'
    )
    
    args = parser.parse_args()
    
    sweeper = PingSweeper()
    
    try:
        alive_hosts, dead_hosts, execution_time = await sweeper.sweep_subnet(args.subnet)
        
        sweeper.print_summary(alive_hosts, dead_hosts, execution_time)
        
        if args.text:
            sweeper.save_results(args.text, args.subnet, alive_hosts, dead_hosts, execution_time)
            
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nScan interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if sys.version_info < (3, 7):
        print("This script requires Python 3.7 or higher", file=sys.stderr)
        sys.exit(1)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(1)