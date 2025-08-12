# Vibe Project Documentation

## Overview

Vibe is an AI-powered development workflow assistant that provides autonomous task execution through customizable YAML-based workflows. The project follows the "vibe coding" philosophy of autonomous AI agent operation without requiring user input beyond the initial prompt.

## Documentation Structure

### Core Philosophy
- **[Vibe Philosophy](vibe-philosophy.md)**: Core principles of autonomous AI agent operation
- **[Development Guidelines](development-guidelines.md)**: Project standards and best practices

### Architecture
- **[Workflow Architecture](workflow-architecture.md)**: YAML-based workflow system design
- **[ADR-001: YAML Workflow System](adr/adr-001-yaml-workflow-system.md)**: Key architectural decision

### Workflow Documentation
Individual workflows are documented within their YAML files:
- `vibe/workflows/data/analysis.yaml`: Project structure analysis
- `vibe/workflows/data/branch_strategy.yaml`: Branch selection and merge timing
- `vibe/workflows/data/dependency_update.yaml`: Dependency and tooling updates
- `vibe/workflows/data/git_management.yaml`: Git repository management

## Key Concepts

### Vibe Coding Philosophy
Autonomous interaction between AI agent and tools/project, requiring no additional user input beyond the initial prompt. All workflows must be self-contained and executable without user interaction.

### YAML Workflow System
External workflow definitions separated from Python code, enabling independent updates and better maintainability. Includes graceful fallback to Python workflows for reliability.

### Architecture Decision Records (ADRs)
Significant architectural decisions are documented in the `adr/` directory using a standard template to capture context, rationale, and consequences.

## Quick Reference

### Adding New Workflows
1. Create YAML file in `vibe/workflows/data/`
2. Follow the standard YAML workflow format
3. Ensure autonomous operation (no user input required)
4. Test workflow loading and execution
5. Document any architectural decisions in ADRs

### Updating Existing Workflows
1. Edit YAML files directly (no code changes needed)
2. Validate autonomous operation principles
3. Test changes before committing
4. Update documentation if workflow behavior changes significantly

### Contributing Guidelines
1. Follow vibe coding philosophy (autonomous operation)
2. Document significant decisions in ADRs
3. Update relevant documentation with changes
4. Ensure comprehensive error handling
5. Test both success and failure scenarios

## Project Evolution

The vibe project has evolved from hardcoded Python workflows to a flexible YAML-based system that supports:
- Independent workflow updates without code changes
- Better separation of concerns between data and logic
- Enhanced maintainability and accessibility
- Robust error handling with graceful fallback
- Full compliance with vibe coding philosophy

This documentation serves as a knowledge base to maintain consistency and accumulate wisdom across development sessions.
