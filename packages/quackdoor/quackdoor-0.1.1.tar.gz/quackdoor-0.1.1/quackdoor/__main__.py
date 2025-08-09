"""
Main Entrypoint
"""

import argparse
from quackdoor.payload import read_payload
from quackdoor.encoder import encode_payload, build_python_exec_command
from quackdoor.builder import build_ducky_script


def main() -> int:
    """
    main()
    """
    parser = argparse.ArgumentParser(
        description="Inject Python into runnable DuckyScript"
    )
    parser.add_argument("input", help="Path to the python script to inject")
    parser.add_argument(
        "-o", "--output", default="payload.txt", help="[Optional] Output file"
    )
    parser.add_argument(
        "-r",
        "--requirements",
        nargs="*",
        default=[],
        help="[Optional] Space delimited list of external package dependencies.",
    )
    parser.add_argument(
        "-p",
        "--pip-time",
        default="",
        help="[Optional] Amount of delay to allow for external dependency installation.",
    )

    args = parser.parse_args()

    try:
        raw = read_payload(args.input)
        encoded = encode_payload(raw)
        exec_cmd = build_python_exec_command(encoded)
        ducky_script = build_ducky_script(
            exec_cmd, pip_time=args.pip_time, requirements=args.requirements
        )

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(ducky_script)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"[!] {str(e)}")
        return 1

    print(f"[+] DuckyScript written to {args.output}")

    return 0


if __name__ == "__main__":
    main()
