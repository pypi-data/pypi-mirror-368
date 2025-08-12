# SenseTable


![SenseTable](./sense_table/statics/SenseTable-light.svg)


SenseTable helps you explore large-volumn of multi-modal AI data easily.

## Development

### Git Hooks

This project uses git hooks to ensure code quality and prevent broken code from being pushed. The hooks are stored in the `.githooks/` directory and shared with all developers.

The hooks will:

- **pre-commit**: Check for Python syntax errors, trailing whitespace, and basic code quality issues
- **pre-push**: Run the full test suite and ensure the git tree is clean

#### For New Developers

After cloning the repository, run the setup script to install hooks and configure the development environment:

```bash
# Run the post-clone setup (installs hooks automatically)
./scripts/post-clone-setup.sh
```

#### Installing Hooks (Manual)

If you need to reinstall hooks manually:

```bash
# Install hooks using make
make install-hooks

# Or run the script directly
./scripts/install-hooks.sh
```

#### Skipping Hooks (Emergency Only)

In emergency situations, you can skip the hooks:

```bash
git commit --no-verify  # Skip pre-commit hook
git push --no-verify    # Skip pre-push hook
```

### Running Tests

```bash
# Run all tests
make test

# Run only unit tests
make unit-test

# Run only integration tests
make integration-test
```

