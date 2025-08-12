# Event Bridge Log Analytics - Shared Package

[![PyPI version](https://badge.fury.io/py/event-bridge-log-shared.svg)](https://badge.fury.io/py/event-bridge-log-shared)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Portfolio Project**: A production-grade shared library demonstrating enterprise-level Python packaging, automated CI/CD, and modern DevOps practices.

## 🎯 **Project Overview**

This package serves as the foundational shared library for a microservices-based Event Bridge Log Analytics Platform. It demonstrates advanced software engineering practices including:

- **Type-safe event modeling** with Pydantic v2
- **Automated release management** with semantic versioning
- **Modern CI/CD pipelines** with GitHub Actions
- **Secure PyPI publishing** using trusted publishers (OIDC)
- **Enterprise-grade code quality** with comprehensive testing and linting

## 🏗️ **Architecture & Design**

### **Event-Driven Architecture**
The package provides standardized event models for a distributed microservices architecture:

```python
from event_bridge_log_shared.models.events.user import UserRegisteredEvent
from event_bridge_log_shared.models.events.ecommerce import OrderCreatedEvent

# Type-safe event creation with automatic validation
user_event = UserRegisteredEvent(
    user_id="user123",
    email="user@example.com",
    username="newuser",
    registration_method="email",
    terms_accepted=True,
    source="user-service"
)

# Events include automatic timestamping, ID generation, and metadata
print(f"Event ID: {user_event.event_id}")
print(f"Timestamp: {user_event.timestamp}")
```

### **Type Safety & Validation**
All events extend `BaseEvent` with built-in features:

- **Automatic UUID generation** for event tracking
- **ISO 8601 timestamps** for precise timing
- **Environment context** (dev/staging/production)
- **Correlation IDs** for distributed tracing
- **Extensible metadata** system
- **AWS EventBridge compatibility**

### **Utility Functions**
Service-agnostic helpers for AWS resource management:

```python
from event_bridge_log_shared.utils import normalize_env, prefix_name, build_role_arn

env = normalize_env("development")  # -> "dev"
bus_name = prefix_name(env, "event-bridge-log-bus")  # -> "dev-event-bridge-log-bus"
role_arn = build_role_arn("123456789012", "MyExecutionRole")
```

## 🚀 **Technical Highlights**

### **Modern Python Packaging**
- **Python 3.13** with cutting-edge features
- **Hatchling** build backend for optimal package building
- **UV** for ultra-fast dependency management
- **Dynamic versioning** from single source

### **Production-Grade CI/CD**
- **Automated releases** with semantic version bumping
- **GitHub Actions workflows** with job orchestration
- **Repository dispatch** for cross-workflow communication
- **Trusted Publisher** PyPI deployment (no API keys required)
- **Comprehensive testing** with pytest and coverage reporting

### **Code Quality & Security**
- **100% type coverage** with mypy strict mode
- **Black** and **Ruff** for consistent code formatting
- **Pre-commit hooks** for automated quality checks
- **Security scanning** and dependency validation
- **Branch protection** and automated testing

## 📦 **Installation**

```bash
# From PyPI (recommended)
pip install event-bridge-log-shared

# From source (development)
pip install git+https://github.com/cblack2008/event-bridge-log-shared.git
```

## 🔧 **Development**

### **Quick Start**
```bash
git clone https://github.com/cblack2008/event-bridge-log-shared.git
cd event-bridge-log-shared

# One-command developer setup
make dev-setup
```

### **Available Commands**
```bash
make test              # Run tests with coverage
make lint              # Lint and type check
make format            # Auto-format code
make coverage-html     # Generate HTML coverage report
make clean             # Remove build artifacts
```

### **Release Process**
The project features a fully automated release pipeline:

1. **Trigger Release**: Run "Release" GitHub Action
2. **Automatic PR**: Creates release branch with version bump
3. **Auto-merge**: PR automatically merges after CI passes
4. **Auto-tag**: Creates Git tag and GitHub Release
5. **Auto-deploy**: Publishes to PyPI via trusted publisher

## 🔒 **Security & Best Practices**

- **Zero secrets in code**: All sensitive data via environment variables
- **OIDC authentication**: Modern secure publishing without API keys
- **Input validation**: All data validated with Pydantic models
- **Type safety**: Full type hints prevent runtime errors
- **Dependency scanning**: Automated vulnerability detection

## 🛠️ **Technology Stack**

| Category | Technologies |
|----------|-------------|
| **Language** | Python 3.13 |
| **Packaging** | Hatchling, UV, PyPI |
| **Validation** | Pydantic v2, Type Hints |
| **Testing** | Pytest, Coverage.py, Pre-commit |
| **CI/CD** | GitHub Actions, Trusted Publishers |
| **Code Quality** | Black, Ruff, MyPy |
| **Infrastructure** | AWS EventBridge, IAM, CloudFormation |

## 📊 **Project Metrics**

- **Test Coverage**: 85%+ maintained
- **Type Coverage**: 100% with mypy strict mode
- **Code Quality**: A+ rating with comprehensive linting
- **Automation**: Fully automated release pipeline
- **Documentation**: Complete API and usage documentation

## 🎓 **Learning Outcomes**

This project demonstrates mastery of:

- **Enterprise Python Development** with modern tooling
- **CI/CD Pipeline Design** and workflow orchestration
- **Package Distribution** and dependency management
- **Type System Design** with advanced Pydantic usage
- **DevOps Automation** with GitHub Actions
- **Security Best Practices** in software delivery

## 📋 **Requirements**

- **Python**: 3.13+
- **Dependencies**: See `pyproject.toml` for complete list
- **Development**: UV package manager recommended

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Ensure all checks pass: `make test lint`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 **Related Projects**

- [Event Bridge Log Analytics](https://github.com/cblack2008/event-bridge-log) - Main microservices platform

## 📞 **Contact**

- **Repository**: [GitHub](https://github.com/cblack2008/event-bridge-log-shared)
- **Issues**: [GitHub Issues](https://github.com/cblack2008/event-bridge-log-shared/issues)
- **Author**: cblack2008

---

*This is a portfolio project demonstrating enterprise-level software engineering practices and modern Python development workflows.*
