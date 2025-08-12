import argparse
import sys
import textwrap

def restricted_int(min_val, max_val):
    def validator(x):
        x = int(x)
        if x < min_val or x > max_val:
            raise argparse.ArgumentTypeError(f"{x} is outside the allowed range [{min_val}, {max_val}]")
        return x
    return validator

def restricted_int_min(min_val):
    def validator(x):
        x = int(x)
        if x < min_val:
            raise argparse.ArgumentTypeError(f"{x} is less than the minimum allowed value ({min_val})")
        return x
    return validator

def compute_args():
    my_parser = argparse.ArgumentParser(
        description=textwrap.dedent("""\
            pybirdsreynolds - Simulation of bird flocking behavior using Reynolds' rules.

            Controls:
             [Up/Down]    Navigate between parameters
             [Left/Right] Adjust selected parameter
             [r]          Reset all parameters
             [Space]      Toggle pause / resume
             [r]          Reset all parameters
                          to their initial values
             [n]          New generation of birds
             [Enter]      Advance the simulation by
                          one frame
            Thanks to Mehdi Moussaïd - http://www.mehdimoussaid.com/a-propos/ - https://youtu.be/xuKrkOh_mzk  
            """),
        epilog=textwrap.dedent("""\
            Full documentation:  https://github.com/thib1984/pybirdsreynolds
            Report bugs:         https://github.com/thib1984/pybirdsreynolds/issues

            License: MIT
            Copyright (c) 2025 thib1984

            This is free software: you can modify and redistribute it.
            There is NO WARRANTY, to the extent permitted by law.
            Written by thib1984.
            """),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    
    my_parser.add_argument(
        "--num_birds",
        type=restricted_int(1, 1000),
        default=500,
        help="Number of birds in the simulation (integer between 1 and 1000, default: 500)"
    )
    my_parser.add_argument(
        "--max_speed",
        type=restricted_int(1, 100),
        default=10,
        help="Maximum speed of birds (integer between 1 and 100, default: 10)"
    )
    my_parser.add_argument(
        "--neighbor_radius",
        type=restricted_int_min(0),
        default=50,
        help="Distance to detect neighbors (pixels, default: 50)"
    )
    my_parser.add_argument(
        "--sep_weight",
        type=restricted_int(0, 10),
        default=1,
        help="Separation weight (integer between 0 and 10, default: 1)"
    )
    my_parser.add_argument(
        "--align_weight",
        type=restricted_int(0, 10),
        default=1,
        help="Alignment weight (integer between 0 and 10, default: 1)"
    )
    my_parser.add_argument(
        "--coh_weight",
        type=restricted_int(0, 10),
        default=1,
        help="Cohesion weight (integer between 0 and 10, default: 1)"
    ) 
    my_parser.add_argument(
        "--random_speed",
        type=restricted_int(0, 100),
        default=10,
        help="Random speed variation ratio (percentage of max speed, integer 0 and 100, default: 10)"
    )
    my_parser.add_argument(
        "--random_angle",
        type=restricted_int(0, 360),
        default=10,
        help="Random angle variation in degrees (integer between 0 and 360, default: 10)"
    )
    my_parser.add_argument(
        "--refresh_ms",
        type=restricted_int_min(1),
        default=10,
        help="Refresh interval in milliseconds (min 10, default: 10)"
    )    
    my_parser.add_argument(
        "--width",
        type=restricted_int(200, 1500),
        default=1000,
        help="Simulation area width (integer between 200 and 1500, default: 1000)"
    )
    my_parser.add_argument(
        "--height",
        type=restricted_int(200, 1000),
        default=500,
        help="Simulation area height (integer between 200 and 1000, default: 500)"
    )


    my_parser.add_argument("--no_color", action="store_true", help="Disable colors (use monochrome display)")
    my_parser.add_argument("--points", action="store_true", help="Render birds as single points instead of triangles")
    my_parser.add_argument(
        "--size",
        type=restricted_int(1, 3),
        default=1,
        help="Visual size of birds (integer between 1 and 3, default: 1)"
    )

    return my_parser.parse_args()
