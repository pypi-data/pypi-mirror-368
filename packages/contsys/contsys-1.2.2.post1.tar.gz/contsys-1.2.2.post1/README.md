# contsys

Python library simplifying system script management with handy functions like clearing the console, setting the window title, and detecting the operating system (Windows, Linux, macOS).

By **G-Azon** 🇫🇷

## Features

- CMD:
   - `CMD.clear` clears the console screen.
   - `CMD.title([TITLE])` changes the title of the console screen to the specified title.

- system:  
   - `system.iswin32()` returns **True** if the current OS is *Windows*, and return **False** if the current OS is not *Windows*.
   - `system.linux()` returns **True** if the current OS is *Linux Based*, and return **False** if the current OS is not *Linux Based*.
   - `system.isdarwin()` returns **True** if the current OS is *MacOS*, and return **False** if the current OS is not *MacOS*.
   - `system.isadmin()` returns **True** if the script is executed as root, and returns **False** if the script is not executed as root.
   - `system.runasadmin([TARGET], [ARGS])` run the specified python script as root.

- monitor:
   - `monitor.cpu_usage()` returns the current cpu usage in percent.
   - `monitor.ram_usage()` returns the current virtual memory usage in percent.

## Installation

You can install contsys using pip:

```bash
pip install contsys
```

## License

This project is under the MIT License.

## Contact

If you have any trouble or you want to suggest an improvement you can contact me at [G-Azon782345@protonmail.com](mailto:G-Azon782345@protonmail.com)

## Changelog

- ### 1.2.2
   - **Added** version the 1.2.1 in the changelog. (i forgotten it)
   - **Improved** the changelog by bolding change types.
   - **Fixed** an issue where the SSH indicator was still **displayed** even when `ssh_indicator` was not specified and the program was not running over an SSH connection.

- ### 1.2.1
   - **Added** an option to `CMD.title()`: it now displays an indicator if the program is running over an SSH connection. This can be disabled by setting `ssh_indicator = False`.

- ### 1.2.0
   - **Added** `system.isadmin()` `system.runasadmin()`

- ### 1.1.3
   - **Added** the MIT license in *LICENSE*

- ### 1.1.2
   - Small improvements in the description in the *Changelog* section

- ### 1.1.1
   - **Added** `monitor.cpu_usage()` `monitor.ram_usage()`.
   - **Added** the changelog section.
   - **Added** a new required dependency: *psutil*

- ### 1.0.2
   - **Added** a better description.

- ### 1.0.1
   - **Added** `system.iswin32()` `system.islinux()` `system.isdarwin()`.

- ### 1.0.0
   - The first version of **contsys**.
   - **Added** `CMD.clear()` `CMD.title()`.