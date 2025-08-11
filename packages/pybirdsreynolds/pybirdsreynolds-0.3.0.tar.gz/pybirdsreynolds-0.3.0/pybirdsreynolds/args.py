"""
pygitscrum argparse gestion
"""

import argparse
import sys
import textwrap

def restricted_int(min_val, max_val):
    def validator(x):
        x = int(x)
        if x < min_val or x > max_val:
            raise argparse.ArgumentTypeError(f"{x} is not in range [{min_val}, {max_val}]")
        return x
    return validator

def restricted_int_min(min_val):
    def validator(x):
        x = int(x)
        if x < min_val:
            raise argparse.ArgumentTypeError(f"{x} is less than the minimum allowed value {min_val}")
        return x
    return validator

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
    my_parser.add_argument(
        "--max_speed",
        type=restricted_int(0,100),
        default=10,
        help="Maximum speed of birds (integer between 0 and 100, default: 10)"
    )
    my_parser.add_argument(
        "--neighbor_radius",
        type=restricted_int_min(0),
        default=50,
        help="Distance to detect neighbors (default: 50)"
    )    
    my_parser.add_argument(
        "--num_points",
        type=restricted_int(1,1000),
        default=500,
        help="Number of agents (default: 500)"
    )  
    my_parser.add_argument(
        "--width",
        type=restricted_int(200,1500),
        default=1000,
        help="Width of the area (integer between 200 and 1500, default: 1000)"
    )
    my_parser.add_argument(
        "--height",
        type=restricted_int(300,1000),
        default=500,
        help="Width of the area (integer between 300 and 1000, default: 500)"
    )
    my_parser.add_argument(
        "--refresh_ms",
        type=restricted_int_min(10),
        default=10,
        help="Refresh time in milliseconds (default: 10)"
    )    
    my_parser.add_argument(
        "--random_speed",
        type=restricted_int(0,100),
        default=10,
        help="% Speed variation ratio of max (integer between 0 and 100, default: 10)"
    )
    my_parser.add_argument(
        "--random_angle",
        type=restricted_int(0,360),
        default=10,
        help="Angle variation in degrees (integer between 0 and 360, default: 10)"
    )
    my_parser.add_argument(
        "--sep_weight",
        type=restricted_int(0,10),
        default=1,
        help="Separation weight (integer between 0 and 10, default: 1)"
    )
    my_parser.add_argument(
        "--align_weight",
        type=restricted_int(0,10),
        default=1,
        help="Alignment weight (integer between 0 and 10, default: 1)"
    )
    my_parser.add_argument(
        "--coh_weight",
        type=restricted_int(0,10),
        default=1,
        help="Cohesion weight  (integer between 0 and 10, default: 1)"
    )
    my_parser.add_argument("--no-color", action="store_true", help="Disable colors, use grayscale (default: False)")
    my_parser.add_argument("--interactive", action="store_true", help="Interactive mode (default: False)")
    my_parser.add_argument("--points", action="store_true", help="Display boids as single pixels instead of directional triangles (default: False)")
    my_parser.add_argument(
        "--size",
        type=restricted_int(1,3),
        default=1,
        help="Visual size of birds (integer between 1 and 3, default: 1)"
    )

    args = my_parser.parse_args()
    return args
