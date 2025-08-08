# AZTP Client Python

Enterprise-grade identity service client for secure workload identity management using AZTP standards.

---

## Table of Contents

- [Installation](#installation)
- [Requirements](#requirements)
- [Trusted Domains](#trusted-domains)
- [Quick Start](#quick-start)
- [Core Methods](#core-methods)
  - [Identity Management](#identity-management)
  - [Policy Management](#policy-management)
  - [OIDC Authentication](#oidc-authentication)
- [Examples](#examples)
- [Error Handling](#error-handling)
- [License](#license)

---

## Installation

```bash
pip install aztp-client
```

## Requirements

- Python 3.8 or higher
- aiohttp (for OIDC functionality)

---

## Trusted Domains

The AZTP client maintains a whitelist of trusted domains for use with the `trustDomain` parameter. If not specified, defaults to `aztp.network`.

```python
from aztp_client import whiteListTrustDomains
print("Available trusted domains:", whiteListTrustDomains)
```

**Current Trusted Domains:**

- `gptarticles.xyz`
- `gptapps.ai`
- `vcagents.ai`

---

## Quick Start

```python
from aztp_client import Aztp

client = Aztp(api_key="your-api-key")
agent = await client.secure_connect({}, "service1", config={"isGlobalIdentity": False})
```

---

## Core Methods

### Identity Management

| Method                                                                            | Description                                                                         |
| --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `secure_connect(crew_agent, name, config)`                                        | Create a secure connection for a workload                                           |
| `verify_identity(agent)`                                                          | Verify the identity of a secured agent                                              |
| `verify_authorize_identity_connection(from_aztp_id, to_aztp_id, policyCode=None)` | Verify and authorize connection between two agents (optionally using a policy code) |
| `get_identity(agent)`                                                             | Get identity information for a secured agent                                        |
| `get_identity_by_name(name)`                                        | Get identity information by name                                   |
| `discover_identity(trust_domain, requestor_identity)`                             | Discover identities based on parameters                                             |
| `revoke_identity(aztp_id, reason)`                                                | Revoke an AZTP identity                                                             |
| `reissue_identity(aztp_id)`                                                       | Restore a previously revoked identity                                               |
| `link_identities(source_identity, target_identity, relationship_type, metadata)`  | Link two workload identities together                                               |

### Policy Management

| Method                                                 | Description                                                                       |
| ------------------------------------------------------ | --------------------------------------------------------------------------------- |
| `get_policy(aztp_id)`                                  | Get access policy for a specific AZTP identity                                    |
| `get_policy_value(policies, filter_key, filter_value)` | Filter and extract a specific policy statement                                    |
| `is_action_allowed(policy, action)`                    | Check if an action is allowed by a policy statement                               |
| `check_identity_policy_permissions(aztp_id, options)`  | Get action permissions for an identity based on policy, actions, and trust domain |

#### Policy Statement Structure

- The `Statement` field in a policy can be either a single dict or a list of dicts.
- The `Action` field can be a string or a list of strings.
- The `is_action_allowed` method normalizes both cases and works for all valid policy structures.

#### Example: Check if an action is allowed

```python
policy_statement = aztpClient.get_policy_value(identity_access_policy, "code", "policy:0650537f8614")
if policy_statement:
    is_allowed = aztpClient.is_action_allowed(policy_statement, "read")
    print(f"Is 'read' allowed? {is_allowed}")
```

**Example Policy Statement:**

```json
{
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["read", "write"]
    },
    {
      "Effect": "Deny",
      "Action": "delete"
    }
  ]
}
```

### Example: Verify and Authorize Identity Connection

```python
# Verify and authorize the connection between two agents (optionally with a policy code)
from_aztp_id = "aztp://example.com/workload/production/node/agentA"
to_aztp_id = "aztp://example.com/workload/production/node/agentB"

# Basic usage (no policy code)
is_valid_connection = await aztpClient.verify_authorize_identity_connection(from_aztp_id, to_aztp_id)
print("Connection valid:", is_valid_connection)

# With a policy code
default_policy_code = "policy:1234567890abcdef"
is_valid_connection = await aztpClient.verify_authorize_identity_connection(from_aztp_id, to_aztp_id, policyCode=default_policy_code)
print("Connection valid with policy:", is_valid_connection)
```

### OIDC Authentication

The AZTP client includes support for OpenID Connect (OIDC) authentication, allowing you to integrate with various identity providers.

#### OIDC Methods

| Method | Description |
|--------|-------------|
| `oidc.login(provider, aztp_id, options)` | Initiate OIDC login with a specified provider |
| `oidc.validate_token(token)` | Validate a JWT token and get user information |

#### OIDC Login Options

The `login` method accepts the following options:

```python
options = {
    "return_url": str,     # Optional callback URL
    "stateless": bool      # Whether to use stateless authentication (default: True)
}
```

#### Example: OIDC Authentication

```python
import asyncio
from aztp_client import Aztp

async def main():
    # Initialize the AZTP client
    client = Aztp(
        api_key="your_api_key"
    )

    # Example 1: Initiate OIDC login with Google
    try:
        login_response = await client.oidc.login(
            provider="google",
            aztp_id="aztp://example.com/workload/production/node/my-service",
            options={
                "return_url": "https://your-app.com/callback"
            }
        )
        print("Redirect URL:", login_response["redirectUrl"])
    except Exception as e:
        print("Login failed:", str(e))

    # Example 2: Validate a token
    try:
        token = "your_token_here"  # Replace with actual token
        validation_response = await client.oidc.validate_token(token)
        
        if validation_response["valid"]:
            print("User Info:")
            print(f"  Name: {validation_response['user']['name']}")
            print(f"  Email: {validation_response['user']['email']}")
            print(f"  Provider: {validation_response['user']['provider']}")
    except Exception as e:
        print("Token validation failed:", str(e))

if __name__ == "__main__":
    asyncio.run(main())
```

#### OIDC Response Types

**Login Response:**
```python
{
    "success": bool,
    "message": str,
    "redirect_url": str,
    "state": str,
    "token": Optional[str]
}
```

**Token Validation Response:**
```python
{
    "success": bool,
    "valid": bool,
    "user": {
        "sub": str,
        "email": str,
        "name": str,
        "provider": str,
        "agent": str
    },
    "token_type": str,
    "message": str
}
```

---

## Examples

### Identity Revocation and Reissue

```python
import os
import asyncio
from aztp_client import Aztp, whiteListTrustDomains
from dotenv import load_dotenv

load_dotenv()

async def main():
    api_key = os.getenv("AZTP_API_KEY")
    base_url = os.getenv("AZTP_BASE_URL")
    if not api_key:
        raise ValueError("AZTP_API_KEY is not set")

    aztpClient = Aztp(api_key=api_key, base_url=base_url)
    agent = {}
    agent_name = "astha-local/arjun"

    # Secure Connect
    print(f"Connecting agent: {agent_name}")
    localTestAgent = await aztpClient.secure_connect(agent, agent_name, {"isGlobalIdentity": False})
    print("AZTP ID:", localTestAgent.identity.aztp_id)

    # Verify
    print(f"Verifying identity for agent: {agent_name}")
    verify = await aztpClient.verify_identity(localTestAgent)
    print("Verify:", verify)

    # Revoke identity
    print(f"Revoking identity for agent: {agent_name}")
    revoke_result = await aztpClient.revoke_identity(localTestAgent.identity.aztp_id, "Revoked by user")
    print("Identity Revoked:", revoke_result)

    # Verify after revoke
    print(f"Verifying identity after revoke for agent: {agent_name}")
    is_valid_after_revoke = await aztpClient.verify_identity(localTestAgent)
    print("Identity Valid After Revoke:", is_valid_after_revoke)

    # Reissue identity
    print(f"Reissuing identity for agent: {agent_name}")
    reissue_result = await aztpClient.reissue_identity(localTestAgent.identity.aztp_id)
    print("Identity Reissued:", reissue_result)

    # Verify after reissue
    print(f"Verifying identity after reissue for agent: {agent_name}")
    is_valid_after_reissue = await aztpClient.verify_identity(localTestAgent)
    print("Identity Valid After Reissue:", is_valid_after_reissue)

    # Get and display policy information
    print(f"Getting policy information for agent: {agent_name}")
    identity_access_policy = await aztpClient.get_policy(localTestAgent.identity.aztp_id)

    # Extract a specific policy by code (replace with your actual policy code)
    policy = aztpClient.get_policy_value(
        identity_access_policy,
        "code",
        "policy:0650537f8614"  # Replace with your actual policy code
    )

    if policy:
        is_allow = aztpClient.is_action_allowed(policy, "read")
        print({"is_allow": is_allow})
        if is_allow:
            print({"actions": actions})
    else:
        print("Policy not found.")

        # Link identities
    print(f"Linking {agent_name}'s identity to another service")
    try:
        target_identity = "aztp://astha.ai/workload/production/node/partner-service"
        link_result = await aztpClient.link_identities(
            localTestAgent.identity.aztp_id,
            target_identity,
            "linked"
        )
        print(f"Identities linked successfully. Link ID: {link_result.get('_id')}")
    except Exception as e:
        print(f"Failed to link identities: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())

### Linking Identities

```python
import os
import asyncio
from aztp_client import Aztp
from dotenv import load_dotenv

load_dotenv()

async def main():
    api_key = os.getenv("AZTP_API_KEY")
    base_url = os.getenv("AZTP_BASE_URL")
    if not api_key:
        raise ValueError("AZTP_API_KEY is not set")

    aztpClient = Aztp(api_key=api_key, base_url=base_url)

    # Define the source and target identities
    source_identity = "aztp://astha.ai/workload/production/node/service-a"
    target_identity = "aztp://astha.ai/workload/production/node/service-b"

    # Link the two identities with a peer relationship
    try:
        result = await aztpClient.link_identities(
            source_identity=source_identity,
            target_identity=target_identity,
            relationship_type="linked",  # Can be "linked" or "parent"
        )
        print("Identity link created successfully:")
        print(f"Link ID: {result.get('_id')}")
        print(f"Source: {result.get('sourceIdentity')}")
        print(f"Target: {result.get('targetIdentity')}")
        print(f"Relationship: {result.get('relationshipType')}")
    except Exception as e:
        print(f"Error linking identities: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())

### Check Identity Policy Permissions

```python
# aztp_id is the full AZTP identity string
aztp_id = "aztp://aztp.local/workload/production/node/aj-agent-172"

# 1. Get all action permissions for an identity
permissions = await aztpClient.check_identity_policy_permissions(aztp_id)
print("Permissions (default):", permissions)

# 2. Get permissions for a specific policy
permissions_policy = await aztpClient.check_identity_policy_permissions(
    aztp_id,
    options={"policy_code": "policy:1589246d7b16"}
)
print("Permissions (policy_code):", permissions_policy)

# 3. Get permissions for specific actions
permissions_actions = await aztpClient.check_identity_policy_permissions(
    aztp_id,
    options={"actions": ["list_users", "read"]}
)
print("Permissions (actions):", permissions_actions)

# 4. Get permissions for a specific trust domain
permissions_trust = await aztpClient.check_identity_policy_permissions(
    aztp_id,
    options={"trust_domain": "aztp.network"}
)
print("Permissions (trust_domain):", permissions_trust)

# 5. Get permissions with all options
permissions_all = await aztpClient.check_identity_policy_permissions(
    aztp_id,
    options={
        "policy_code": "policy:1589246d7b16",
        "actions": ["read", "write"],
        "trust_domain": "aztp.network"
    }
)
print("Permissions (all options):", permissions_all)

# Note: You can use either snake_case or camelCase keys in the options dict.
```

---

## Error Handling

- **Connection Errors**: Handles network and server connectivity issues
- **Authentication Errors**: Manages API key and authentication failures
- **Validation Errors**: Validates input parameters and trust domains
- **Policy Errors**: Handles policy retrieval and validation failures

---

## License

MIT License
