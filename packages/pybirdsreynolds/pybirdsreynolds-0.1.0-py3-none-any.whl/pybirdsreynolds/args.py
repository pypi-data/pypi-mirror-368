"""
pygitscrum argparse gestion
"""

import argparse
import sys
import textwrap

def compute_args():
    """
    Parse command line arguments and return them.
    """
    my_parser = argparse.ArgumentParser(
        description=textwrap.dedent("""pybirdsreynolds - interactive simulation of bird flocking behavior using Reynolds rules
            space to pause/unpause,
            enter to iterate
        """),       
        epilog=textwrap.dedent("""
            Full documentation at: <https://github.com/thib1984/pybirdsreynolds>.
            Report bugs to <https://github.com/thib1984/pybirdsreynolds/issues>.
            MIT Licence.
            Copyright (c) 2025 thib1984.
            This is free software: you are free to change and redistribute it.
            There is NO WARRANTY, to the extent permitted by law.
            Written by thib1984.
        """),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    
    # Ajout des arguments modifiables par l'utilisateur :
    my_parser.add_argument("--max_speed", type=float, default=10, help="Maximum speed of agents (default: 10)")
    my_parser.add_argument("--neighbor_radius", type=float, default=50, help="Distance to detect neighbors (default: 50)")
    my_parser.add_argument("--num_points", type=int, default=500, help="Number of agents (default: 500)")
    my_parser.add_argument("--width", type=int, default=1000, help="Width of the area (default: 1000)")
    my_parser.add_argument("--heigth", type=int, default=500, help="Height of the area (default: 500)")
    my_parser.add_argument("--refresh_ms", type=int, default=1, help="Refresh time in milliseconds (default: 1)")
    my_parser.add_argument("--random_speed", type=float, default=0.1, help="Speed variation ratio (default: 0.1)")
    my_parser.add_argument("--random_angle", type=float, default=10, help="Angle variation in degrees (default: 10)")
    my_parser.add_argument("--sep_weight", type=float, default=1, help="Separation weight (default: 1)")
    my_parser.add_argument("--align_weight", type=float, default=1, help="Alignment weight (default: 1)")
    my_parser.add_argument("--coh_weight", type=float, default=1, help="Cohesion weight (default: 1)")
    my_parser.add_argument("--no-color", action="store_true", help="Disable colors, use grayscale (default: False)")
    my_parser.add_argument("--interactive", action="store_true", help="Interactive mode (default: False)")
    
    args = my_parser.parse_args()
    return args
