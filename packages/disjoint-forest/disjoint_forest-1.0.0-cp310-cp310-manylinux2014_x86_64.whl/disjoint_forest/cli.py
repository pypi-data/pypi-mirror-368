#!/usr/bin/env python3
"""
Command-line interface for the disjoint-forest package.
"""

import argparse
import sys
from typing import List, Optional

try:
    import disjoint_forest
except ImportError:
    print("Error: Could not import disjoint_forest module.")
    print("Please ensure the package is properly installed.")
    sys.exit(1)


def create_forest_example():
    """Create and demonstrate a simple disjoint forest."""
    print("Creating a disjoint forest with example data...")
    
    # Create a forest
    forest = disjoint_forest.DisjointForest(10)
    
    # Create some sets
    nodes = []
    for i in range(5):
        node = forest.make_set(i)
        nodes.append(node)
        print(f"Created set with data: {node.data}")
    
    print(f"\nForest size: {forest.size()}")
    print(f"Forest capacity: {forest.capacity()}")
    
    # Union some sets
    forest.union_sets(nodes[0], nodes[1])
    forest.union_sets(nodes[2], nodes[3])
    
    print("\nAfter unions:")
    for i, node in enumerate(nodes):
        rep = forest.find(node)
        print(f"Node {i} ({node.data}) -> Representative: {rep.data}")
    
    # Expand capacity
    forest.expand(5)
    print(f"\nExpanded capacity to: {forest.capacity()}")
    
    # Add more nodes
    for i in range(5, 10):
        node = forest.make_set(i)
        nodes.append(node)
        print(f"Added new set with data: {node.data}")
    
    print(f"Final forest size: {forest.size()}")
    
    return forest


def interactive_mode():
    """Run an interactive session with the disjoint forest."""
    print("Interactive Disjoint Forest Session")
    print("Type 'help' for commands, 'quit' to exit")
    print("=" * 40)
    
    forest = disjoint_forest.DisjointForest()
    nodes = []
    
    while True:
        try:
            command = input("\nforest> ").strip().lower()
            
            if command in ['quit', 'exit', 'q']:
                break
            elif command == 'help':
                print_help()
            elif command == 'status':
                print_status(forest, nodes)
            elif command.startswith('add '):
                data = command[4:].strip()
                try:
                    # Try to evaluate as Python literal
                    import ast
                    data = ast.literal_eval(data)
                except:
                    pass  # Keep as string if evaluation fails
                node = forest.make_set(data)
                nodes.append(node)
                print(f"Added node with data: {data}")
            elif command.startswith('union '):
                try:
                    parts = command[6:].split()
                    if len(parts) == 2:
                        i, j = int(parts[0]), int(parts[1])
                        if 0 <= i < len(nodes) and 0 <= j < len(nodes):
                            forest.union_sets(nodes[i], nodes[j])
                            print(f"United nodes {i} and {j}")
                        else:
                            print("Invalid node indices")
                    else:
                        print("Usage: union <index1> <index2>")
                except ValueError:
                    print("Invalid indices")
            elif command.startswith('find '):
                try:
                    i = int(command[5:])
                    if 0 <= i < len(nodes):
                        rep = forest.find(nodes[i])
                        print(f"Node {i} representative: {rep.data}")
                    else:
                        print("Invalid node index")
                except ValueError:
                    print("Invalid index")
            elif command == 'expand':
                forest.expand(5)
                print(f"Expanded capacity to {forest.capacity()}")
            elif command == 'clear':
                forest.clear()
                nodes.clear()
                print("Forest cleared")
            else:
                print("Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


def print_help():
    """Print help information."""
    print("Available commands:")
    print("  add <data>     - Add a new set with the given data")
    print("  union <i> <j>  - Union sets at indices i and j")
    print("  find <i>       - Find representative of set at index i")
    print("  status         - Show current forest status")
    print("  expand         - Expand forest capacity by 5")
    print("  clear          - Clear all sets")
    print("  help           - Show this help")
    print("  quit           - Exit the session")


def print_status(forest, nodes):
    """Print the current status of the forest."""
    print(f"Forest size: {forest.size()}")
    print(f"Forest capacity: {forest.capacity()}")
    print(f"Number of nodes: {len(nodes)}")
    
    if nodes:
        print("\nNodes:")
        for i, node in enumerate(nodes):
            try:
                rep = forest.find(node)
                print(f"  [{i}] {node.data} -> Representative: {rep.data}")
            except:
                print(f"  [{i}] {node.data} -> Invalid")
    else:
        print("No nodes created yet.")


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Disjoint Forest Data Structure CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Run interactive mode
  %(prog)s --example         # Run example demonstration
  %(prog)s --version         # Show version information
        """
    )
    
    parser.add_argument(
        '--example',
        action='store_true',
        help='Run a demonstration example'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'disjoint-forest {disjoint_forest.__version__}'
    )
    
    args = parser.parse_args()
    
    if args.example:
        create_forest_example()
    else:
        interactive_mode()


if __name__ == '__main__':
    main() 