import argparse
import mywatering.temperature as temperature
import mywatering.watering as watering
import mywatering.common as common


def measure_temperature(args: dict) -> None:
    if args.wait_random_time is not None:
        common.random_wait(args.wait_random_time)
    temperature.main(args)


def water_plants(args: dict) -> None:
    if args.wait_random_time is not None:
        common.random_wait(args.wait_random_time)
    watering.main(args)


def main() -> None:
    parser = argparse.ArgumentParser(description="MyWatering client")
    subparsers = parser.add_subparsers(title="Subcommands")

    # measure_temperature
    parser_temp = subparsers.add_parser(
        "temperature", help="Measure temperature and humidity."
    )
    parser_temp.add_argument(
        "-s", "--server", type=str, help="Server host", required=True
    )
    parser_temp.add_argument(
        "-c", "--client-number", type=str, help="Client number", required=True
    )
    parser_temp.add_argument("-u", "--user", type=str, help="Username", required=True)
    parser_temp.add_argument(
        "-p", "--password", type=str, help="Password", required=True
    )
    parser_temp.add_argument(
        "-w", "--wait-random-time", type=int, help="Wait random time up to provided value in seconds before run", required=False
    )
    parser_temp.set_defaults(func=measure_temperature)

    # water_plants
    parser_water = subparsers.add_parser("water", help="Water plants.")
    parser_water.add_argument(
        "-s", "--server", type=str, help="Server host", required=True
    )
    parser_water.add_argument(
        "-c", "--client-number", type=str, help="Client number", required=True
    )
    parser_water.add_argument("-u", "--user", type=str, help="Username", required=True)
    parser_water.add_argument(
        "-p", "--password", type=str, help="Password", required=True
    )
    parser_water.add_argument(
        "-w", "--wait-random-time", type=int, help="Wait random time up to provided value in seconds before run", required=False
    )
    parser_water.set_defaults(func=water_plants)

    args = parser.parse_args()
    if "func" in args:
        args.func(args)
    else:
        parser.print_usage()


if __name__ == "__main__":
    main()
