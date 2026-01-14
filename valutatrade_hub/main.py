from .cli.interface import CLIInterface
from .infra.logging_config import setup_logging


def main():
    setup_logging()
    cli = CLIInterface()
    cli.run()


if __name__ == '__main__':
    main()
