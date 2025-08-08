import logging
import click
from ostdetector.report import Detector

logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.INFO, filename='log.txt')
# logger = logging.getLogger(__name__)

# See https://click.palletsprojects.com/en/8.1.x/documentation/#help-texts
CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--output",
    "-o",
    help="The output dir where the usage of OS-Specific Tests related to the repository will be stored. "
    "By default, the information will written to `data' dir.",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, writable=True),
)
@click.argument(
    "repository",
    type=str,
)
def main(
    output, 
    repository, 
):
    """Extract the usage of OS-Specific Tests from a single Git repository `REPOSITORY`.
    The Git repository can be remote. It will be pulled locally in the folder `data`.
    Every extracted OS-Specific Tests will be written in the dir given to `-o`,
    or in the `data' if not specified.

    Example of usage:
    python main.py ricardojob/OSTDetector -o data_experiment
    """
    
    detector = Detector(repository, output)
    detector.collect()

if __name__ == "__main__":
    main()
