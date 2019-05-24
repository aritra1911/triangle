import argparse
import sys

def parse_cli():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "layers",
            type=int,
            help="number of layers"
        )
        parser.add_argument(
            "-a", "--animate",
            action="store_true",
            help="render a zoom in animation"
        )
        parser.add_argument(
            "-s", "--save-image",
            action="store_true",
            help="render only the first frame"
        )
        args = parser.parse_args()

        if args.layers is None:
            parser.print_help()
            sys.exit(1)

        if args.layers < 2:
            print("Triangle fractals must have at least 2 layers")
            sys.exit(1)

        return args

    except argparse.ArgumentError as err:
        print(str(err))
        sys.exit(1)

def get_configuration(args):
    config = {
        "animate": args.animate or not args.save_image,
        "layers": args.layers
    }

    return config
