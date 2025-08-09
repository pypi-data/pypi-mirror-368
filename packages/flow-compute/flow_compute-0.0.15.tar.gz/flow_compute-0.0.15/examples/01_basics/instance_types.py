#!/usr/bin/env python3
"""List available GPU instances matching criteria.

This example demonstrates how to:
1. Search for available GPU instances
2. Filter by instance type and region
3. Display pricing and availability information
4. Show GPU specifications and memory

Prerequisites:
- Flow SDK installed (`pip install flow-sdk`)
- Mithril API key configured (`flow init`)

How to run:
    # List all available H100s
    python list_available_instances.py

    # List specific instance type
    python list_available_instances.py --type h100

    # Filter by region
    python list_available_instances.py --region us-west-1

Expected output:
- Lists matching instances with pricing
- Shows GPU memory and count
- Displays regional availability
- Sorted by price (lowest first)
"""

import flow
from flow import Flow
import sys
import argparse
from typing import Optional


def main():
    """List available GPU instances based on criteria."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="List available GPU instances")
    parser.add_argument(
        "--type", default="h100", help="Instance type to search for (e.g., h100, a100, 8xh100)"
    )
    parser.add_argument(
        "--region", default=None, help="Filter by region (e.g., us-west-1, us-central-1)"
    )
    parser.add_argument(
        "--max-price", type=float, default=None, help="Maximum price per hour in USD"
    )
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of results to show")

    args = parser.parse_args()

    print(f"Searching for available {args.type} instances...")
    if args.region:
        print(f"Region filter: {args.region}")
    if args.max_price:
        print(f"Max price: ${args.max_price}/hour")
    print()

    try:
        # Create Flow client
        with Flow() as client:
            # Build search criteria
            criteria = {"instance_type": args.type}

            if args.region:
                criteria["region"] = args.region

            if args.max_price:
                criteria["max_price"] = args.max_price

            # Find available instances
            instances = client.find_instances(criteria, limit=args.limit)

            if not instances:
                print("No instances found matching your criteria.")
                print("\nSuggestions:")
                print("- Try a different region")
                print("- Increase max price limit")
                print("- Use a different instance type")
                return 1

            # Display results
            print(f"Found {len(instances)} available instances:\n")
            print(
                f"{'Region':<15} {'Instance Type':<20} {'Price/Hour':<12} {'GPUs':<6} {'GPU Memory':<12} {'Available':<10}"
            )
            print("-" * 95)

            for inst in instances:
                # Format instance details
                region = inst.get("region", "Unknown")
                instance_type = inst["instance_type"]
                price = f"${inst['price_per_hour']:.2f}"
                gpu_count = inst.get("gpu_count", 1)
                gpu_memory = (
                    f"{inst.get('gpu_memory_gb', 'N/A')}GB" if inst.get("gpu_memory_gb") else "N/A"
                )
                available = inst.get("available_quantity", "Unknown")

                print(
                    f"{region:<15} {instance_type:<20} {price:<12} {gpu_count:<6} {gpu_memory:<12} {available:<10}"
                )

            # Show summary
            print(f"\nLowest price: ${min(inst['price_per_hour'] for inst in instances):.2f}/hour")
            print(f"Highest price: ${max(inst['price_per_hour'] for inst in instances):.2f}/hour")

            # Show example command
            cheapest = min(instances, key=lambda x: x["price_per_hour"])
            print(f"\nTo launch the cheapest instance:")
            print(
                f'  flow run "nvidia-smi" --instance-type "{cheapest["instance_type"]}" --region "{cheapest.get("region", "auto")}"'
            )

            return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
