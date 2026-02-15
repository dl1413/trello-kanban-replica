# Security Policy

## Supported Versions

We actively maintain the latest version of the RL Environment Framework. Security updates are applied to the main branch.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it by:

1. Opening a GitHub issue with the `security` label
2. Or emailing the maintainers directly (if sensitive)

**Do not** disclose security vulnerabilities publicly until they have been addressed.

## Security Measures

### Dependency Management

All dependencies are pinned to specific versions and regularly audited for vulnerabilities:

```bash
# Check dependencies for vulnerabilities
make security
```

### Known Issues and Resolutions

#### Weights & Biases (wandb) - RESOLVED ✅

**Issue**: SSRF vulnerability in wandb versions <= 0.17.0
- **CVE**: Server-Side Request Forgery (Withdrawn Advisory)
- **Affected versions**: <= 0.17.0
- **Resolution**: Removed from default dependencies (2024-02-15)
- **Alternative**: Use TensorBoard (included) or install wandb >= 0.18.0 manually

### Code Security

1. **No eval() usage**: All string-to-code conversions use `ast.literal_eval()`
2. **Input validation**: All user inputs are validated
3. **Proper permissions**: GitHub Actions uses explicit read-only permissions
4. **Type safety**: Full type hints with mypy checking
5. **Code scanning**: Automated CodeQL analysis

### CI/CD Security

Our CI/CD pipeline includes:
- **CodeQL scanning**: Automated vulnerability detection
- **Dependency scanning**: Regular checks with safety/bandit
- **Permission boundaries**: Minimal GITHUB_TOKEN permissions
- **Signed commits**: Co-authored commits for traceability

### Best Practices

When contributing:

1. Never commit secrets or API keys
2. Use environment variables for sensitive data
3. Keep dependencies up to date
4. Run security checks before committing:
   ```bash
   make security
   ```

### Vulnerability Scan Results

Last scanned: 2024-02-15

```
Dependencies checked: 12
Vulnerabilities found: 0
Status: ✅ PASS
```

All core dependencies are verified clean:
- gymnasium==0.29.1
- numpy==1.24.4
- pyyaml==6.0.1
- matplotlib==3.7.5
- pandas==2.0.3
- pytest==7.4.4
- pytest-cov==4.1.0
- black==23.12.1
- flake8==7.0.0
- tensorboard==2.13.0
- tqdm==4.66.1
- mypy==1.8.0

## Security Audit History

| Date       | Action                              | Result |
|------------|-------------------------------------|--------|
| 2024-02-15 | Removed wandb (SSRF vulnerability) | ✅ Fixed |
| 2024-02-15 | CodeQL scan                         | ✅ Pass  |
| 2024-02-15 | Dependency audit                    | ✅ Clean |
| 2024-02-15 | GitHub Actions permissions audit    | ✅ Pass  |

## Contact

For security concerns, please contact the maintainers through GitHub issues.
