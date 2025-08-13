# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Initial work

## [0.1.0] - 2025-08-12
- Initial release
- Core solver refactored into `AdaptiveSolvePlanner` package
- Sequential `plan` and process parallel `parallel_plan` APIs
- `PlannerConfig` using pydantic v2/pydantic-settings
- Auto-tuning heuristic for parallel runs
- Unit tests + CI + docs skeleton
