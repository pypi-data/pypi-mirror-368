#!/usr/bin/env python3
"""
Agent Runner - Runtime Execution
===============================

Basic runtime execution for agent packages.
This provides actual agent execution for the beta release.
"""

import os
import json
import subprocess
import signal
import time
from pathlib import Path
from typing import Dict, Any, Optional
import threading

class AgentRunner:
    """
    Runs agent packages locally
    
    Provides basic execution of built agent packages.
    This is a simplified implementation for beta release.
    """
    
    def __init__(self):
        """Initialize the agent runner"""
        self.running_agents = {}  # tag -> process
        self.agent_logs = {}      # tag -> log file
    
    def run(self, package_tag: str, manifest_path: str, layers_dir: str) -> bool:
        """
        Run an agent package
        
        Args:
            package_tag: Package tag to run
            manifest_path: Path to package manifest
            layers_dir: Directory containing package layers
            
        Returns:
            bool: True if agent started successfully
        """
        try:
            # Load manifest
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Create runtime environment
            runtime_dir = self._create_runtime_env(layers_dir, manifest)
            
            # Start agent process
            process = self._start_agent_process(runtime_dir, manifest)
            
            if process:
                self.running_agents[package_tag] = process
                print(f"Agent {package_tag} started successfully")
                print(f"  Entrypoint: {manifest.get('entrypoint', 'unknown')}")
                print(f"  Ports: {manifest.get('ports', [])}")
                print(f"  Press Ctrl+C to stop")
                return True
            else:
                print(f"Failed to start agent {package_tag}")
                return False
                
        except Exception as e:
            print(f"Error running agent {package_tag}: {e}")
            return False
    
    def stop(self, package_tag: str) -> bool:
        """
        Stop a running agent
        
        Args:
            package_tag: Package tag to stop
            
        Returns:
            bool: True if agent stopped successfully
        """
        if package_tag in self.running_agents:
            process = self.running_agents[package_tag]
            try:
                process.terminate()
                process.wait(timeout=5)
                del self.running_agents[package_tag]
                print(f"Agent {package_tag} stopped")
                return True
            except subprocess.TimeoutExpired:
                process.kill()
                del self.running_agents[package_tag]
                print(f"Agent {package_tag} force stopped")
                return True
            except Exception as e:
                print(f"Error stopping agent {package_tag}: {e}")
                return False
        else:
            print(f"Agent {package_tag} not running")
            return False
    
    def stop_all(self):
        """Stop all running agents"""
        for tag in list(self.running_agents.keys()):
            self.stop(tag)
    
    def list_running(self) -> Dict[str, Any]:
        """
        List all running agents
        
        Returns:
            Dict[str, Any]: Information about running agents
        """
        running = {}
        for tag, process in self.running_agents.items():
            running[tag] = {
                "pid": process.pid,
                "status": "running" if process.poll() is None else "stopped",
                "returncode": process.returncode
            }
        return running
    
    def _create_runtime_env(self, layers_dir: str, manifest: Dict[str, Any]) -> str:
        """
        Create runtime environment from package layers
        
        Args:
            layers_dir: Directory containing package layers
            manifest: Package manifest
            
        Returns:
            str: Path to runtime environment
        """
        # Create temporary runtime directory
        import tempfile
        runtime_dir = tempfile.mkdtemp(prefix="agent_runtime_")
        
        # Copy layers to runtime environment
        layers_path = Path(layers_dir)
        runtime_path = Path(runtime_dir)
        
        # Copy each layer
        for layer_dir in layers_path.iterdir():
            if layer_dir.is_dir():
                layer_dest = runtime_path / layer_dir.name
                if layer_dest.exists():
                    import shutil
                    shutil.rmtree(layer_dest)
                import shutil
                shutil.copytree(layer_dir, layer_dest)
        
        # Create runtime configuration
        runtime_config = {
            "manifest": manifest,
            "runtime_dir": runtime_dir,
            "created": time.time()
        }
        
        config_path = runtime_path / "runtime_config.json"
        with open(config_path, 'w') as f:
            json.dump(runtime_config, f, indent=2)
        
        return runtime_dir
    
    def _start_agent_process(self, runtime_dir: str, manifest: Dict[str, Any]) -> Optional[subprocess.Popen]:
        """
        Start agent process
        
        Args:
            runtime_dir: Runtime environment directory
            manifest: Package manifest
            
        Returns:
            Optional[subprocess.Popen]: Process object if started successfully
        """
        try:
            # Get entrypoint command
            entrypoint = manifest.get('entrypoint', '')
            if not entrypoint:
                print("No entrypoint specified in manifest")
                return None
            
            # Set up environment variables
            env = os.environ.copy()
            for key, value in manifest.get('environment', {}).items():
                env[key] = value
            
            # Change to runtime directory
            os.chdir(runtime_dir)
            
            # Start process
            process = subprocess.Popen(
                entrypoint.split(),
                cwd=runtime_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Start log monitoring in background
            def monitor_logs():
                while process.poll() is None:
                    output = process.stdout.readline()
                    if output:
                        print(f"[AGENT] {output.strip()}")
                    error = process.stderr.readline()
                    if error:
                        print(f"[AGENT ERROR] {error.strip()}")
            
            log_thread = threading.Thread(target=monitor_logs, daemon=True)
            log_thread.start()
            
            return process
            
        except Exception as e:
            print(f"Error starting agent process: {e}")
            return None
    
    def __del__(self):
        """Cleanup on deletion"""
        self.stop_all()

# Global runner instance
_runner = AgentRunner()

def get_runner() -> AgentRunner:
    """Get global agent runner instance"""
    return _runner

# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\nShutting down agents...")
    _runner.stop_all()
    exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler) 