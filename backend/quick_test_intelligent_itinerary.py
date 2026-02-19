"""
Quick Test for Intelligent Itinerary Endpoint
Tests the unified AI itinerary generation system
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
from rich.json import JSON

console = Console()

BASE_URL = "http://localhost:8000/api/generate"


def print_section(title):
    """Print section header"""
    console.print(f"\n[bold cyan]{'=' * 80}[/bold cyan]")
    console.print(f"[bold yellow]{title}[/bold yellow]")
    console.print(f"[bold cyan]{'=' * 80}[/bold cyan]\n")


def test_intelligent_itinerary():
    """Test the main intelligent itinerary endpoint"""
    print_section("Testing: POST /intelligent-itinerary")
    
    console.print("[bold]Testing comprehensive intelligent itinerary generation...[/bold]\n")
    
    payload = {
        "location": "Paris",
        "latitude": 48.8566,
        "longitude": 2.3522,
        "budget": 1500,
        "duration": 7,
        "group_size": 2,
        "mood": "relaxed",
        "travel_type": "cultural",
        "include_hotels": True,
        "include_restaurants": True,
        "include_enrichment": True,
        "student_friendly": True,
        "max_distance_km": 50.0
    }
    
    console.print("[cyan]Request Payload:[/cyan]")
    console.print(JSON(json.dumps(payload, indent=2)))
    console.print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/intelligent-itinerary",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            console.print("[bold green]✓ Success![/bold green]\n")
            
            # Overview
            console.print("[bold]📊 Overview:[/bold]")
            overview = Table(show_header=False, box=box.ROUNDED)
            overview.add_column("Field", style="cyan")
            overview.add_column("Value", style="green")
            
            overview.add_row("Location", data["location"])
            overview.add_row("Duration", f"{data['duration_days']} days")
            overview.add_row("Group Size", f"{data['group_size']} people")
            overview.add_row("Generation Time", f"{data['generation_time_seconds']}s")
            overview.add_row("Features Included", f"{len(data['included_features'])}")
            
            console.print(overview)
            console.print()
            
            # Budget Breakdown
            if data.get("budget_breakdown"):
                console.print("[bold]💰 Budget Breakdown:[/bold]")
                budget = data["budget_breakdown"]
                
                budget_table = Table(box=box.ROUNDED)
                budget_table.add_column("Category", style="cyan")
                budget_table.add_column("Amount", style="green", justify="right")
                budget_table.add_column("Percentage", style="yellow", justify="right")
                
                budget_table.add_row(
                    "Total Budget",
                    f"${budget['total_budget']:.2f}",
                    "100%"
                )
                budget_table.add_row(
                    "Accommodation",
                    f"${budget['stay_budget']:.2f}",
                    f"{budget['allocation_percentages']['stay']}%"
                )
                budget_table.add_row(
                    "Food",
                    f"${budget['food_budget']:.2f}",
                    f"{budget['allocation_percentages']['food']}%"
                )
                budget_table.add_row(
                    "Travel",
                    f"${budget['travel_budget']:.2f}",
                    f"{budget['allocation_percentages']['travel']}%"
                )
                budget_table.add_row(
                    "Activities",
                    f"${budget['activity_budget']:.2f}",
                    f"{budget['allocation_percentages']['activities']}%"
                )
                
                console.print(budget_table)
                console.print(f"[dim]Budget Tier: {budget['budget_tier']} | "
                             f"Per Person/Day: ${budget['per_person_per_day']:.2f}[/dim]\n")
            
            # Itinerary
            if data.get("optimized_itinerary"):
                console.print("[bold]📅 Optimized Itinerary:[/bold]")
                
                for day in data["optimized_itinerary"][:3]:  # Show first 3 days
                    console.print(f"[bold cyan]Day {day['day']}: {day['title']}[/bold cyan]")
                    if day.get('morning_activity'):
                        console.print(f"  🌅 Morning: {day['morning_activity']}")
                    if day.get('afternoon_activity'):
                        console.print(f"  ☀️  Afternoon: {day['afternoon_activity']}")
                    if day.get('evening_activity'):
                        console.print(f"  🌙 Evening: {day['evening_activity']}")
                    if day.get('recommended_restaurant'):
                        console.print(f"  🍽️  Restaurant: {day['recommended_restaurant']}")
                    if day.get('budget_estimate'):
                        console.print(f"  💵 Budget: ${day['budget_estimate']:.2f}")
                    console.print()
                
                if len(data["optimized_itinerary"]) > 3:
                    console.print(f"[dim]... and {len(data['optimized_itinerary']) - 3} more days[/dim]\n")
            
            # Hotels
            if data.get("ranked_hotels"):
                console.print("[bold]🏨 Top Hotels:[/bold]")
                hotel_table = Table(box=box.SIMPLE)
                hotel_table.add_column("Rank", style="cyan", width=4)
                hotel_table.add_column("Name", style="green")
                hotel_table.add_column("Rating", justify="center")
                hotel_table.add_column("Score", justify="center")
                hotel_table.add_column("Distance", justify="right")
                
                for hotel in data["ranked_hotels"][:5]:
                    hotel_table.add_row(
                        str(hotel["rank"]),
                        hotel["name"],
                        f"{hotel['rating']:.1f}⭐",
                        f"{hotel['score']:.2f}",
                        f"{hotel['distance_km']:.1f}km"
                    )
                
                console.print(hotel_table)
                console.print()
            
            # Restaurants
            if data.get("ranked_restaurants"):
                console.print("[bold]🍽️  Top Restaurants:[/bold]")
                restaurant_table = Table(box=box.SIMPLE)
                restaurant_table.add_column("Rank", style="cyan", width=4)
                restaurant_table.add_column("Name", style="green")
                restaurant_table.add_column("Rating", justify="center")
                restaurant_table.add_column("Score", justify="center")
                
                for rest in data["ranked_restaurants"][:5]:
                    restaurant_table.add_row(
                        str(rest["rank"]),
                        rest["name"],
                        f"{rest['rating']:.1f}⭐",
                        f"{rest['score']:.2f}"
                    )
                
                console.print(restaurant_table)
                console.print()
            
            # Route Optimization
            if data.get("route_order"):
                console.print("[bold]🗺️  Route Optimization:[/bold]")
                route = data["route_order"]
                console.print(f"Method: {route['optimization_method']}")
                console.print(f"Total Distance: {route['total_distance_km']:.1f} km")
                console.print(f"Estimated Travel Time: {route['estimated_travel_time_hours']:.1f} hours")
                console.print(f"Ordered Route: {' → '.join(route['ordered_places'][:5])}")
                if len(route['ordered_places']) > 5:
                    console.print(f"  ... and {len(route['ordered_places']) - 5} more stops")
                console.print()
            
            # Educational Enrichment
            if data.get("educational_enrichment"):
                console.print("[bold]📚 Educational Enrichment:[/bold]")
                enrich = data["educational_enrichment"]
                console.print(f"[italic]{enrich.get('historical_summary', 'N/A')}[/italic]\n")
                
                if enrich.get('cultural_insights'):
                    console.print("[bold cyan]Cultural Insights:[/bold cyan]")
                    for insight in enrich['cultural_insights'][:3]:
                        console.print(f"  • {insight}")
                    console.print()
            
            # Books
            if data.get("recommended_books"):
                console.print("[bold]📖 Recommended Books:[/bold]")
                for book in data["recommended_books"][:3]:
                    console.print(f"  • '{book['title']}' by {book['author']} ({book['rating']}⭐)")
                console.print()
            
            # Included Features
            console.print("[bold]✨ Included Features:[/bold]")
            for feature in data["included_features"]:
                console.print(f"  ✓ {feature.replace('_', ' ').title()}")
            
            console.print()
            console.print(Panel.fit(
                "[bold green]✓ INTELLIGENT ITINERARY GENERATED SUCCESSFULLY![/bold green]\n"
                f"Generated comprehensive {data['duration_days']}-day itinerary in {data['generation_time_seconds']}s",
                box=box.DOUBLE,
                border_style="green"
            ))
            
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
    
    endpoints = [
        ("/intelligent-itinerary/health", "Health Check"),
        ("/intelligent-itinerary/features", "Features List"),
        ("/intelligent-itinerary/supported-moods", "Supported Moods"),
        ("/intelligent-itinerary/supported-travel-types", "Supported Travel Types")
    ]
    
    passed = 0
    total = len(endpoints)
    
    for endpoint, name in endpoints:
        console.print(f"[bold]Testing: {name}[/bold]")
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                console.print(f"[green]✓ {name}: Success[/green]")
                if endpoint == "/intelligent-itinerary/health":
                    console.print(f"  Status: {data['status']}")
                    console.print(f"  Subsystems: {len(data['subsystems'])} operational")
                elif endpoint == "/intelligent-itinerary/features":
                    console.print(f"  Features: {len(data['features'])}")
                elif endpoint == "/intelligent-itinerary/supported-moods":
                    console.print(f"  Moods: {len(data['moods'])}")
                elif endpoint == "/intelligent-itinerary/supported-travel-types":
                    console.print(f"  Travel Types: {len(data['travel_types'])}")
                passed += 1
            else:
                console.print(f"[red]✗ {name}: Failed ({response.status_code})[/red]")
        except Exception as e:
            console.print(f"[red]✗ {name}: Error - {e}[/red]")
        console.print()
    
    return passed, total


def main():
    """Run all tests"""
    console.print(Panel.fit(
        "[bold yellow]Intelligent Itinerary System - Test Suite[/bold yellow]\n"
        "Testing unified AI itinerary generation",
        box=box.DOUBLE
    ))
    
    # Test main endpoint
    main_test_passed = test_intelligent_itinerary()
    
    # Test utility endpoints
    utility_passed, utility_total = test_utility_endpoints()
    
    # Summary
    print_section("Test Summary")
    
    total_tests = 1 + utility_total
    total_passed = (1 if main_test_passed else 0) + utility_passed
    
    console.print(f"[bold]Results: {total_passed}/{total_tests} tests passed[/bold]\n")
    
    if total_passed == total_tests:
        console.print(Panel.fit(
            "[bold green]✓ ALL TESTS PASSED![/bold green]\n"
            "Intelligent itinerary system is working correctly.\n"
            "All 5 AI subsystems integrated successfully.",
            box=box.DOUBLE,
            border_style="green"
        ))
    else:
        console.print(Panel.fit(
            f"[bold red]✗ {total_tests - total_passed} TEST(S) FAILED[/bold red]\n"
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
