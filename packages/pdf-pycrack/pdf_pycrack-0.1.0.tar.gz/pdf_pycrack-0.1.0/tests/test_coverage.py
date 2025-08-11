"""Additional tests to improve coverage to 100%."""

from unittest.mock import MagicMock, patch

from pdf_pycrack.main import main


@patch("pdf_pycrack.main.setup_arg_parser")
@patch("pdf_pycrack.main.crack_pdf_password")
@patch("pdf_pycrack.main.print_start_info")
@patch("pdf_pycrack.main.print_end_info")
def test_main_all_charset_options(
    mock_print_end_info, mock_print_start_info, mock_crack, mock_setup_arg_parser
):
    """Test main() with all charset options enabled."""
    # Mock arguments with all charset options enabled
    mock_args = MagicMock()
    mock_args.charset_custom = "xyz"  # Using distinct characters
    mock_args.charset_numbers = True
    mock_args.charset_letters = True
    mock_args.charset_special = True
    mock_args.file = "test.pdf"
    mock_args.cores = 1
    mock_args.min_len = 1
    mock_args.max_len = 4
    mock_args.batch_size = 100
    mock_args.worker_errors = False

    mock_setup_arg_parser.return_value.parse_args.return_value = mock_args

    # Mock the crack function to return a result
    mock_crack.return_value = MagicMock()

    # Call main
    main()

    # Check that crack function was called
    mock_crack.assert_called_once()
    call_kwargs = mock_crack.call_args[1]
    # Check that all charset options are included in the final charset
    charset = call_kwargs["charset"]
    # Check for individual characters since the charset is sorted
    assert "x" in charset
    assert "y" in charset
    assert "z" in charset
    assert "0" in charset  # numbers
    assert "a" in charset  # lowercase letters
    assert "A" in charset  # uppercase letters
    assert "!" in charset  # special characters


@patch("pdf_pycrack.main.setup_arg_parser")
@patch("pdf_pycrack.main.crack_pdf_password")
@patch("pdf_pycrack.main.print_start_info")
@patch("pdf_pycrack.main.print_end_info")
def test_main_none_result(
    mock_print_end_info, mock_print_start_info, mock_crack, mock_setup_arg_parser
):
    """Test main() when crack_pdf_password returns None."""
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

    # Mock the crack function to return None
    mock_crack.return_value = None

    # Mock time.time for consistent elapsed time
    with patch("pdf_pycrack.main.time.time") as mock_time:
        # Set up time values for start and end
        mock_time.side_effect = [1000.0, 1001.0]  # Start time, end time

        # Call main
        main()

        # Check that print_end_info was called with PasswordNotFound
        mock_print_end_info.assert_called_once()
        call_args = mock_print_end_info.call_args[0]
        result = call_args[0]
        from pdf_pycrack.models.cracking_result import PasswordNotFound

        assert isinstance(result, PasswordNotFound)
        assert result.elapsed_time == 1.0
        assert result.passwords_checked == 0
        assert result.passwords_per_second == 0
