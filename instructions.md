# Project Instructions

## Overview
This document serves as the single source of truth for project-specific instructions, business context, and development guidelines.

## Development Workflow
All feature development should follow the structured approach defined in `.cursorrules`:
1. Clarifying questions before implementation
2. Teaching explanations of design decisions
3. API contracts and security considerations
4. Step-by-step implementation with tests
5. Proper commit messages and PR documentation

## Business Context
- **Project Type**: [To be filled based on your project]
- **Target Users**: [To be defined]
- **Key Business Metrics**: [To be defined]
- **Compliance Requirements**: [To be defined]

## Security Policies
- All secrets must be stored in secure secrets manager (specify which one)
- Authentication and authorization required for all protected endpoints
- Input validation mandatory for all user inputs
- Sensitive data encryption at rest and in transit
- Audit logging for all security-relevant operations

## Architecture Guidelines
- Keep changes small and self-contained (< 300 LOC per PR when possible)
- Maintain backward compatibility unless explicitly approved
- Follow existing code style and lint rules
- Prefer composition over inheritance
- Document all public APIs

## Testing Standards
- Unit tests required for all business logic
- Integration tests for API endpoints
- Manual QA checklist for UI changes
- Performance tests for critical paths
- Security tests for authentication/authorization

## Deployment Process
- All changes go through PR review
- CI/CD pipeline must pass before merge
- Staging deployment before production
- Rollback plan documented for each release
- Post-deploy smoke tests and monitoring

## Contact & Escalation
- Technical questions: [To be defined]
- Security concerns: [To be defined]
- Business decisions: [To be defined]

---
*Last updated: [Date will be maintained automatically]*
