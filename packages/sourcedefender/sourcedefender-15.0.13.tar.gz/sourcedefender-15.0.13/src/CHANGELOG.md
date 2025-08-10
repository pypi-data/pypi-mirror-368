## 15.0.13
- Refactored System UUID Generation code.

## 15.0.12
- Added 'feedparser' to requirements.txt.
- Refactoring code.

## 15.0.11
- Refactored protection for overlay attacks.
- Updated documentation to include more details on our release process for CI/CD usage.

## 15.0.10
- Relaxed debugger detection in some cases.

## 15.0.9
- Added message when Debugger detected.

## 15.0.8
- Optimise Garbage Collection.

## 15.0.7
- Expanded dependencies list used by PyInstaller.
- Refactor code enabled via the '--debug' option.

## 15.0.6
- Added support for pushing to PyPi after build completes.

## 15.0.5
- Enabled (by default) the more secure method of using Python Bytecode as Payload data.
- Added opton (--no-bytecode) to disable the use of Python Bytecode as Payload data.

## 15.0.4
- Apply code formatting

## 15.0.3
- Exclude using Mac Address to identify machine inside a container.

## 15.0.2
- Force compilation of loaded code prior to execution.
- Include Mac Address when uniquly identifying a machine.

## 15.0.1
- Fixed issue where CLI command errors if no script is provided i.e python -m sourcedefender script.pye

## 15.0.0
- Dropped TgCrypto as has not been updated for 2 years (see: https://pypi.org/project/TgCrypto/#history)
- Added TgCrypto-pyrofork (see: https://pypi.org/project/TgCrypto-pyrofork/)

## 14.1.1
- Added '--debug' option to expose output from exceptions and tracebacks.
- Fixed issue where TTL wasn't converted to seconds.

## 14.1.0
- Enhanced error logging when incorrect salt/password is used.
- Added support for Python 3.13.
- Removed support for Python 3.8.

## 14.0.10
- Changed import error text when failing due to TTL expiration.

## 14.0.9
- Fix indentation bug in loader

## 14.0.8
- Adjusted retry algorithm for activations/validations.
- Refactored API client code.
- Adding NTP option to compare UTC offset to counter clock drift.

## 14.0.7
- Added feature to disbale auto_upgrades configured by the API.

## 14.0.6
- Updated PyPi documentation.

## 14.0.5
- Fixing bug in rate-limiting code.

## 14.0.4
- Added support for more granular rate-limiting of API access.

## 14.0.3
- Refactored protection for overlay attacks.

## 14.0.2
- Updated PyPi Documentation.
- Remove v8 Compatibility mode code that is no longer used.

## 14.0.1
- Added more checks for overlay attacks.
- Added SOURCEDEFENDER_APPEND_FINDER environment variable.
- Fix ttl parsing bug.

## 14.0.0
- Drop support for 32-bit Python on Windows AMD64 platforms.

## 13.0.1
- Refactored protection for overlay attacks.

## 13.0.0
- Refactored loader to improve speed.
- Removed zlib dependency.

## 12.0.5
- Fixed NoneType error in loader.

## 12.0.4
- Enhanced Garbage Collection to fix memory leak.

## 12.0.3
- Updated PyPi Docs to mirror Website.
- Updated versions listed in setup.py used by PyPi.
- Refactored code.

## 12.0.2
- Fixed bug where 'verify --target' returned wrong exit code.

## 12.0.1
- Refactored code.

## 12.0.0
- Renamed internal variables to fully block SourceRestorer on newly obfuscated code.
- Fixed a bug on activation returning an incorrect exit code on failure.

## 11.0.21
- Updated PyPi documentation.
- Impliment a fix for https://github.com/Lazza/SourceRestorer/

## 11.0.20
- Remove python-minifier support as it has stopped working.

## 11.0.19
- Updated Garbage Collection frequency.

## 11.0.18
- Updating PyPi documentation.

## 11.0.17
- Introduced minimum versions for Python dependencies we require.

## 11.0.16
- Updated missing 11.0.15 entry in the Changelog.

## 11.0.15
- Added --ttl-info option to provide message upon failed import due to TTL expiration.

## 11.0.14
- Set sys.dont_write_bytecode = True during import.

## 11.0.13
- Updated PyPi Docs.

## 11.0.12
- Moved auto-update to work every 10th day rather than on every use of the sdk tools.
- Remove Python 3.7 support as dependencies no longer install.

## 11.0.11
- Updated license validation code to fix bug with exit status.

## 11.0.10
- Moved the auto-upgrade test to be completed during a license verify and not on every run.

## 11.0.9
- Changed when the --target flag could be used.

## 11.0.8
- Added a '--target' flag to the validate option to view TTL data for encrypted files.
- Updated README documentation.

## 11.0.7
- Updated requirements.txt to remove dependencies that are not required.

## 11.0.6
- Fixed requirements.txt getting truncated.

## 11.0.5
- Added output of errors found by AST Parsing of plain-text code before encrypting.
- Removed parallel file encryption.
- Fixed bug that failed to set exit code to 1 when a file isn't encrypted.

## 11.0.4
- Dropped Linux/32bit-ARMv6 as dependency packages longer compile.

## 11.0.3
- Removed unrequired output during encryption.

## 11.0.2
- Updated PyPi README.md

## 11.0.1
- Updated supported Python versions for PyPi.

## 11.0.0
- Added in --bytecode option.
- Added support for Python 3.12.
- Removed support for Windows 32-bit Operating Systems.

## 10.0.13
- Fixed argparser bug when running as script.

## 10.0.12
- Fixed PyPi Upload issue.

## 10.0.11
- Fixed ValueError bug.

## 10.0.10
- Fixed UnboundLocalError bug.

## 10.0.9
- Enhanced licence validation code checking.

## 10.0.8
- Added support for Python 3.11.
- Added pyproject.toml

## 10.0.7
- Enabed the '--crossover' option by default prior to deprecating it.

## 10.0.6
- Updated Documentation on PyPi.
- Fixed 'validate' command so it works before activation.

## 10.0.5
- Updated PyPi Documentation in README.md.
- Fixed typo in '--help' section.

## 10.0.4
- Fixed bug where pack didn't work for trail users.
- Refactored pip installation code.

## 10.0.3
- Fixed wildcard import issue when using: 'from package import *' imports.

## 10.0.2
- Fixed crossover code detection error.

## 10.0.1
- Fixed bug in '--crossover'.

## 10.0.0
- Added '--crossover' as an option to enable cross Python version support.
- Changed auto-upgrade to keep sourcedefender in the current release branch e.g sourcedefender~=10.

## 9.4.2
- Changed defaults to '--minify' to keep Python annotations.

## 9.4.1
- Bugfixes

## 9.4.0
- Changed 'feedparser' & 'python-minifier' to get installed on-demand.
- Added '--minify' as an option rather than the default.
- Updated deployment process to include reviewing CHANGELOG.md before uploading to PyPi.
- Added 'changelog' to see changes since the last release.
- Added '--all' to the changelog option to view all changes, not just since the last release.
- Added CHANGELOG.md
