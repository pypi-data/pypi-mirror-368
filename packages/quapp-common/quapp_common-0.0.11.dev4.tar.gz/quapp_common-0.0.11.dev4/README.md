# quapp-common

Quapp common library supporting Quapp Platform for Quantum Computing.

## Overview

`quapp-common` is a Python library designed to support the Quapp Platform for
Quantum Computing by providing common utilities, configurations, and
abstractions for working with
quantum providers and devices.

Recent improvements focus on cleaner and more consistent logging, enhanced error
handling, and
standardizing header management by adding workspace-specific headers instead of
tenant-specific ones,
improving maintainability and clarity.

## Features

- Provider and device factory for quantum computing platforms.
- Logging and configuration utilities with improved and detailed log messages.
- Support for AWS Braket, OQC Cloud, Qiskit, PennyLane, DWave Ocean, and Quapp
  quantum simulators.
- Refactored classes and utilities to remove tenant-specific request, response,
  and promise classes.
- Standardized naming by renaming `ProjectHeader` to `CustomHeader`.
- Enhanced error handling and job metadata update mechanisms.
- Simplified and cleaner HTTP request/response logging and URL parsing
  utilities.

## Installation

Install via pip:

```bash
pip install quapp-common
```

## Recently Changes Highlights

- Added workspace-specific classes for request, response, and promise,
  consolidating code to unify context handling.
- Refactored logging throughout the codebase, removing redundant debug logs and
  adding context-rich log messages.
- Improved URL parsing and job ID extraction, especially in HTTP utilities, to
  better track jobs.
- Cleaned up logging configuration files to standardize log formats and levels.
- Added robust error handling in job execution and analysis pipelines, ensuring
  detailed failure reporting.
- Simplified header and request body logging, improving performance and
  readability.

---

For detailed usage and API references, please refer to the in-code documentation
or contact the maintainers.
 
