# jarvis_launcher.py - Main launcher untuk JARVIS AI Assistant dengan UI
import os
import sys
import signal
import webbrowser
import threading
import time
from datetime import datetime
from dotenv import load_dotenv
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from colorama import init, Fore, Style

# Initialize colorama for Windows support
init()

# Load environment variables
load_dotenv()

console = Console()

class JarvisLauncher:
    def __init__(self):
        self.processes = []
        self.is_running = False
        self.start_time = None
        
    def display_banner(self):
        """Display JARVIS ASCII art banner"""
        banner = """
        ╔══════════════════════════════════════════════════════════════╗
        ║     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗               ║
        ║     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝               ║
        ║     ██║███████║██████╔╝██║   ██║██║███████╗               ║
        ║██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║               ║
        ║╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║               ║
        ║ ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝               ║
        ║                                                             ║
        ║         Just A Rather Very Intelligent System              ║
        ║              AI Assistant with ElevenLabs                  ║
        ╚══════════════════════════════════════════════════════════════╝
        """
        console.print(banner, style="bold cyan")
    
    def check_requirements(self):
        """Check if all required services are configured"""
        console.print("\n[yellow]🔍 Checking system requirements...[/yellow]")
        
        requirements = {
            "ELEVENLABS_API_KEY": os.getenv("ELEVENLABS_API_KEY"),
            "AGENT_ID": os.getenv("AGENT_ID"),
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        }
        
        table = Table(title="System Requirements", show_header=True)
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        
        all_ok = True
        for key, value in requirements.items():
            if value:
                table.add_row(key, "✅ Configured")
            else:
                table.add_row(key, "❌ Missing")
                all_ok = False
        
        console.print(table)
        
        # Check Python packages
        console.print("\n[yellow]📦 Checking Python packages...[/yellow]")
        required_packages = [
            "elevenlabs", "flask", "websockets", "openai",
            "pyaudio", "opencv-python", "rich"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            console.print(f"[red]Missing packages: {', '.join(missing_packages)}[/red]")
            console.print("[yellow]Install them with: pip install -r requirement.txt[/yellow]")
            all_ok = False
        else:
            console.print("[green]✅ All required packages installed[/green]")
        
        return all_ok
    
    def start_backend(self):
        """Start Flask backend server"""
        console.print("\n[cyan]🚀 Starting Flask backend server...[/cyan]")
        try:
            # Create app.py if not exists (save the UI HTML)
            if not os.path.exists("templates"):
                os.makedirs("templates")
            
            # Start Flask server
            self.flask_process = subprocess.Popen(
                [sys.executable, "app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes.append(self.flask_process)
            time.sleep(3)  # Wait for server to start
            console.print("[green]✅ Backend server started on http://localhost:5000[/green]")
            return True
        except Exception as e:
            console.print(f"[red]❌ Failed to start backend: {e}[/red]")
            return False
    
    def start_websocket(self):
        """Start WebSocket server"""
        console.print("[cyan]🔌 Starting WebSocket server...[/cyan]")
        try:
            # WebSocket is started by app.py
            console.print("[green]✅ WebSocket server started on ws://localhost:8765[/green]")
            return True
        except Exception as e:
            console.print(f"[red]❌ Failed to start WebSocket: {e}[/red]")
            return False
    
    def open_browser(self):
        """Open web browser with the UI"""
        console.print("[cyan]🌐 Opening web browser...[/cyan]")
        time.sleep(2)
        webbrowser.open("http://localhost:5000")
        console.print("[green]✅ Browser opened[/green]")
    
    def monitor_system(self):
        """Monitor system status"""
        try:
            import psutil
            
            layout = Layout()
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="body"),
                Layout(name="footer", size=3)
            )
            
            while self.is_running:
                # System stats
                cpu = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                # Update time
                uptime = datetime.now() - self.start_time if self.start_time else "N/A"
                
                # Create status table
                table = Table(title="System Status", show_header=True)
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")
                
                table.add_row("Status", "🟢 Running")
                table.add_row("Uptime", str(uptime).split('.')[0])
                table.add_row("CPU Usage", f"{cpu}%")
                table.add_row("Memory Usage", f"{memory.percent}%")
                table.add_row("Backend", "http://localhost:5000")
                table.add_row("WebSocket", "ws://localhost:8765")
                
                console.clear()
                self.display_banner()
                console.print(table)
                console.print("\n[yellow]Press Ctrl+C to stop JARVIS[/yellow]")
                
                time.sleep(5)
        except Exception as e:
            console.print(f"[red]Monitor error: {e}[/red]")
    
    def start(self):
        """Start JARVIS system"""
        self.display_banner()
        
        # Check requirements
        if not self.check_requirements():
            console.print("\n[red]⚠️  Please configure all requirements before starting[/red]")
            return False
        
        # Start services
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            
            task = progress.add_task("[cyan]Starting JARVIS systems...", total=3)
            
            # Start backend
            if self.start_backend():
                progress.update(task, advance=1)
            else:
                return False
            
            # Start WebSocket
            if self.start_websocket():
                progress.update(task, advance=1)
            else:
                return False
            
            # Open browser
            self.open_browser()
            progress.update(task, advance=1)
        
        self.is_running = True
        self.start_time = datetime.now()
        
        console.print("\n[bold green]✨ JARVIS is now online![/bold green]")
        console.print("[cyan]You can now interact with JARVIS through the web interface[/cyan]")
        
        # Start monitoring in a separate thread
        monitor_thread = threading.Thread(target=self.monitor_system, daemon=True)
        monitor_thread.start()
        
        return True
    
    def stop(self):
        """Stop JARVIS system"""
        console.print("\n[yellow]Shutting down JARVIS...[/yellow]")
        
        self.is_running = False
        
        # Terminate all processes
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        
        console.print("[green]✅ JARVIS shutdown complete[/green]")
        console.print("[cyan]Thank you for using JARVIS AI Assistant![/cyan]")
    
    def signal_handler(self, sig, frame):
        """Handle Ctrl+C signal"""
        self.stop()
        sys.exit(0)

def main():
    """Main entry point"""
    launcher = JarvisLauncher()
    
    # Set up signal handler
    signal.signal(signal.SIGINT, launcher.signal_handler)
    
    try:
        if launcher.start():
            # Keep the program running
            while launcher.is_running:
                time.sleep(1)
    except KeyboardInterrupt:
        launcher.stop()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        launcher.stop()

if __name__ == "__main__":
    main()