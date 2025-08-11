"""Tests for the main module."""

from unittest.mock import MagicMock, patch

from pdf_pycrack.main import main
from pdf_pycrack.models.cracking_result import (
    CrackingInterrupted,
    NotEncrypted,
    PasswordNotFound,
)


@patch("pdf_pycrack.main.setup_arg_parser")
@patch("pdf_pycrack.main.crack_pdf_password")
@patch("pdf_pycrack.main.print_start_info")
@patch("pdf_pycrack.main.print_end_info")
@patch("pdf_pycrack.main.print")
def test_main_default_charset(
    mock_print,
    mock_print_end_info,
    mock_print_start_info,
    mock_crack,
    mock_setup_arg_parser,
):
    """Test main() with default charset when none is specified."""
    # Mock arguments with no charset specified
    mock_args = MagicMock()
    mock_args.charset_custom = ""
    mock_args.charset_numbers = False
    mock_args.charset_letters = False
    mock_args.charset_special = False
    mock_args.file = "test.pdf"
    mock_args.cores = 1
    mock_args.min_len = 1
    mock_args.max_len = 4
    mock_args.batch_size = 100
    mock_args.worker_errors = False

    mock_setup_arg_parser.return_value.parse_args.return_value = mock_args

    # Mock the crack function to return a result
    mock_crack.return_value = PasswordNotFound(
        passwords_checked=100, passwords_per_second=10.0, elapsed_time=1.0
    )

    # Call main
    main()

    # Check that the default charset message was printed
    mock_print.assert_called_once_with(
        "No charset specified, defaulting to numbers (0-9)."
    )

    # Check that crack function was called with the default charset
    mock_crack.assert_called_once()
    call_kwargs = mock_crack.call_args[1]
    assert "0123456789" in call_kwargs["charset"]


@patch("pdf_pycrack.main.multiprocessing.cpu_count")
@patch("pdf_pycrack.main.setup_arg_parser")
@patch("pdf_pycrack.main.crack_pdf_password")
@patch("pdf_pycrack.main.print_start_info")
@patch("pdf_pycrack.main.print_end_info")
@patch("pdf_pycrack.main.print_warning")
def test_main_not_encrypted_result(
    mock_print_warning,
    mock_print_end_info,
    mock_print_start_info,
    mock_crack,
    mock_setup_arg_parser,
    mock_cpu_count,
):
    """Test main() when the result status is 'not_encrypted'."""
    # Mock CPU count
    mock_cpu_count.return_value = 4

    # Mock arguments
    mock_args = MagicMock()
    mock_args.charset_custom = "0123456789"
    mock_args.charset_numbers = False
    mock_args.charset_letters = False
    mock_args.charset_special = False
    mock_args.file = "test.pdf"
    mock_args.cores = 1
    mock_args.min_len = 1
    mock_args.max_len = 4
    mock_args.batch_size = 100
    mock_args.worker_errors = False

    mock_setup_arg_parser.return_value.parse_args.return_value = mock_args

    # Mock the crack function to return a NotEncrypted result
    mock_crack.return_value = NotEncrypted(elapsed_time=0.1)

    # Call main
    main()

    # Check that print_end_info was NOT called because status is 'not_encrypted'
    mock_print_end_info.assert_not_called()


@patch("pdf_pycrack.main.setup_arg_parser")
@patch("pdf_pycrack.main.crack_pdf_password")
@patch("pdf_pycrack.main.print_start_info")
@patch("pdf_pycrack.main.print_end_info")
@patch("pdf_pycrack.main.print_error")
def test_main_invalid_length_parameters(
    mock_print_error,
    mock_print_end_info,
    mock_print_start_info,
    mock_crack,
    mock_setup_arg_parser,
):
    """Test main() with invalid password length parameters."""
    # Mock arguments with invalid length parameters
    mock_args = MagicMock()
    mock_args.charset_custom = "0123456789"
    mock_args.charset_numbers = False
    mock_args.charset_letters = False
    mock_args.charset_special = False
    mock_args.file = "test.pdf"
    mock_args.cores = 1
    mock_args.min_len = 5  # min > max
    mock_args.max_len = 4
    mock_args.batch_size = 100
    mock_args.worker_errors = False

    mock_setup_arg_parser.return_value.parse_args.return_value = mock_args

    # Mock sys.exit
    with patch("sys.exit") as mock_exit:
        # Call main
        main()

        # Check that print_error was called with the expected parameters
        mock_print_error.assert_called_once()
        call_args = mock_print_error.call_args
        assert call_args[1]["title"] == "Invalid Password Length Configuration"
        assert "invalid" in call_args[1]["message"]
        assert "Minimum length: 5, Maximum length: 4" in call_args[1]["details"]

        # Check that sys.exit was called with code 1
        mock_exit.assert_called_once_with(1)


@patch("pdf_pycrack.main.setup_arg_parser")
@patch("pdf_pycrack.main.crack_pdf_password")
@patch("pdf_pycrack.main.print_start_info")
@patch("pdf_pycrack.main.print_end_info")
def test_main_keyboard_interrupt(
    mock_print_end_info, mock_print_start_info, mock_crack, mock_setup_arg_parser
):
    """Test main() when KeyboardInterrupt is raised during cracking."""
    # Mock arguments
    mock_args = MagicMock()
    mock_args.charset_custom = "0123456789"
    mock_args.charset_numbers = False
    mock_args.charset_letters = False
    mock_args.charset_special = False
    mock_args.file = "test.pdf"
    mock_args.cores = 1
    mock_args.min_len = 1
    mock_args.max_len = 4
    mock_args.batch_size = 100
    mock_args.worker_errors = False

    mock_setup_arg_parser.return_value.parse_args.return_value = mock_args

    # Mock the crack function to raise KeyboardInterrupt
    mock_crack.side_effect = KeyboardInterrupt()

    # Mock time.time for consistent elapsed time
    with patch("pdf_pycrack.main.time.time") as mock_time:
        # Set up time values for start and end
        mock_time.side_effect = [1000.0, 1001.0]  # Start time, end time

        # Call main
        main()

        # Check that print_end_info was called with CrackingInterrupted result
        mock_print_end_info.assert_called_once()
        call_args = mock_print_end_info.call_args[0]
        result = call_args[0]
        assert isinstance(result, CrackingInterrupted)
        assert result.elapsed_time == 1.0  # 1001.0 - 1000.0
