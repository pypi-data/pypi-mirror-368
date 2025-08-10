"""Create pod command."""

import os
import sys
from typing import Optional

import click
from rich.prompt import Confirm, Prompt
from rich.text import Text

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from lium_sdk import ExecutorInfo, Lium, Template
from ..utils import (console, handle_errors, loading_status,
                     resolve_executor_indices)


def select_executor() -> Optional[ExecutorInfo]:
    """Interactive executor selection."""
    from .ls import show_executors
    
    console.print("[yellow]Select executor:[/yellow]")
    
    lium = Lium()
    with loading_status("Loading Executors", "Executors loaded"):
        executors = lium.ls()

    if not executors:
        console.print("[red]No executors available[/red]")
        return None

    show_executors(executors, limit=20)

    choice = Prompt.ask(
        "[cyan]Select executor by number[/cyan]",
        choices=[str(i) for i in range(1, len(executors) + 1)],
        default="1"
    )

    chosen_executor = executors[int(choice) - 1]
    console.print(f"[green]Selected: {chosen_executor.huid}[/green]")
    return chosen_executor


def select_template(filter_text: Optional[str] = None) -> Optional[Template]:
    """Interactive template selection."""
    from .templates import show_templates

    console.print("[yellow]Select template:[/yellow]")

    lium = Lium()
    with loading_status("Loading Templates", "Templates loaded"):
        templates = lium.templates(filter_text)

    if not templates:
        console.print("[red]No templates available[/red]")
        return None

    show_templates(templates, numbered=True)

    choice = Prompt.ask(
        "Select template by number or enter text to filter",
        default="1"
    )
    
    if not choice.isnumeric():
        return select_template(choice)

    chosen_template = templates[int(choice) - 1]
    text = Text(f"Selected: {chosen_template.docker_image}:{chosen_template.docker_image_tag}", style="dim")
    console.print(text, markup=False, highlight=False)
    return chosen_template

def show_pod_created(pod_info: dict) -> None:
    """Display created pod info."""
    pod_id = pod_info.get('huid', pod_info.get('id', pod_info.get('name', 'N/A')))
    console.print(f"[green]✓[/green] Pod '{pod_id}' created")
    
    if pod_info.get('ssh_cmd'):
        console.print(f"SSH: {pod_info['ssh_cmd']}")
    elif "ssh" in pod_info:
        console.print(f"SSH: {pod_info['ssh']}")
    
    console.print("[dim]Use 'lium ps' to check status[/dim]")


@click.command("up")
@click.argument("executor_id", required=False)
@click.option("--name", "-n", help="Custom pod name")
@click.option("--template_id", "-t", help="Template ID")
@click.option("--wait", "-w", is_flag=True, help="Wait for pod to be ready")
@click.option("--timeout", default=300, help="Wait timeout in seconds (default: 300)")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
@handle_errors
def up_command(executor_id: Optional[str], name: Optional[str], template_id: Optional[str], wait: bool, timeout: int, yes: bool):
    """Create a new GPU pod on an executor.
    
    EXECUTOR_ID: Executor UUID, HUID, or index from last 'lium ls'. 
    If not provided, shows interactive selection.
    
    Examples:
      lium up                       # Interactive executor selection
      lium up cosmic-hawk-f2        # Create pod on specific executor
      lium up 1                     # Create pod on executor #1 from last ls
      lium up -w cosmic-hawk-f2     # Create and wait for pod to be ready
      lium up --name my-pod         # Create with custom name
    """
    lium = Lium()

    # Resolve executor ID if it's an index
    executor = None
    if executor_id and executor_id.isdigit():
        resolved_ids, error_msg = resolve_executor_indices([executor_id])
        if error_msg:
            console.print(f"[red]{error_msg}[/red]")
            if not resolved_ids:
                return
        if resolved_ids:
            executor_id = resolved_ids[0]
    
    # Get or select executor
    if executor_id:
        with loading_status("Loading executor", "Executor loaded"):
            executor = lium.get_executor(executor_id)
    if not executor:
        executor = select_executor()
        if not executor:
            return

    # Get or select template
    template = None
    if template_id:
        template = lium.get_template(template_id)
    if not template:
        template = select_template()
        if not template:
            return

    # Use executor HUID as default name
    if not name:
        name = executor.huid

    # Confirm creation
    if not yes:
        confirm_msg = f"Acquire pod on {executor.huid} ({executor.gpu_count}×{executor.gpu_type}) at ${executor.price_per_hour:.2f}/h?"
        if not Confirm.ask(confirm_msg, default=False):
            console.print("[yellow]Cancelled[/yellow]")
            return
    
    with loading_status(f"Creating pod {name}", "Pod created"):
        pod_info = lium.up(executor_id=executor.id, pod_name=name, template_id=template.id)

    # Wait for pod to be ready if requested
    if wait:
        console.print(f"[dim]Pod created. Waiting for pod to be ready (timeout: {timeout}s)...[/dim]")
        
        with console.status("[bold green]Waiting for pod..."):
            pod_id = pod_info.get('id') or pod_info.get('name', '')
            pod = lium.wait_ready(pod_id, timeout=timeout)
        
        if pod:
            show_pod_created({"huid": pod.huid, "name": pod.name, "status": pod.status, "ssh_cmd": pod.ssh_cmd})
        else:
            console.print(f"[yellow]⚠ Pod not ready after {timeout}s timeout[/yellow]")
            show_pod_created(pod_info)
    else:
        show_pod_created(pod_info)
