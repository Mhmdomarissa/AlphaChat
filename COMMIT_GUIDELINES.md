# Commit Message Guidelines

## Format
Use the conventional commit format:
```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

## Types
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **build**: Changes that affect the build system or external dependencies
- **ci**: Changes to our CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files
- **revert**: Reverts a previous commit

## Scopes
Use relevant scope based on the area of change:
- **api**: API-related changes
- **ui**: User interface changes
- **db**: Database-related changes
- **auth**: Authentication/authorization
- **config**: Configuration changes
- **deps**: Dependency updates

## Examples

### Good Examples
```
feat(api): add POST /v1/users endpoint with validation

- Add user creation endpoint
- Include email validation and uniqueness check
- Add rate limiting (10 requests/minute)
- Return 201 on success, 400 on validation error

Closes #123
```

```
fix(auth): resolve JWT token expiration handling

- Fix token refresh logic in middleware
- Add proper error messages for expired tokens
- Update tests for edge cases

Fixes #456
```

```
docs(api): update authentication documentation

- Add examples for JWT token usage
- Document rate limiting policies
- Include error response formats
```

### Bad Examples
```
❌ update stuff
❌ fix bug
❌ WIP: working on feature
❌ Fixed the thing that was broken
```

## Rules
1. **Use imperative mood**: "add feature" not "added feature"
2. **Keep subject line under 50 characters**
3. **Capitalize the subject line**
4. **Don't end subject line with a period**
5. **Use body to explain what and why, not how**
6. **Separate subject from body with blank line**
7. **Wrap body at 72 characters**
8. **Reference issues and pull requests when relevant**

## Breaking Changes
For breaking changes, add `BREAKING CHANGE:` in the footer:
```
feat(api): change user endpoint response format

BREAKING CHANGE: User endpoint now returns `userId` instead of `id`
```

## Security-Related Commits
For security fixes, use the `security` type or add `[SECURITY]` prefix:
```
security(auth): fix SQL injection vulnerability in login

- Sanitize user input in authentication queries
- Add parameterized queries
- Update input validation

CVE-2023-XXXX
```

## Revert Commits
```
revert: feat(api): add POST /v1/users endpoint

This reverts commit 1234567890abcdef.

Reason: Endpoint caused performance issues in production
```

## Co-authored Commits
When pair programming:
```
feat(ui): add dark mode toggle

Co-authored-by: Jane Doe <jane@example.com>
```



