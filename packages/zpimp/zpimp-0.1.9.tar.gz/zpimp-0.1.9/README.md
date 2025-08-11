# ZPimp: Zeppelin Python Notebook Importer

A simple Python library to import and execute Python code from one Apache Zeppelin notebook into another.

## The Problem

Apache Zeppelin notebooks often require shared configurations, constants, or utility functions across multiple notes. Copy-pasting code between them leads to duplication, potential errors, and maintenance headaches. `ZPimp` addresses this by allowing you to define common Python code in a central "library" notebook and easily import and execute it in other notebooks, promoting DRY (Don't Repeat Yourself) principles within your Zeppelin environment.

## Features

* utility functions acroImport notebooks using a simple path prefix (e.g., `Utils/config`) without needing the full filename including the Zeppelin-generated ID.
*o another.

## The ProblemThe library automatically finds the correct
A simplefile in the target directory based on the provided prefix.
*library to import and exeIf multiple notebooks match the prefix, it raises ae Python libralisting the conflicting files and guiding the user to provide a more specific path (including the ID).
*om one Apache Zeppelin noteRaisesp: Zeppelin Python Noif the target directory or notebook cannot be located.
*hon library to import and exeAutomatically finds and extracts code only from paragraphs identified as Python (e.g., starting withe from one # ZPimp: Zeppelin  `%flink.pyflink`).
*hon Notebook Importer

A simple PytExecutes the imported code within theorter

A simpscope of the calling notebook's paragraph, making functions and variables immediately available.

## Installation

```bash
pip install zpimp
```

# Usage
Imagine you have a shared notebook located at /notebook/Libraries/main_config_ABC123XYZ.zpln (where /notebook is Zeppelin's base notebook directory). Inside this notebook, you have a Python paragraph (%python):

```python
# Content of a %python paragraph in Libraries/main_config_ABC123XYZ.zpln
print("Executing shared config code...")

MY_CONFIG_VALUE = "some_secret_value"
DEFAULT_TIMEOUT = 60

def common_utility_function(x):
  """A simple shared utility function."""
  return x * x

print("Shared config loaded.")
Now, in another notebook where you want to use this configuration or function:
```


```python
%python
# In your main Zeppelin notebook where you want to use the shared code

# Import the core function from the library
from zpimp import import_note

# Specify the path prefix to the notebook RELATIVE to Zeppelin's base notebook directory
# e.g., If the target is /notebook/Libraries/main_config_ABC123XYZ.zpln
# and the base dir is /notebook, the prefix is "Libraries/main_config"
notebook_prefix = "Libraries/main_config"

# Specify the absolute base directory where Zeppelin stores notebooks
# (Important: Ensure this path is correct for your setup!)
zeppelin_notebook_base_dir = "/notebook" # Or "/zeppelin/notebook", "/opt/zeppelin/notebook", etc.

print(f"Attempting to import notebook: '{notebook_prefix}'")

# Execute the import
# Pass the prefix and the base directory
import_successful = import_note(
    notebook_path_prefix=notebook_prefix,
    base_dir=zeppelin_notebook_base_dir
)

if import_successful:
    print("Import successful!")
    # Now, variables and functions from 'main_config' are available directly
    try:
        print(f"Config value: {MY_CONFIG_VALUE}")
        print(f"Default timeout: {DEFAULT_TIMEOUT}")
        result = common_utility_function(5)
        print(f"Utility function result: {result}")
    except NameError as e:
        print(f"Error accessing imported variable/function: {e}")
else:
    print("Import failed. Check logs above for details.")
```

# Function Arguments
The import_note function takes the following arguments:
 • notebook_path_prefix (str): Required. The path to the target notebook, relative to base_dir, without the _NOTEBOOKID.zpln suffix. Example: "MyFolder/SubFolder/MyNotebook".
 • base_dir (str): Required. The absolute path to the root directory where Apache Zeppelin stores its notebook folders.
Example: "/path/to/zeppelin/notebook". Ensure this path is correct for your installation!
Error Handling
 • FileNotFoundError: Raised if the base_dir or a subdirectory specified in the notebook_path_prefix does not exist, or if no .zpln file matching the prefix is found.
 • ValueError: Raised if multiple .zpln files matching the prefix are found in the target directory. The error message lists the conflicting files and advises using a more specific path including the notebook ID (which can usually be found in the notebook's URL).
 • Other standard exceptions (JSONDecodeError, OSError, Exception) might occur during file reading, JSON parsing, or execution of the imported code.

# How it Works
 1 import_note determines the target directory based on base_dir and notebook_path_prefix.
 2 It scans this directory for .zpln files where the name part before the last underscore (_) matches the final component of the notebook_path_prefix.
 3 It verifies if zero, one, or multiple matches are found.
 4 If exactly one match is found, the .zpln file (which contains JSON) is read.
 5 The JSON content is parsed to extract text from paragraphs identified as Python code (checking for known markers like %python).
 6 The extracted Python code blocks are concatenated into a single string.
 7 This combined code string is executed using exec(code, globals()), making the definitions available in the calling paragraph's global scope

 License: Apache 2.0