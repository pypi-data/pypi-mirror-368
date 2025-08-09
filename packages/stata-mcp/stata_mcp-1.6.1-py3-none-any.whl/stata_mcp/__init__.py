import argparse
import os
import platform
import sys
from datetime import datetime
from importlib.metadata import version
from typing import Dict, List, Optional, Union

import dotenv
import pandas as pd
from mcp.server.fastmcp import FastMCP

from .config import Config
from .core.stata import StataController, StataDo, StataFinder
from .utils.Installer import Installer
from .utils.Prompt import pmp
from .utils.usable import usable

__version__ = version("stata-mcp")

dotenv.load_dotenv()
mcp = FastMCP(name="stata-mcp")
config_mgr = Config()

# Initialize optional parameters
sys_os = platform.system()

# Determine documents path
if sys_os in ["Darwin", "Linux"]:
    documents_path = os.getenv(
        "documents_path",
        os.path.expanduser("~/Documents")
    )
elif sys_os == "Windows":
    documents_path = os.getenv(
        "documents_path",
        os.path.join(os.environ.get("USERPROFILE", "~"), "Documents"),
    )
else:
    sys.exit("Unknown System")

# Use configured output path if available
output_base_path = config_mgr.get("stata-mcp.output_base_path") or os.path.join(
    documents_path, "stata-mcp-folder"
)
os.makedirs(output_base_path, exist_ok=True)

try:
    # stata_cli
    finder = StataFinder()
    default_cli = finder.find_stata()
    stata_cli = config_mgr.get("stata.stata_cli") or os.getenv(
        "stata_cli", default_cli
    )
    if stata_cli is None:
        exit_msg = (
            "Missing Stata.exe, "
            "you could config your Stata.exe abspath in your env\ne.g\n"
            r'stata_cli="C:\\Program Files\\Stata19\StataMP.exe"'
            r"/usr/local/bin/stata-mp")
        sys.exit(exit_msg)
except Exception:
    stata_cli = None

# Create a series of folder
log_base_path = os.path.join(output_base_path, "stata-mcp-log")
os.makedirs(log_base_path, exist_ok=True)
dofile_base_path = os.path.join(output_base_path, "stata-mcp-dofile")
os.makedirs(dofile_base_path, exist_ok=True)
result_doc_path = os.path.join(output_base_path, "stata-mcp-result")
os.makedirs(result_doc_path, exist_ok=True)

lang = os.getenv("lang", "en")
if lang not in ["en", "cn"]:
    lang = "en"  # Default to English if not set or invalid
pmp.set_lang(lang)


@mcp.prompt()
def stata_assistant_role(lang: str = None) -> str:
    """
    Return the Stata assistant role prompt content.

    This function retrieves a predefined prompt that defines the role and capabilities
    of a Stata analysis assistant. The prompt helps set expectations and context for
    the assistant's behavior when handling Stata-related tasks.

    Args:
        lang (str, optional): Language code for localization of the prompt content.
            If None, returns the default language version. Defaults to None.
            Examples: "en" for English, "cn" for Chinese.

    Returns:
        str: The Stata assistant role prompt text in the requested language.

    Examples:
        >>> stata_assistant_role()  # Returns default language version
        "I am a Stata analysis assistant..."

        >>> stata_assistant_role(lang="en")  # Returns English version
        "I am a Stata analysis assistant..."

        >>> stata_assistant_role(lang="cn")  # Returns Chinese version
        "我是一个Stata分析助手..."
    """
    return pmp.get_prompt(prompt_id="stata_assistant_role", lang=lang)


@mcp.prompt()
def stata_analysis_strategy(lang: str = None) -> str:
    """
    Return the Stata analysis strategy prompt content.

    This function retrieves a predefined prompt that outlines the recommended
    strategy for conducting data analysis using Stata. The prompt includes
    guidelines for data preparation, code generation, results management,
    reporting, and troubleshooting.

    Args:
        lang (str, optional): Language code for localization of the prompt content.
            If None, returns the default language version. Defaults to None.
            Examples: "en" for English, "cn" for Chinese.

    Returns:
        str: The Stata analysis strategy prompt text in the requested language.

    Examples:
        >>> stata_analysis_strategy()  # Returns default language version
        "When conducting data analysis using Stata..."

        >>> stata_analysis_strategy(lang="en")  # Returns English version
        "When conducting data analysis using Stata..."

        >>> stata_analysis_strategy(lang="cn")  # Returns Chinese version
        "使用Stata进行数据分析时，请遵循以下策略..."
    """
    return pmp.get_prompt(prompt_id="stata_analysis_strategy", lang=lang)


