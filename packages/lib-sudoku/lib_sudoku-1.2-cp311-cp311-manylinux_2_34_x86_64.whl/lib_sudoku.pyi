from .lib_sudoku import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    class PuzzleReader:
        def __init__(self, filename: str, from_url: bool) -> PuzzleReader:
            """
            Takes in the name or url of a csv file containing sudoku puzzles in the format "puzzle,solution" and returns a PuzzleReader object.

            Args:
                filename (str): The name of the csv file.
                from_url (bool): Whether the given file is from a url.

            Returns:
                PuzzleReader object.

            Raises:
                FileNotFoundError: If a local file does not exist.
                RuntimeError: If a url does not point to a valid puzzle file.
                ValueError: If the file is malformed.
            """
            ...

        def get_unsolved_puzz(self, line_number: int) -> bytearray:
            """
            Takes in the line number of an unsolved puzzle from the csv file and returns the puzzle as a list.

            Args:
                line_number (int): The line number of the puzzle.

            Returns:
                list: The unsolved puzzle.

            Raises:
                ValueError: If the line number does not correspond to a puzzle in the csv file.
            """
            ...

        def get_solved_puzz(self, line_number: int) -> bytearray:
            """
            Takes in the line number of a solved puzzle from the csv file and returns the puzzle as a list.

            Args:
                line_number (int): The line number of the puzzle.

            Returns:
                list: The solved puzzle.

            Raises:
                ValueError: If the line number does not correspond to a puzzle in the csv file.
            """
            ...

    def print_puzz(puzzle: list) -> None:
        """
        Prints a puzzle in the correct format.
        :param puzzle:
        """

    def synchronous_speedtest(puzzle_reader: PuzzleReader, verbose: bool):
        """
        Takes in a puzzle reader object and solves all the puzzles. It will also check all the solutions to confirm that the solver is current.

        Args:
            puzzle_reader (PuzzleReader): The puzzle reader object.
            verbose (bool, optional): Whether the function should print all unsolved and solved puzzles. This is good for debugging, but it adds a lot of overhead. Defaults to False.
        """
        ...

    def async_speedtest(puzzle_reader: PuzzleReader, verbose: bool):
        """
        Takes in a puzzle reader object and solves all the puzzles with multithreading. It should be much faster. The function will also check all the solutions to confirm that the solver is current.

        Args:
            puzzle_reader (PuzzleReader): The puzzle reader object.
            verbose (bool, optional): Whether the function should print all unsolved and solved puzzles. This is good for debugging, but it adds a lot of overhead. Defaults to False.
        """
        ...

    def solve(puzzle: list) -> bytearray:
        """
        Takes in a puzzle in the form of a row-major list and returns a solved version.

        Args:
            puzzle (list): The puzzle in the form of an 81-length row-major list.

        returns:
            bytearray: The solved puzzle.
        """
        ...

    def gen_unsolved(num_hints: int) -> bytearray:
        """
        Generates a random incomplete puzzle with the specified number of hints.

        Args:
            num_hints (int): The number of hints the final puzzle will have. Must be between 23 and 40.

        returns:
        bytearray: The puzzle with the specified number of hints.
        """
        ...
