"""Tests for CLI argument validation.

This module contains tests that verify proper validation of command-line
arguments, particularly for core count valida            with patch("pdf_pycrack.main.multiprocessing.cpu_count") as mock_cpu_count, \
             patch("pdf_pycrack.main.crack_pdf_password") as mock_crack, \
             patch("pdf_pycrack.main.print_start_info"), \
             patch("pdf_pycrack.main.print_end_info"), \
             patch("pdf_pycrack.main.print_warning") as mock_print_warning:ith patch("pdf_pycrack.main.multiprocessing.cpu_count") as mock_cpu_count, \
             patch("pdf_pycrack.main.crack_pdf_password") as mock_crack, \
             patch("pdf_pycrack.main.print_start_info"), \
             patch("pdf_pycrack.main.print_end_info"), \
             patch("pdf_pycrack.main.print_warning") as mock_print_warning:and warnings.
"""

import argparse
import multiprocessing
import sys
from unittest.mock import patch

import pytest

from pdf_pycrack.cli import setup_arg_parser, validate_cores


class TestCoreValidation:
    """Test suite for CPU core count validation."""

    def test_validate_cores_positive_number(self):
        """Test that positive core numbers are accepted."""
        result = validate_cores("4")
        assert result == 4

    def test_validate_cores_zero_raises_error(self):
        """Test that zero cores raises an error."""
        with pytest.raises(
            argparse.ArgumentTypeError, match="Number of cores must be positive"
        ):
            validate_cores("0")

    def test_validate_cores_negative_raises_error(self):
        """Test that negative core numbers raise an error."""
        with pytest.raises(
            argparse.ArgumentTypeError, match="Number of cores must be positive"
        ):
            validate_cores("-1")

    def test_validate_cores_non_integer_raises_error(self):
        """Test that non-integer values raise an error."""
        with pytest.raises(
            argparse.ArgumentTypeError, match="Number of cores must be an integer"
        ):
            validate_cores("abc")

    def test_validate_cores_float_raises_error(self):
        """Test that float values raise an error."""
        with pytest.raises(
            argparse.ArgumentTypeError, match="Number of cores must be an integer"
        ):
            validate_cores("4.5")

    def test_validate_cores_accepts_large_numbers(self):
        """Test that cores larger than available are accepted in validation."""
        # The validation function should accept large numbers
        # The limiting happens in main()
        max_cores = multiprocessing.cpu_count()
        large_number = max_cores * 10
        result = validate_cores(str(large_number))
        assert result == large_number


class TestArgParser:
    """Test suite for argument parser setup."""

    def test_arg_parser_default_cores(self):
        """Test that default cores equals CPU count."""
        parser = setup_arg_parser()
        # Parse with minimal args to test defaults
        args = parser.parse_args(["test.pdf"])
        expected_cores = multiprocessing.cpu_count()
        assert args.cores == expected_cores

    def test_arg_parser_custom_cores(self):
        """Test that custom core count is parsed correctly."""
        parser = setup_arg_parser()
        args = parser.parse_args(["test.pdf", "--cores", "2"])
        assert args.cores == 2

    def test_arg_parser_invalid_cores_zero(self):
        """Test that zero cores are rejected by parser."""
        parser = setup_arg_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["test.pdf", "--cores", "0"])

    def test_arg_parser_invalid_cores_negative(self):
        """Test that negative cores are rejected by parser."""
        parser = setup_arg_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["test.pdf", "--cores", "-1"])

    def test_arg_parser_invalid_cores_string(self):
        """Test that string cores are rejected by parser."""
        parser = setup_arg_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["test.pdf", "--cores", "abc"])


