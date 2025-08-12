# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [PEP 440](https://www.python.org/dev/peps/pep-0440/)
and uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0]

### Added
* Geocode-only entrypoint.

### Changed
* Update readme with docker instructions and layer info.

### Removed
* Output of area projection metadata.
* Prototype polar grid support in favor of full support via the new docker image.
* Old per-file entrypoints.

### Fixed
* Plotting issues with the cal/val submodule.

## [0.4.0]

### Changed
* CLI interface so that the RTC workflow must now be accessed via a subcommand (`mulitrtc rtc`).

### Added
* Utilities for assessing absolute/relative location error, and point target characteristics of output products.

## [0.3.3]

### Changed
* Bumped minimum Python version to >=3.10 to support modern typing

## [0.3.2]

### Added
* ICEYE support

### Changed
* Refactored library to reduce code duplication and simplify structure

## [0.3.1]

### Changed
* Loading of SICD data during beta0/sigma0 creation to a chunked strategy to reduce memory requirements

### Fixed
* Geolocation issue for prototype Umbra workflow related to switching to local UTM zone during processing

## [0.3.0]

### Changed
* Changed PFA workflow to use a sublclass of the SicdSlc class

### Added
* Cal/Val scripts for performing absolute geolocation error (ALE) assessment

### Fixed
* Property assignment issues that caused bugs in the SicdRzdSlc class

## [0.2.0]

### Added
* Support for Capella SICD SLC products

## [0.1.1]

### Added
* Conversion to sigma0 radiometry for Umbra workflow

## [0.1.0]

### Added
* Initial version

## [0.0.0]

### Added
* Marking 0th release for CI/CD