@mcp.prompt(name="help", description="Get help for a Stata command")
def help(cmd: str) -> str:
    """
    Execute the Stata 'help' command and return its output.

    Args:
        cmd (str): The name of the Stata command to query, e.g., "regress" or "describe".

    Returns:
        str: The help text returned by Stata for the specified command,
             or a message indicating that no help was found.
    """
    controller = StataController(stata_cli)
    std_error_msg = (
        f"help {cmd}\r\n"
        f"help for {cmd} not found\r\n"
        f"try help contents or search {cmd}"
    )
    help_result = controller.run(f"help {cmd}")

    if help_result != std_error_msg:
        return help_result
    else:
        return "No help found for the command: " + cmd


@mcp.tool()
def read_log(log_path: str) -> str:
    """
    Read the log file and return its content.

    Args:
        log_path (str): The path to the log file.

    Returns:
        str: The content of the log file.
    """
    with open(log_path, "r") as file:
        log = file.read()
    return log


@mcp.tool(name="get_data_info",
          description="Get descriptive statistics for the data file")
def get_data_info(data_path: str,
                  vars_list: Optional[List[str]] = None,
                  encoding: str = "utf-8") -> str:
    """
    Analyze the data file and return descriptive statistics. Supports various file formats,
    including Stata data files (.dta), CSV files (.csv), and Excel files (.xlsx, .xls).
    If the AI wants to examine the data situation, it should not use `use`, but should use
    `get_data_info` instead.

    Args:
        data_path: Path to the data file, supporting .dta, .csv, .xlsx, and .xls formats.
        vars_list: Optional list of variables. If provided, returns statistics only for these variables.
                  If None, returns statistics for all variables.
        encoding: The data file encoding method, supporting "utf-8", "gbk" and so on. (Only works when the data is csv)

    Returns:
        str: A string containing descriptive statistics of the data, including:
             - Basic file information (format, size, number of variables, number of observations, etc.)
             - Variable type statistics
             - Statistical summary of numerical variables (mean, standard deviation, min, max, etc.)
             - Frequency distribution of categorical variables
             - Missing value analysis
             - Panel structure information, if it is panel data

    Raises:
        ValueError: If the file format is not supported or the file does not exist
        ImportError: If packages required for processing specific file formats are missing

    Examples:
        >>> get_data_info("example.dta")
        'File Information:
         Format: Stata data file (.dta)
         File size: 1.2 MB
         Observations: 1000
         Variables: 15
         ...'

        >>> get_data_info("sales.csv", vars_list=["price", "quantity", "date"])
        'File Information:
         Format: CSV file (.csv)
         File size: 0.5 MB
         Observations: 500
         Variables: 3 (selected from original variables)
         ...'
    """
    # Check if the file exists
    if not os.path.exists(data_path):
        raise ValueError(f"File does not exist: {data_path}")

    # Get file information
    file_size = os.path.getsize(data_path) / (1024 * 1024)  # Convert to MB
    file_extension = os.path.splitext(data_path)[1].lower()

    # Read data according to file extension
    if file_extension == ".dta":
        try:
            # Try to read Stata file
            df = pd.read_stata(data_path)
            file_type = "Stata data file (.dta)"
        except ImportError:
            raise ImportError(
                "Missing package required to read Stata files. Please install pandas: pip install pandas"
            )
    elif file_extension == ".csv":
        try:
            # Try to read CSV file, handle potential encoding issues
            try:
                df = pd.read_csv(data_path, encoding=encoding)
            except UnicodeDecodeError:
                # Try different encoding
                df = pd.read_csv(data_path, encoding="latin1")
            file_type = "CSV file (.csv)"
        except ImportError:
            raise ImportError(
                "Missing package required to read CSV files. Please install pandas: pip install pandas"
            )
    elif file_extension in [".xlsx", ".xls"]:
        try:
            # Try to read Excel file
            df = pd.read_excel(data_path)
            file_type = f"Excel file ({file_extension})"
        except ImportError:
            raise ImportError(
                "Missing package required to read Excel files. Please install openpyxl: pip install openpyxl"
            )
    else:
        raise ValueError(
            f"Unsupported file format: {file_extension}. Supported formats include .dta, .csv, .xlsx, and .xls"
        )

    # If variable list is provided, only keep these variables
    if vars_list is not None:
        # Check if all requested variables exist
        missing_vars = [var for var in vars_list if var not in df.columns]
        if missing_vars:
            raise ValueError(
                f"The following variables do not exist in the dataset: {', '.join(missing_vars)}"
            )

        # Select specified variables
        df = df[vars_list]

    # Create output string
    output: list = []

    # 1. Basic file information
    output.append("File Information:")
    output.append(f"Format: {file_type}")
    output.append(f"File size: {file_size:.2f} MB")
    output.append(f"Observations: {df.shape[0]}")

    if vars_list is not None:
        output.append(
            f"Variables: {len(vars_list)} (selected from original variables)")
    else:
        output.append(f"Variables: {df.shape[1]}")

    # 2. Variable type statistics
    num_numeric = sum(
        pd.api.types.is_numeric_dtype(
            df[col]) for col in df.columns)
    num_categorical = sum(
        pd.api.types.is_categorical_dtype(df[col]) or df[col].dtype == "object"
        for col in df.columns
    )
    num_datetime = sum(
        pd.api.types.is_datetime64_dtype(
            df[col]) for col in df.columns)
    num_boolean = sum(
        pd.api.types.is_bool_dtype(
            df[col]) for col in df.columns)

    output.append("\nVariable Type Statistics:")
    output.append(f"Numeric variables: {num_numeric}")
    output.append(f"Categorical variables: {num_categorical}")
    output.append(f"Datetime variables: {num_datetime}")
    output.append(f"Boolean variables: {num_boolean}")

    # 3. Missing value analysis
    total_missing = df.isna().sum().sum()
    missing_percent = (total_missing / (df.shape[0] * df.shape[1])) * 100

    output.append("\nMissing Value Analysis:")
    output.append(f"Total missing values: {total_missing}")
    output.append(f"Missing value percentage: {missing_percent:.2f}%")

    # Get missing value count and percentage for each variable
    if (
        df.shape[1] <= 30
    ):  # If there aren't many variables, show missing values for each
        output.append("\nMissing values by variable:")
        for col in df.columns:
            missing_count = df[col].isna().sum()
            missing_percent = (missing_count / df.shape[0]) * 100
            if missing_count > 0:
                output.append(
                    f"  {col}: {missing_count} ({missing_percent:.2f}%)")
    else:
        # If there are too many variables, only show the top 10 with missing
        # values
        missing_cols = df.isna().sum().sort_values(ascending=False)
        missing_cols = missing_cols[missing_cols > 0]
        if len(missing_cols) > 0:
            output.append("\nTop 10 variables with most missing values:")
            for col, count in missing_cols.head(10).items():
                missing_percent = (count / df.shape[0]) * 100
                output.append(f"  {col}: {count} ({missing_percent:.2f}%)")

    # 4. Statistical summary of numerical variables
    numeric_cols = df.select_dtypes(include=["number"]).columns

    if len(numeric_cols) > 0:
        output.append("\nNumerical Variable Statistics:")

        # Calculate statistics
        desc_stats = df[numeric_cols].describe().T

        # Add additional statistics
        if df.shape[0] > 0:  # Ensure there is data
            desc_stats["Missing"] = df[numeric_cols].isna().sum()
            desc_stats["Missing Ratio"] = df[numeric_cols].isna().sum() / \
                df.shape[0]

            # Optional: Add more statistics
            desc_stats["Skewness"] = df[numeric_cols].skew()
            desc_stats["Kurtosis"] = df[numeric_cols].kurtosis()

        # Format and add to output
        for col in desc_stats.index:
            output.append(f"\n  {col}:")
            output.append(f"    Count: {desc_stats.loc[col, 'count']:.0f}")
            output.append(f"    Mean: {desc_stats.loc[col, 'mean']:.4f}")
            output.append(f"    Std Dev: {desc_stats.loc[col, 'std']:.4f}")
            output.append(f"    Min: {desc_stats.loc[col, 'min']:.4f}")
            output.append(
                f"    25th Percentile: {desc_stats.loc[col, '25%']:.4f}")
            output.append(f"    Median: {desc_stats.loc[col, '50%']:.4f}")
            output.append(
                f"    75th Percentile: {desc_stats.loc[col, '75%']:.4f}")
            output.append(f"    Max: {desc_stats.loc[col, 'max']:.4f}")
            output.append(
                f"    Missing Values: {desc_stats.loc[col, 'Missing']:.0f} ({desc_stats.loc[col, 'Missing Ratio']:.2%})"
            )
            output.append(
                f"    Skewness: {desc_stats.loc[col, 'Skewness']:.4f}")
            output.append(
                f"    Kurtosis: {desc_stats.loc[col, 'Kurtosis']:.4f}")

    # 5. Frequency distribution of categorical variables
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns

    if len(categorical_cols) > 0:
        output.append("\nCategorical Variable Frequency Distribution:")

        for col in categorical_cols:
            # Get number of unique values
            unique_count = df[col].nunique()

            output.append(f"\n  {col}:")
            output.append(f"    Unique values: {unique_count}")

            # If number of unique values is reasonable (not more than 10), show
            # frequency distribution
            if unique_count <= 10 and unique_count > 0:
                value_counts = df[col].value_counts().head(10)
                value_percent = df[col].value_counts(
                    normalize=True).head(10) * 100

                for i, (value, count) in enumerate(value_counts.items()):
                    percent = value_percent[i]
                    output.append(f"    {value}: {count} ({percent:.2f}%)")
            elif unique_count > 10:
                # If too many unique values, only show top 5
                output.append("    Top 5 most common values:")
                value_counts = df[col].value_counts().head(5)
                value_percent = df[col].value_counts(
                    normalize=True).head(5) * 100

                for i, (value, count) in enumerate(value_counts.items()):
                    percent = value_percent[i]
                    output.append(f"    {value}: {count} ({percent:.2f}%)")

    # 6. Detect if it's panel data and analyze panel structure
    # Typically panel data has ID and time dimensions
    potential_id_cols = [
        col
        for col in df.columns
        if "id" in str(col).lower()
        or "code" in str(col).lower()
        or "key" in str(col).lower()
    ]
    potential_time_cols = [
        col
        for col in df.columns
        if "time" in str(col).lower()
        or "date" in str(col).lower()
        or "year" in str(col).lower()
        or "month" in str(col).lower()
        or "day" in str(col).lower()
    ]

    # If there are potential ID columns and time columns, try to analyze panel
    # structure
    if potential_id_cols and potential_time_cols:
        for id_col in potential_id_cols[:1]:  # Only try the first ID column
            # Only try the first time column
            for time_col in potential_time_cols[:1]:
                # Calculate panel structure
                try:
                    n_ids = df[id_col].nunique()
                    n_times = df[time_col].nunique()
                    n_obs = df.shape[0]

                    output.append(
                        "\nPotential Panel Data Structure Detection:")
                    output.append(
                        f"  ID variable: {id_col} (unique values: {n_ids})")
                    output.append(
                        f"  Time variable: {time_col} (unique values: {n_times})"
                    )
                    output.append(f"  Total observations: {n_obs}")

                    # Check if panel is balanced
                    cross_table = pd.crosstab(df[id_col], df[time_col])
                    is_balanced = (cross_table == 1).all().all()

                    if is_balanced and n_ids * n_times == n_obs:
                        output.append(
                            "  Panel status: Strongly balanced panel (each ID has one observation at each time point)"
                        )
                    elif df.groupby(id_col)[time_col].count().var() == 0:
                        output.append(
                            "  Panel status: Weakly balanced panel (each ID has the same number of observations, but possibly not at the same time points)"
                        )
                    else:
                        output.append(
                            "  Panel status: Unbalanced panel (different IDs have different numbers of observations)"
                        )

                    # Calculate average observations per ID
                    avg_obs_per_id = df.groupby(id_col).size().mean()
                    output.append(
                        f"  Average observations per ID: {avg_obs_per_id:.2f}"
                    )

                    # Calculate time span
                    if pd.api.types.is_datetime64_dtype(df[time_col]):
                        min_time = df[time_col].min()
                        max_time = df[time_col].max()
                        output.append(f"  Time span: {min_time} to {max_time}")
                except Exception:
                    # If calculation fails, skip panel analysis
                    pass

    # Return formatted output
    return "\n".join(output)


