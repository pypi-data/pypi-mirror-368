"""
Command-line interface for Itinerizer.
"""

import sys
import json
from pathlib import Path
from datetime import date, datetime
from uuid import UUID
import argparse

from . import ItineraryManager, __version__


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="itinerizer",
        description="Itinerizer - Travel Itinerary Management System"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "--storage-path",
        type=str,
        help="Custom storage path for itineraries",
        default=None
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all itineraries")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--trip-type", help="Filter by trip type")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get an itinerary")
    get_parser.add_argument("id", type=str, help="Itinerary ID")
    get_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create an itinerary")
    create_parser.add_argument("--file", type=str, required=True, help="JSON file with itinerary data")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete an itinerary")
    delete_parser.add_argument("id", type=str, help="Itinerary ID")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate an itinerary file")
    validate_parser.add_argument("file", type=str, help="JSON file to validate")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export an itinerary")
    export_parser.add_argument("id", type=str, help="Itinerary ID")
    export_parser.add_argument("--output", type=str, required=True, help="Output file path")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Initialize manager
    manager = ItineraryManager(storage_path=args.storage_path)
    
    try:
        if args.command == "list":
            itineraries = manager.search_itineraries(
                status=args.status,
                trip_type=args.trip_type
            )
            
            if not itineraries:
                print("No itineraries found.")
            else:
                print(f"Found {len(itineraries)} itinerary(ies):")
                for itin in itineraries:
                    print(f"  - {itin.id}: {itin.title} ({itin.status})")
                    print(f"    {itin.start_date} to {itin.end_date}")
                    print(f"    Travelers: {len(itin.travelers)}, Segments: {len(itin.segments)}")
        
        elif args.command == "get":
            itinerary_id = UUID(args.id)
            itinerary = manager.get_itinerary(itinerary_id)
            
            if not itinerary:
                print(f"Itinerary {args.id} not found.", file=sys.stderr)
                return 1
            
            if args.json:
                print(json.dumps(itinerary.model_dump(mode='json'), indent=2, default=str))
            else:
                print(f"Itinerary: {itinerary.title}")
                print(f"ID: {itinerary.id}")
                print(f"Status: {itinerary.status}")
                print(f"Dates: {itinerary.start_date} to {itinerary.end_date}")
                print(f"Travelers: {len(itinerary.travelers)}")
                print(f"Segments: {len(itinerary.segments)}")
                
                if itinerary.segments:
                    print("\nSegments:")
                    for seg in itinerary.segments:
                        print(f"  - {seg.type}: {seg.start_datetime.strftime('%Y-%m-%d %H:%M')}")
        
        elif args.command == "create":
            file_path = Path(args.file)
            if not file_path.exists():
                print(f"File not found: {args.file}", file=sys.stderr)
                return 1
            
            with open(file_path) as f:
                data = json.load(f)
            
            # Parse dates
            if 'start_date' in data:
                data['start_date'] = date.fromisoformat(data['start_date'])
            if 'end_date' in data:
                data['end_date'] = date.fromisoformat(data['end_date'])
            
            # Parse travelers
            from .models import Traveler
            travelers = []
            for t_data in data.get('travelers', []):
                travelers.append(Traveler.model_validate(t_data))
            data['travelers'] = travelers
            
            itinerary = manager.create_itinerary(**data)
            print(f"Created itinerary: {itinerary.id}")
        
        elif args.command == "delete":
            itinerary_id = UUID(args.id)
            if manager.delete_itinerary(itinerary_id):
                print(f"Deleted itinerary: {args.id}")
            else:
                print(f"Itinerary {args.id} not found.", file=sys.stderr)
                return 1
        
        elif args.command == "validate":
            file_path = Path(args.file)
            if not file_path.exists():
                print(f"File not found: {args.file}", file=sys.stderr)
                return 1
            
            with open(file_path) as f:
                data = json.load(f)
            
            from .models import Itinerary
            try:
                itinerary = Itinerary.model_validate(data)
                result = manager.validator.validate(itinerary)
                
                if result.is_valid:
                    print("✓ Itinerary is valid")
                else:
                    print("✗ Itinerary has validation errors:")
                    for error in result.errors:
                        print(f"  - {error.code}: {error.message}")
                
                if result.warnings:
                    print("\nWarnings:")
                    for warning in result.warnings:
                        print(f"  - {warning.code}: {warning.message}")
            
            except Exception as e:
                print(f"✗ Invalid itinerary format: {e}", file=sys.stderr)
                return 1
        
        elif args.command == "export":
            itinerary_id = UUID(args.id)
            itinerary = manager.get_itinerary(itinerary_id)
            
            if not itinerary:
                print(f"Itinerary {args.id} not found.", file=sys.stderr)
                return 1
            
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                json.dump(itinerary.model_dump(mode='json'), f, indent=2, default=str)
            
            print(f"Exported itinerary to: {output_path}")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())