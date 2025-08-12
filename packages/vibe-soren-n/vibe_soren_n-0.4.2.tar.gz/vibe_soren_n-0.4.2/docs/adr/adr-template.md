# ADR Template

> Copy this template to create new Architecture Decision Records (ADRs)

## ADR-XXX: [Title]

**Date**: YYYY-MM-DD
**Status**: [Proposed | Accepted | Deprecated | Superseded]
**Deciders**: [Names of people involved in decision]

### Context

What is the issue that we're seeing that is motivating this decision or change?

### Decision

What is the change that we're proposing or have agreed to implement?

### Rationale

Why are we making this decision? What alternatives did we consider?

### Consequences

What becomes easier or more difficult to do and any risks introduced by this change?

### Implementation

How will this decision be implemented? What are the steps?

### Notes

Any additional information, links, or context that might be helpful.

---

## Example ADR

### ADR-001: YAML-Based Workflow System

**Date**: 2025-08-10
**Status**: Accepted
**Deciders**: Development Team

#### Context

Workflows were hardcoded in Python files, making them difficult to update without code changes. This created friction for workflow modifications and made it harder for non-technical users to contribute workflow improvements.

#### Decision

Implement a YAML-based workflow system with external workflow definitions and a loader system that falls back to Python workflows.

#### Rationale

- **Separation of Concerns**: Code and data should be separate for better maintainability
- **Independent Updates**: Workflows can be modified without code changes
- **Version Control**: Workflow changes can be tracked independently
- **Accessibility**: YAML is more accessible to non-technical users than Python
- **Backward Compatibility**: Fallback system ensures no disruption during transition

Alternatives considered:
- JSON format (rejected: less human-readable)
- Database storage (rejected: adds complexity and dependencies)
- Configuration files (rejected: less structured than YAML)

#### Consequences

**Easier**:
- Updating workflow definitions
- Adding new workflows
- Version controlling workflow changes
- Non-technical contributions to workflows

**More Difficult**:
- Initial migration complexity
- Need to maintain two systems during transition
- Additional error handling for file operations

**Risks**:
- YAML parsing errors could break workflow loading
- File system dependencies could cause issues in some environments
- Performance impact from file I/O operations

#### Implementation

1. Create `models.py` with `Workflow` dataclass
2. Implement `loader.py` with YAML parsing and caching
3. Update `core.py` to use loader with fallback
4. Migrate existing workflows to YAML format
5. Add comprehensive error handling and logging

#### Notes

- Uses PyYAML for parsing workflow definitions
- Implements in-memory caching for performance
- Maintains full backward compatibility with Python workflows
- Follows vibe philosophy of autonomous operation