@mcp.prompt()
def results_doc_path() -> str:
    """
    Generate and return a result document storage path based on the current timestamp.

    This function performs the following operations:
    1. Gets the current system time and formats it as a '%Y%m%d%H%M%S' timestamp string
    2. Concatenates this timestamp string with the preset result_doc_path base path to form a complete path
    3. Creates the directory corresponding to that path (no error if directory already exists)
    4. Returns the complete path string of the newly created directory

    Returns:
        str: The complete path of the newly created result document directory, formatted as:
            `<result_doc_path>/<YYYYMMDDHHMMSS>`, where the timestamp portion is generated from the system time when the function is executed

    Notes:
        (The following content is not needed for LLM to understand)
        - Using the `exist_ok=True` parameter, no exception will be raised when the target directory already exists
        - The function uses the walrus operator (:=) in Python 3.8+ to assign a variable within an expression
        - The returned path is suitable for use as the output directory for Stata commands such as `outreg2`
        - In specific Stata code, you can set the file output path at the beginning.
    """
    os.makedirs(
        (path := os.path.join(
            result_doc_path,
            datetime.strftime(
                datetime.now(),
                "%Y%m%d%H%M%S"))),
        exist_ok=True,
    )
    return path


@mcp.tool(name="write_dofile", description="write the stata-code to dofile")
def write_dofile(content: str) -> str:
    """
    Write stata code to a dofile.

    Args:
        content: The stata code content which will be writen to the designated do-file.

    Returns:
        the do-file path

    Notes:
        Please be careful about the first command in dofile should be use data.
        For avoiding make mistake, you can generate stata-code with the function from `StataCommandGenerator` class.
        Please avoid writing any code that draws graphics or requires human intervention for uncertainty bug.
        If you find something went wrong about the code, you can use the function from `StataCommandGenerator` class.

    Enhancement:
        If you have `outreg2`, `esttab` command for output the result,
        you should use the follow command to get the output path.
        `results_doc_path`, and use `local output_path path` the path is the return of the function `results_doc_path`.
        If you want to use the function `write_dofile`, please use `results_doc_path` before which is necessary.

    """
    file_path = os.path.join(
        dofile_base_path,
        datetime.strftime(
            datetime.now(),
            "%Y%m%d%H%M%S") +
        ".do")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return file_path