class TestMainCoreWarning:
    """Test suite for core count warning in main function."""

    @patch("pdf_pycrack.main.print_warning")
    @patch("pdf_pycrack.main.print_end_info")
    @patch("pdf_pycrack.main.print_start_info")
    @patch("pdf_pycrack.main.crack_pdf_password")
    @patch("pdf_pycrack.main.multiprocessing.cpu_count")
    def test_main_warns_when_too_many_cores_requested(
        self,
        mock_cpu_count,
        mock_crack,
        mock_print_start,
        mock_print_end,
        mock_print_warning,
    ):
        """Test that main() shows warning when too many cores are requested."""
        from pdf_pycrack.main import main
        from pdf_pycrack.models.cracking_result import PasswordNotFound

        # Mock CPU count to be 4
        mock_cpu_count.return_value = 4

        # Mock the crack function to return a result
        mock_crack.return_value = PasswordNotFound(
            passwords_checked=100, passwords_per_second=10.0, elapsed_time=1.0
        )

        # Mock sys.argv to simulate command line args
        test_args = ["pdf-pycrack", "test.pdf", "--cores", "8"]
        with patch.object(sys, "argv", test_args):
            main()

        # Check that warning was printed with correct parameters
        mock_print_warning.assert_called_once()
        call_args = mock_print_warning.call_args
        assert call_args[1]["title"] == "Core Count Warning"
        assert (
            "Requested 8 cores, but only 4 cores are available"
            in call_args[1]["message"]
        )
        assert "use 4 cores instead" in call_args[1]["message"]

        # Check that suggested actions are provided
        suggested_actions = call_args[1]["suggested_actions"]
        assert len(suggested_actions) == 2
        assert "Use --cores 4" in suggested_actions[0]

        # Verify that crack_pdf_password was called with limited cores
        mock_crack.assert_called_once()
        call_args = mock_crack.call_args
        assert call_args[1]["num_processes"] == 4

    def test_main_no_warning_when_cores_within_limit(self):
        """Test that main() doesn't show warning when cores are within limit."""
        from pdf_pycrack.main import main
        from pdf_pycrack.models.cracking_result import PasswordNotFound

        with (
            patch("pdf_pycrack.main.multiprocessing.cpu_count") as mock_cpu_count,
            patch("pdf_pycrack.main.crack_pdf_password") as mock_crack,
            patch("pdf_pycrack.main.print_start_info"),
            patch("pdf_pycrack.main.print_end_info"),
            patch("pdf_pycrack.main.print_warning") as mock_print_warning,
        ):
            # Mock CPU count to be 4
            mock_cpu_count.return_value = 4

            # Mock the crack function to return a result
            mock_crack.return_value = PasswordNotFound(
                passwords_checked=100, passwords_per_second=10.0, elapsed_time=1.0
            )

            # Mock sys.argv to simulate command line args with 2 cores (within limit)
            test_args = ["pdf-pycrack", "test.pdf", "--cores", "2"]
            with patch.object(sys, "argv", test_args):
                main()

            # Check that no warning was printed
            mock_print_warning.assert_not_called()

            # Verify that crack_pdf_password was called with requested cores
            mock_crack.assert_called_once()
            call_args = mock_crack.call_args
            assert call_args[1]["num_processes"] == 2

    def test_main_uses_exact_cores_when_equal_to_max(self):
        """Test that main() uses exact cores when equal to CPU count."""
        from pdf_pycrack.main import main
        from pdf_pycrack.models.cracking_result import PasswordNotFound

        with (
            patch("pdf_pycrack.main.multiprocessing.cpu_count") as mock_cpu_count,
            patch("pdf_pycrack.main.crack_pdf_password") as mock_crack,
            patch("pdf_pycrack.main.print_start_info"),
            patch("pdf_pycrack.main.print_end_info"),
            patch("pdf_pycrack.main.print_warning") as mock_print_warning,
        ):
            # Mock CPU count to be 4
            mock_cpu_count.return_value = 4

            # Mock the crack function to return a result
            mock_crack.return_value = PasswordNotFound(
                passwords_checked=100, passwords_per_second=10.0, elapsed_time=1.0
            )

            # Mock sys.argv to simulate command line args with exactly 4 cores
            test_args = ["pdf-pycrack", "test.pdf", "--cores", "4"]
            with patch.object(sys, "argv", test_args):
                main()

            # Check that no warning was printed
            mock_print_warning.assert_not_called()

            # Verify that crack_pdf_password was called with exactly 4 cores
            mock_crack.assert_called_once()
            call_args = mock_crack.call_args
            assert call_args[1]["num_processes"] == 4


class TestPasswordLengthValidation:
    """Test suite for password length validation error messages."""

    def test_main_shows_error_for_zero_min_length(self):
        """Test that main() shows formatted error for zero minimum length."""
        from pdf_pycrack.main import main

        with patch("pdf_pycrack.main.print_error") as mock_print_error:
            test_args = ["pdf-pycrack", "test.pdf", "--min_len", "0", "--max_len", "5"]
            with patch.object(sys, "argv", test_args):
                with pytest.raises(SystemExit):
                    main()

            # Check that error was printed with correct parameters
            mock_print_error.assert_called_once()
            call_args = mock_print_error.call_args
            assert call_args[1]["title"] == "Invalid Password Length Configuration"
            assert (
                "password length parameters provided are invalid"
                in call_args[1]["message"]
            )
            assert "Minimum length: 0, Maximum length: 5" in call_args[1]["details"]

    def test_main_shows_error_for_negative_length(self):
        """Test that main() shows formatted error for negative length."""
        from pdf_pycrack.main import main

        with patch("pdf_pycrack.main.print_error") as mock_print_error:
            test_args = ["pdf-pycrack", "test.pdf", "--min_len", "-1", "--max_len", "5"]
            with patch.object(sys, "argv", test_args):
                with pytest.raises(SystemExit):
                    main()

            # Check that error was printed
            mock_print_error.assert_called_once()
            call_args = mock_print_error.call_args
            assert "Minimum length: -1, Maximum length: 5" in call_args[1]["details"]

    def test_main_shows_error_when_min_greater_than_max(self):
        """Test that main() shows formatted error when min > max length."""
        from pdf_pycrack.main import main

        with patch("pdf_pycrack.main.print_error") as mock_print_error:
            test_args = ["pdf-pycrack", "test.pdf", "--min_len", "8", "--max_len", "5"]
            with patch.object(sys, "argv", test_args):
                with pytest.raises(SystemExit):
                    main()

            # Check that error was printed
            mock_print_error.assert_called_once()
            call_args = mock_print_error.call_args
            assert "Minimum length: 8, Maximum length: 5" in call_args[1]["details"]

            # Check that suggested actions are provided
            suggested_actions = call_args[1]["suggested_actions"]
            assert len(suggested_actions) == 3
            assert "positive numbers" in suggested_actions[0]
            assert (
                "minimum length is less than or equal to maximum length"
                in suggested_actions[1]
            )
            assert "Example:" in suggested_actions[2]
