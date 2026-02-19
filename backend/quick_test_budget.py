"""
Quick Manual Test for Budget Allocation System
Run this to manually test budget optimization with different scenarios
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

BASE_URL = "http://localhost:8000/api/optimize"


def print_section(title):
    """Print section header"""
    console.print(f"\n[bold cyan]{'=' * 80}[/bold cyan]")
    console.print(f"[bold yellow]{title}[/bold yellow]")
    console.print(f"[bold cyan]{'=' * 80}[/bold cyan]\n")


def test_scenario(name, total_budget, duration, group_size, custom_allocation=None):
    """Test a budget scenario"""
    console.print(f"[bold green]Testing: {name}[/bold green]")
    console.print(f"Budget: ${total_budget}, Duration: {duration} days, Group: {group_size} people\n")
    
    payload = {
        "total_budget": total_budget,
        "duration": duration,
        "group_size": group_size
    }
    
    if custom_allocation:
        payload["custom_allocation"] = custom_allocation
    
    try:
        response = requests.post(f"{BASE_URL}/budget", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Overview
            console.print("[bold]Overview:[/bold]")
            overview = Table(show_header=False, box=box.ROUNDED)
            overview.add_column("Field", style="cyan")
            overview.add_column("Value", style="green")
            
            overview.add_row("Budget Tier", data["budget_tier"].upper())
            overview.add_row("Per Person Total", f"${data['per_person_total']:.2f}")
            overview.add_row("Per Person Per Day", f"${data['per_person_per_day']:.2f}")
            overview.add_row("Group Discount", f"{(1 - data['group_discount_factor']) * 100:.0f}%")
            
            console.print(overview)
            console.print()
            
            # Budget Breakdown
            console.print("[bold]Budget Breakdown:[/bold]")
            breakdown = Table(box=box.ROUNDED)
            breakdown.add_column("Category", style="cyan", justify="left")
            breakdown.add_column("Amount", style="green", justify="right")
            breakdown.add_column("Percentage", style="yellow", justify="right")
            breakdown.add_column("Per Person", style="magenta", justify="right")
            breakdown.add_column("Per Day", style="blue", justify="right")
            
            categories = ["stay", "food", "travel", "activity"]
            category_names = ["Stay", "Food", "Travel", "Activities"]
            
            for cat, name in zip(categories, category_names):
                budget_key = f"{cat}_budget"
                pct = data["allocation_percentages"][cat]
                per_person = data["per_person"][cat]
                per_day = data["per_day"][cat]
                
                breakdown.add_row(
                    name,
                    f"${data[budget_key]:.2f}",
                    f"{pct}%",
                    f"${per_person:.2f}",
                    f"${per_day:.2f}"
                )
            
            # Total row
            total_budget = sum(data[f"{cat}_budget"] for cat in categories)
            total_pct = sum(data["allocation_percentages"][cat] for cat in categories)
            breakdown.add_row(
                "[bold]TOTAL[/bold]",
                f"[bold]${total_budget:.2f}[/bold]",
                f"[bold]{total_pct}%[/bold]",
                f"[bold]${data['per_person_total']:.2f}[/bold]",
                f"[bold]${data['per_day']['per_day']:.2f}[/bold]",
                style="bold"
            )
            
            console.print(breakdown)
            console.print()
            
            # Suggestions
            if data["suggestions"]:
                console.print("[bold]Smart Suggestions:[/bold]")
                for i, sug in enumerate(data["suggestions"], 1):
                    priority_color = {
                        "critical": "red",
                        "high": "yellow",
                        "medium": "blue",
                        "low": "white"
                    }.get(sug["priority"], "white")
                    
                    console.print(
                        f"  {i}. [{priority_color}][{sug['priority'].upper()}][/{priority_color}] "
                        f"[{sug['category'].upper()}] {sug['tip']}"
                    )
                console.print()
            
            console.print("[bold green]✓ Test passed![/bold green]\n")
            return True
            
        else:
            console.print(f"[bold red]✗ Request failed with status {response.status_code}[/bold red]")
            console.print(f"Response: {response.text}\n")
            return False
            
    except requests.exceptions.ConnectionError:
        console.print("[bold red]✗ Could not connect to backend. Is it running on localhost:8000?[/bold red]\n")
        return False
    except Exception as e:
        console.print(f"[bold red]✗ Error: {e}[/bold red]\n")
        return False


def test_utility_endpoints():
    """Test utility endpoints"""
    print_section("Testing Utility Endpoints")
    
    # Test tiers endpoint
    console.print("[bold]1. GET /budget/tiers[/bold]")
    try:
        response = requests.get(f"{BASE_URL}/budget/tiers", timeout=10)
        if response.status_code == 200:
            data = response.json()
            console.print(f"[green]✓ Found {len(data['tiers'])} budget tiers[/green]")
            for tier_name in data["tiers"]:
                console.print(f"  - {tier_name}: {data['tiers'][tier_name]['threshold']}")
        else:
            console.print(f"[red]✗ Failed with status {response.status_code}[/red]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
    console.print()
    
    # Test allocation defaults
    console.print("[bold]2. GET /budget/allocation-defaults[/bold]")
    try:
        response = requests.get(f"{BASE_URL}/budget/allocation-defaults", timeout=10)
        if response.status_code == 200:
            data = response.json()
            console.print(f"[green]✓ Default allocation:[/green]")
            for cat, pct in data["default"].items():
                console.print(f"  - {cat.capitalize()}: {pct}%")
        else:
            console.print(f"[red]✗ Failed with status {response.status_code}[/red]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
    console.print()
    
    # Test calculate per-person
    console.print("[bold]3. POST /budget/calculate-per-person[/bold]")
    try:
        response = requests.post(
            f"{BASE_URL}/budget/calculate-per-person",
            json={"total_budget": 1500, "duration": 7, "group_size": 2},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            console.print(f"[green]✓ Calculation result:[/green]")
            console.print(f"  - Per person total: ${data['per_person_total']}")
            console.print(f"  - Per person per day: ${data['per_person_per_day']}")
            console.print(f"  - Budget tier: {data['budget_tier']}")
        else:
            console.print(f"[red]✗ Failed with status {response.status_code}[/red]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
    console.print()
    
    # Test health check
    console.print("[bold]4. GET /budget/health[/bold]")
    try:
        response = requests.get(f"{BASE_URL}/budget/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            console.print(f"[green]✓ Service: {data['service']} - {data['status']}[/green]")
            console.print(f"  Features: {', '.join([k for k, v in data['features'].items() if v])}")
        else:
            console.print(f"[red]✗ Failed with status {response.status_code}[/red]")
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
    console.print()


def main():
    """Run all tests"""
    console.print(Panel.fit(
        "[bold yellow]Budget Allocation System - Quick Test Suite[/bold yellow]\n"
        "Testing budget optimization with different scenarios",
        box=box.DOUBLE
    ))
    
    passed = 0
    total = 0
    
    # Test scenarios
    print_section("Scenario 1: Backpacker Budget (Ultra Low)")
    total += 1
    if test_scenario(
        "Solo backpacker - Southeast Asia",
        total_budget=700,
        duration=14,
        group_size=1
    ):
        passed += 1
    
    print_section("Scenario 2: Student Group Trip (Low)")
    total += 1
    if test_scenario(
        "Student group - European cities",
        total_budget=2400,
        duration=10,
        group_size=4
    ):
        passed += 1
    
    print_section("Scenario 3: Moderate Budget Couple (Moderate)")
    total += 1
    if test_scenario(
        "Couple - South American adventure",
        total_budget=3000,
        duration=14,
        group_size=2
    ):
        passed += 1
    
    print_section("Scenario 4: Family Vacation (Comfortable)")
    total += 1
    if test_scenario(
        "Family of 4 - USA road trip",
        total_budget=6000,
        duration=10,
        group_size=4
    ):
        passed += 1
    
    print_section("Scenario 5: Luxury Getaway (High)")
    total += 1
    if test_scenario(
        "Luxury couple - Mediterranean cruise",
        total_budget=10000,
        duration=7,
        group_size=2
    ):
        passed += 1
    
    print_section("Scenario 6: Weekend Trip (Moderate)")
    total += 1
    if test_scenario(
        "Weekend getaway - nearby city",
        total_budget=800,
        duration=3,
        group_size=2
    ):
        passed += 1
    
    print_section("Scenario 7: Custom Allocation")
    total += 1
    if test_scenario(
        "Custom budget priorities",
        total_budget=2000,
        duration=7,
        group_size=2,
        custom_allocation={
            "stay": 50,
            "food": 20,
            "travel": 15,
            "activities": 15
        }
    ):
        passed += 1
    
    print_section("Scenario 8: Large Group (Group Discount)")
    total += 1
    if test_scenario(
        "Large student group - spring break",
        total_budget=8000,
        duration=7,
        group_size=8
    ):
        passed += 1
    
    # Test utility endpoints
    test_utility_endpoints()
    
    # Summary
    print_section("Test Summary")
    console.print(f"[bold]Results: {passed}/{total} scenarios passed[/bold]")
    
    if passed == total:
        console.print(Panel.fit(
            "[bold green]✓ ALL TESTS PASSED![/bold green]\n"
            "Budget allocation system is working correctly.",
            box=box.DOUBLE,
            border_style="green"
        ))
    else:
        console.print(Panel.fit(
            f"[bold red]✗ {total - passed} TEST(S) FAILED[/bold red]\n"
            "Please check the errors above.",
            box=box.DOUBLE,
            border_style="red"
        ))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Test interrupted by user[/yellow]")
        sys.exit(1)