@mcp.tool(
    name="append_dofile",
    description="append stata-code to an existing dofile or create a new one",
)
def append_dofile(original_dofile_path: str, content: str) -> str:
    """
    Append stata code to an existing dofile or create a new one if the original doesn't exist.

    Args:
        original_dofile_path: Path to the original dofile to append to. If empty or invalid, a new file will be created.
        content: The stata code content which will be appended to the designated do-file.

    Returns:
        The new do-file path (either the modified original or a newly created file)

    Notes:
        When appending to an existing file, the content will be added at the end of the file.
        If the original file doesn't exist or path is empty, a new file will be created with the content.
        Please be careful about the syntax coherence when appending code to an existing file.
        For avoiding mistakes, you can generate stata-code with the function from `StataCommandGenerator` class.
        Please avoid writing any code that draws graphics or requires human intervention for uncertainty bug.
        If you find something went wrong about the code, you can use the function from `StataCommandGenerator` class.

    Enhancement:
        If you have `outreg2`, `esttab` command for output the result,
        you should use the follow command to get the output path.
        `results_doc_path`, and use `local output_path path` the path is the return of the function `results_doc_path`.
        If you want to use the function `append_dofile`, please use `results_doc_path` before which is necessary.
    """
    # Create a new file path for the output
    new_file_path = os.path.join(
        dofile_base_path, datetime.strftime(
            datetime.now(), "%Y%m%d%H%M%S") + ".do")

    # Check if original file exists and is valid
    original_exists = False
    original_content = ""
    if original_dofile_path and os.path.exists(original_dofile_path):
        try:
            with open(original_dofile_path, "r", encoding="utf-8") as f:
                original_content = f.read()
            original_exists = True
        except Exception:
            # If there's any error reading the file, we'll create a new one
            original_exists = False

    # Write to the new file (either copying original content + new content, or
    # just new content)
    with open(new_file_path, "w", encoding="utf-8") as f:
        if original_exists:
            f.write(original_content)
            # Add a newline if the original file doesn't end with one
            if original_content and not original_content.endswith("\n"):
                f.write("\n")
        f.write(content)

    return new_file_path


