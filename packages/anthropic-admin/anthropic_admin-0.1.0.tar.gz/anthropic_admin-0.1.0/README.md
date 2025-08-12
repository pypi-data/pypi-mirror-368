# Anthropic Admin SDK

**⚠️ UNOFFICIAL Python SDK** for Anthropic Admin API

[![PyPI version](https://badge.fury.io/py/anthropic-admin.svg)](https://badge.fury.io/py/anthropic-admin)
[![Python Support](https://img.shields.io/pypi/pyversions/anthropic-admin.svg)](https://pypi.org/project/anthropic-admin/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python SDK for managing Anthropic organizations, workspaces, members, and API keys through the Admin API.

## ⚠️ Important Disclaimer

This is an **unofficial** SDK not affiliated with or endorsed by Anthropic. Use at your own discretion and ensure compliance with Anthropic's terms of service.

## 🚀 Installation

```bash
pip install anthropic-admin
```

## 🔑 Prerequisites

- **Admin API Key**: You need an Admin API key (starting with `sk-ant-admin...`) 
- **Organization Admin Role**: Only organization admins can provision Admin API keys
- **Organization Account**: Admin API is unavailable for individual accounts

## 📋 Features

- **Organization Members**: List, update roles, and remove members
- **Invitations**: Create, list, and manage organization invites  
- **Workspaces**: Create, list, archive, and manage workspace members
- **API Keys**: List and manage organization API keys
- **Type Safety**: Full type hints and Pydantic models
- **Error Handling**: Comprehensive exception handling
- **Rate Limiting**: Built-in respect for API rate limits

## 🏃‍♂️ Quick Start

```python
from anthropic_admin import AnthropicAdminClient

# Initialize client with your admin API key
client = AnthropicAdminClient(api_key="sk-ant-admin-...")

# List organization members
members = client.members.list()
for member in members:
    print(f"{member.email} - {member.role}")

# Create a new workspace
workspace = client.workspaces.create(name="ML Team")
print(f"Created workspace: {workspace.name}")

# Invite a new developer
invite = client.invites.create(
    email="newdev@company.com",
    role="developer"
)
print(f"Invited: {invite.email}")

# List API keys
api_keys = client.api_keys.list(status="active")
for key in api_keys:
    print(f"API Key: {key.name} - {key.status}")
```

## 📚 Detailed Usage

### Managing Organization Members

```python
# List all members
members = client.members.list(limit=50)

# Update member role
client.members.update(user_id="user_123", role="developer")

# Remove member
client.members.remove(user_id="user_456")
```

### Managing Invitations

```python
# Create invite
invite = client.invites.create(
    email="engineer@company.com",
    role="claude_code_user"
)

# List pending invites
invites = client.invites.list()

# Delete invite
client.invites.delete(invite_id=invite.id)
```

### Managing Workspaces

```python
# Create workspace
workspace = client.workspaces.create(name="Production")

# List workspaces
workspaces = client.workspaces.list(include_archived=False)

# Archive workspace
client.workspaces.archive(workspace_id=workspace.id)

# Manage workspace members
client.workspaces.members.add(
    workspace_id=workspace.id,
    user_id="user_123",
    workspace_role="workspace_developer"
)

client.workspaces.members.update_role(
    workspace_id=workspace.id,
    user_id="user_123", 
    workspace_role="workspace_admin"
)

client.workspaces.members.remove(
    workspace_id=workspace.id,
    user_id="user_123"
)
```

### Managing API Keys

```python
# List API keys for specific workspace
api_keys = client.api_keys.list(
    workspace_id="wrkspc_123",
    status="active",
    limit=25
)

# Update API key
client.api_keys.update(
    api_key_id="key_456",
    status="inactive",
    name="Updated Key Name"
)
```

## 🔧 Advanced Usage

### Bulk Operations

```python
# Promote all users to developers
for member in client.members.list():
    if member.role == "user":
        client.members.update(member.id, role="developer")
        print(f"Promoted {member.email} to developer")

# Setup new team workspace
workspace = client.workspaces.create(name="Data Science Team")
team_emails = ["alice@company.com", "bob@company.com"]

for email in team_emails:
    # Invite to organization
    invite = client.invites.create(email=email, role="developer")
    print(f"Invited {email} to organization")
```

### Error Handling

```python
from anthropic_admin.exceptions import (
    AnthropicAdminError,
    AuthenticationError,
    PermissionError,
    NotFoundError,
    RateLimitError
)

try:
    members = client.members.list()
except AuthenticationError:
    print("Invalid admin API key")
except PermissionError:
    print("Insufficient permissions")
except RateLimitError:
    print("Rate limit exceeded, please wait")
except AnthropicAdminError as e:
    print(f"API error: {e}")
```

## 🔒 Security Best Practices

1. **Never hardcode API keys** - Use environment variables
2. **Use least privilege** - Only grant necessary permissions
3. **Rotate keys regularly** - Monitor and update API keys
4. **Audit access** - Regularly review organization members and roles

```python
import os
from anthropic_admin import AnthropicAdminClient

# ✅ Good: Use environment variables
client = AnthropicAdminClient(
    api_key=os.getenv("ANTHROPIC_ADMIN_API_KEY")
)

# ❌ Bad: Never hardcode keys
# client = AnthropicAdminClient(api_key="sk-ant-admin-...")
```

## 📖 API Reference

### Organization Roles

| Role | Permissions |
|------|-------------|
| `user` | Can use Workbench |
| `claude_code_user` | Can use Workbench and Claude Code |
| `developer` | Can use Workbench and manage API keys |
| `billing` | Can use Workbench and manage billing |
| `admin` | All permissions plus user management |

### Workspace Roles

| Role | Permissions |
|------|-------------|
| `workspace_user` | Basic workspace access |
| `workspace_developer` | Can manage workspace API keys |
| `workspace_admin` | Full workspace management |

## 🧪 Development

```bash
# Clone repository
git clone https://github.com/yourusername/anthropic-admin
cd anthropic-admin

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Build package
python -m build
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/anthropic-admin/issues)
- **Documentation**: [GitHub Docs](https://github.com/yourusername/anthropic-admin/blob/main/docs/)

## ⚠️ Disclaimer

This SDK is not officially supported by Anthropic. Use responsibly and in accordance with Anthropic's terms of service. The authors are not responsible for any misuse or damages.
