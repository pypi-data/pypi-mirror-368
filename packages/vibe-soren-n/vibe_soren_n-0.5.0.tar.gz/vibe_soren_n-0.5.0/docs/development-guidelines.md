# Development Guidelines

## Project Standards

### Code Organization
- **Separation of Concerns**: Keep data, logic, and configuration separate
- **Modular Design**: Small, focused modules with clear responsibilities
- **Clear Dependencies**: Explicit imports and minimal circular dependencies
- **Error Handling**: Comprehensive error handling with graceful degradation

### Python Code Standards
- **Type Hints**: Use type hints for all function parameters and return values
- **Docstrings**: Clear docstrings for all public functions and classes
- **Error Handling**: Use try-catch blocks with specific exception types
- **Logging**: Use structured logging instead of print statements
- **Testing**: Write tests for all public interfaces and critical logic

### YAML Workflow Standards
- **Autonomous Operation**: All workflows must execute without user input
- **Informational Echo**: Use echo statements for information, not interaction
- **Clear Structure**: Consistent YAML structure with required fields
- **Command Lists**: All commands must be executable shell commands
- **Documentation**: Include description and trigger patterns

### File Naming Conventions
- **Python Files**: `snake_case.py` (e.g., `workflow_loader.py`)
- **YAML Files**: `kebab-case.yaml` (e.g., `branch-strategy.yaml`)
- **Documentation**: `kebab-case.md` (e.g., `development-guidelines.md`)
- **Directories**: `snake_case` for Python, `kebab-case` for docs

### Git Workflow
- **Commit Messages**: Use conventional commit format (`type(scope): description`)
- **Branch Names**: Use descriptive names (`feature/yaml-workflows`, `fix/loader-error`)
- **Small Commits**: Keep commits focused on single changes
- **Documentation**: Update docs with code changes in same commit

## AI Agent Collaboration

### Session Documentation
- **Document Decisions**: Record architectural decisions in ADRs
- **Capture Context**: Maintain conversation summaries for complex sessions
- **Update Guidelines**: Evolve guidelines based on lessons learned
- **Knowledge Accumulation**: Build on previous session insights

### Code Review Patterns
- **Philosophy Compliance**: Ensure all changes follow vibe coding principles
- **Architecture Consistency**: Check new code follows established patterns
- **Error Handling**: Verify comprehensive error handling is in place
- **Testing Coverage**: Ensure changes include appropriate tests

### Workflow Updates
- **Autonomous Validation**: Check workflows can execute without user input
- **Clear Commands**: Ensure all commands are executable and well-documented
- **Error Recovery**: Include error handling and recovery mechanisms
- **Testing**: Validate workflow changes before committing

## Quality Standards

### Testing Requirements
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **Workflow Tests**: Validate YAML workflows load and execute correctly
- **Error Handling Tests**: Test error conditions and fallback mechanisms

### Documentation Requirements
- **API Documentation**: Document all public interfaces
- **Architecture Docs**: Maintain design documentation
- **ADRs**: Record significant decisions
- **README Updates**: Keep project README current

### Performance Standards
- **Caching**: Use caching for expensive operations
- **Lazy Loading**: Load resources only when needed
- **Error Costs**: Minimize performance impact of error handling
- **Memory Usage**: Monitor memory usage for long-running operations

## Common Patterns

### Error Handling Pattern
```python
try:
    # Main operation
    result = risky_operation()
    return result
except SpecificException as e:
    logger.error(f"Specific error occurred: {e}")
    # Handle specific case
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Fallback behavior
    return fallback_result()
```

### YAML Workflow Pattern
```yaml
name: "Descriptive Workflow Name"
description: "Clear description of what this workflow does"
triggers:
  - "keyword patterns that trigger this workflow"
project_types:
  - "project types this applies to"
dependencies:
  - "required tools or conditions"
conditions:
  - "when this workflow should be used"
commands:
  - "echo '🔍 INFORMATIONAL HEADER'"
  - "executable_command --with-args"
  - "echo '✅ Status update'"
```

### Caching Pattern
```python
class CachedLoader:
    def __init__(self):
        self._cache = {}

    def load_data(self, key: str):
        if key not in self._cache:
            self._cache[key] = expensive_operation(key)
        return self._cache[key]
```

## Maintenance Practices

### Regular Reviews
- **Code Quality**: Regular code quality checks
- **Documentation Updates**: Keep docs synchronized with code
- **Dependency Updates**: Regular dependency updates and security audits
- **Performance Monitoring**: Monitor performance characteristics

### Refactoring Guidelines
- **Small Steps**: Make incremental improvements
- **Test Coverage**: Ensure tests cover refactored code
- **Backward Compatibility**: Maintain compatibility during transitions
- **Documentation Updates**: Update docs with refactoring changes

### Technical Debt Management
- **Identify Debt**: Document technical debt and its impact
- **Prioritize Fixes**: Address high-impact debt first
- **Incremental Improvement**: Make small improvements over time
- **Prevent Accumulation**: Establish practices to prevent new debt