@mcp.tool(name="stata_do", description="Run a stata-code via Stata")
def stata_do(dofile_path: str,
             is_read_log: bool = True) -> Dict[str, Union[str, None]]:
    """
    Execute a Stata do-file and return the log file path with optional log content.

    This function runs a Stata do-file using the configured Stata executable and
    generates a log file. It supports cross-platform execution (macOS, Windows, Linux).

    Args:
        dofile_path (str): Absolute or relative path to the Stata do-file (.do) to execute.
        is_read_log (bool, optional): Whether to read and return the log file content.
                                    Defaults to True.

    Returns:
        Dict[str, Union[str, None]]: A dictionary containing:
            - "log_file_path" (str): Path to the generated Stata log file
            - "log_content" (str, optional): Content of the log file if is_read_log is True

    Raises:
        FileNotFoundError: If the specified do-file does not exist
        RuntimeError: If Stata execution fails or log file cannot be generated
        PermissionError: If there are insufficient permissions to execute Stata or write log files

    Example:
        >>> result = stata_do(do_file_path, is_read_log=True)
        >>> print(result[log_file_path])
        /path/to/logs/analysis.log
        >>> print(result[log_content])
        Stata log content...

    Note:
        - The log file is automatically created in the configured log_file_path directory
        - Supports multiple operating systems through the StataDo executor
        - Log file naming follows Stata conventions with .log extension
    """
    # Initialize Stata executor with system configuration
    stata_executor = StataDo(
        stata_cli=stata_cli,  # Path to Stata executable
        log_file_path=log_base_path,  # Directory for log files
        dofile_base_path=dofile_base_path,  # Base directory for do-files
        sys_os=sys_os  # Operating system identifier
    )

    # Execute the do-file and get log file path
    log_file_path = stata_executor.execute_dofile(dofile_path)

    # Return log content based on user preference
    if is_read_log:
        # Read and include log file content in response
        log_content = stata_executor.read_log(log_file_path)
        return {
            "log_file_path": log_file_path,
            "log_content": log_content
        }
    else:
        # Return only the log file path
        return {
            "log_file_path": log_file_path,
            "log_content": None
        }


