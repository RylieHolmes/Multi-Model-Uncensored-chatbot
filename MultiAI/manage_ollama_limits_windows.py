import os
import sys
import ctypes
import subprocess
from rich.console import Console
from rich.panel import Panel

# --- Configuration for Ollama on Windows ---

# List the CPU cores you want Ollama to be restricted to.
# To find your cores, open Task Manager > Performance > CPU.
# The number of "Logical processors" is your total core count (e.g., 0-15 for 16 cores).
# Example for first 4 cores: [0, 1, 2, 3]
CPU_AFFINITY_CORES = [0, 1, 2, 3, 4, 5, 6, 7]

# Set the process priority. Options: "Idle", "BelowNormal", "Normal", "AboveNormal", "High"
# "BelowNormal" is recommended to prevent system freezes.
PROCESS_PRIORITY = "BelowNormal"

# Set how many models can be loaded into VRAM at once.
# This is crucial for managing GPU memory. 1 is the safest value.
MAX_LOADED_MODELS = 1
# -----------------------------------------

console = Console()

def is_admin():
    """Check if the script is running with Administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Re-run the script with Administrator privileges."""
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
    except Exception as e:
        console.print(f"[bold red]Error elevating to admin: {e}[/bold red]")
    sys.exit(0)

def apply_windows_limits():
    """
    Generates and executes a PowerShell script to apply CPU affinity and priority
    limits to the Ollama process on Windows.
    """
    console.print(Panel(
        "[bold yellow]Ollama Resource Limiter for Windows[/bold yellow]\n\n"
        "This script will apply CPU and memory limits to the Ollama service.\n"
        "It requires [bold red]Administrator[/bold red] privileges to modify a running service.",
        title="[bold cyan]Description[/bold cyan]",
        border_style="cyan"
    ))

    if not is_admin():
        console.print("[yellow]Administrator privileges required. Re-launching...[/yellow]")
        run_as_admin()

    console.print("\n[green]✓ Running with Administrator privileges.[/green]")

    # --- Step 1: Generate the PowerShell script ---
    # Convert the list of cores to a bitmask integer required by PowerShell
    affinity_mask = sum(2**core for core in CPU_AFFINITY_CORES)

    # Map friendly priority names to the integer values SetPriority expects
    priority_map = {
        "Idle": 64,
        "BelowNormal": 16384,
        "Normal": 32,
        "AboveNormal": 32768,
        "High": 128
    }
    priority_value = priority_map.get(PROCESS_PRIORITY, 32) # Default to Normal

    powershell_script = f"""
# This script is auto-generated to apply resource limits to ollama.exe
# Suppress error output for cleaner execution
$ErrorActionPreference = "SilentlyContinue"

Write-Host "Searching for ollama.exe process..."
$process = Get-Process ollama -ErrorAction SilentlyContinue

if ($null -eq $process) {{
    Write-Host "Error: ollama.exe is not running. Please start the Ollama application first."
    exit 1
}}

Write-Host "Found Ollama process with ID: $($process.Id)"

# --- Apply CPU Affinity ---
$affinityMask = {affinity_mask}
$process.ProcessorAffinity = $affinityMask
$coreList = "{', '.join(map(str, CPU_AFFINITY_CORES))}"
Write-Host "Successfully set CPU affinity to cores: $coreList"

# --- Apply Process Priority ---
$priorityValue = {priority_value}
$priorityName = "{PROCESS_PRIORITY}"
try {{
    $wmiProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $($process.Id)"
    $wmiProcess | Invoke-CimMethod -MethodName SetPriority -Arguments @{{Priority = $priorityValue}}
    Write-Host "Successfully set process priority to: $priorityName"
}} catch {{
    Write-Host "Warning: Could not set process priority. This may happen on some systems."
}}

# --- Set Environment Variable for VRAM Limit ---
$envVarName = "OLLAMA_MAX_LOADED_MODELS"
$envVarValue = "{MAX_LOADED_MODELS}"
[System.Environment]::SetEnvironmentVariable($envVarName, $envVarValue, [System.EnvironmentVariableTarget]::User)
Write-Host "Successfully set OLLAMA_MAX_LOADED_MODELS environment variable to '$envVarValue'."
Write-Host "You must RESTART the Ollama application for this VRAM limit to take effect."

Write-Host "Script finished."
"""

    # --- Step 2: Save and execute the PowerShell script ---
    script_path = "temp_ollama_limiter.ps1"
    try:
        with open(script_path, "w") as f:
            f.write(powershell_script)

        console.print("\n[yellow]Executing PowerShell script to apply limits...[/yellow]\n")
        # Execute the script
        result = subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path],
            capture_output=True, text=True
        )

        # Print the output from the PowerShell script
        console.print(Panel(result.stdout, title="[cyan]PowerShell Output[/cyan]", border_style="cyan"))

        if result.stderr:
            console.print(Panel(result.stderr, title="[red]PowerShell Errors[/red]", border_style="red"))

        console.print("\n[bold green]✓ Limits applied successfully![/bold green]")
        console.print("[bold yellow]Important:[/bold yellow] The CPU limits are active now, but you must [bold]RESTART the Ollama application[/bold] for the VRAM limit to work.")

    except Exception as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")
    finally:
        # Clean up the temporary script file
        if os.path.exists(script_path):
            os.remove(script_path)

if __name__ == "__main__":
    apply_windows_limits()