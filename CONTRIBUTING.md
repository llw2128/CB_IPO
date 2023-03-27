## Prequisites

Python must be version 3.7 or higher
Chrome must be Version 111.0.5563.64 or higher
This project also requires the installation of selenium, pandas, Chromedriver, and bs4

Prerequisites can be installed by running `make develop` in root directory

## Contributing

If you are interested in contirbuting it is reccomended to take the following steps:

- Fork the repository on Github
- Clone your fork to your computer by running `git clone`
- To install dependencies and build library run `make develop` inside the folder

## Pull Requests

Prior to opening a pull request be sure to do the following:

- Run `make tests` or `make coverage` to ensure changes pass tests and that code coverage is adequate
- Run `make lint` and `make format` in the folder for formatting using black and flake8

If code is sufficently covered and formated then open a pull request.

## Additional Notes

Please add tests for any new features