def main() -> None:
    """Entry point for the command line interface."""
    parser = argparse.ArgumentParser(
        prog="stata-mcp",
        description="Stata-MCP command line interface",
        add_help=True)
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"Stata-MCP version is {__version__}",
        help="show version information",
    )
    parser.add_argument(
        "--usable",
        action="store_true",
        help="check whether Stata-MCP could be used on this computer",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="install Stata-MCP to Claude Desktop")
    parser.add_argument(
        "--webui",
        action="store_true",
        help="launch the configuration web UI",
    )

    # mcp.run
    parser.add_argument(
        "-t",
        "--transport",
        choices=["stdio", "sse", "http", "streamable-http"],
        default=None,
        help="mcp server transport method (default: stdio)",
    )
    args = parser.parse_args()

    if args.usable:
        sys.exit(usable())
    elif args.install:
        Installer(sys_os=sys.platform).install()
    elif args.webui:
        from .webui import main as webui_main
        webui_main()
    else:
        print("Starting Stata-MCP...")

        # Use stdio if there is no transport argument
        transport = args.transport or "stdio"
        if transport == "http":
            transport = (
                "streamable-http"  # Default to streamable-http for HTTP transport
            )
        mcp.run(transport=transport)


if __name__ == "__main__":
    print(f"Hello Stata-MCP@version{__version__}")
    main()
