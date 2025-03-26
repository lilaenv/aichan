# AIchan

**AIchan** is an AI-powered Discord bot that leverages advanced natural language processing capabilities to enable interactive communication with users.

## Getting Started

This guide explains how to run AIchan locally on macOS.

### Prerequisites

The following preparations are required:
- Python runtime environment
- Anthropic API Key
- OpenAI API Key
- Discord Bot configuration

For detailed information, please refer to [PREREQUISITES.md](https://github.com/lilaenv/aichan/blob/main/docs/PREREQUISITES.md).

### Set up

**1. Clone repository and install dependencies**

```
# ----- clone repo -----
git clone https://github.com/lilaenv/aichan.git
cd aichan/

# ----- install dependencies -----
# with uv
uv sync

# without uv
pip install -r requirements.txt
```

**2. Prepare env file**

This application requires a `.env` file for configuration. Follow these steps:

- Copy the `.env.example` file and rename it to `.env`.
- Fill in the actual values.

**3. Write system prompts**

> [!IMPORTANT]
> When operating on a public server, it is strongly recommended to use robust system prompts with security measures in place.

Make a copy of `.prompt.example.yml` and rename it to `.prompt.yml`. Set system prompts for each feature.

Example:

```yaml
# For `/chat` command
chat_system: |
  You are a helpful assistant that strictly follows the [System Instructions].

  # [System Instructions]

  Detail instructions...
```

### Run the Bot

Finally, make sure all values in the `.env` file and `.prompt.yml` file are filled in correctly, and then execute the following:

```
python -m src.aichan [--log <log_level>]
```

**Note:** `--log <log_level>` is optional and allows you to set the log level. Available values are DEBUG, INFO, WARNING, ERROR, CRITICAL. If not specified, INFO will be used.

## Commands

Here are the available commands in Discord and planned implementations.

> [!NOTE]
> All AIchan commands are managed by their own Access Type system, separate from Discord roles. Additionally, there are restrictions on the number of times certain commands can be used and which channels they can be used in. For details, please refer to the Note at the bottom of this section.

- Access Types are, in order of highest to lowest privilege: Admin, Advanced, Normal (no Access Type), and Blocked. Admin is set via environment variables, while Advanced and Blocked are managed through Access Management Commands.
- Some commands have daily usage limits. These are marked as "Enabled" under Limitation.
- The `/talk` command is restricted to specific channels. These channels must be configured by Admin users through Command Channel Commands.

### Access Management Commands

Manage user access permissions by granting or disabling access types in the database.

<table>
    <tr>
        <th>Command</th>
        <th>Description</th>
        <th>Access Type</th>
        <th>Limitation</th>
        <th>Status</th>
    </tr>
    <tr>
        <td><code>/grant_access</code></td>
        <td>Grant a access type to a user</td>
        <td>Admin</td>
        <td>Unlimited</td>
        <td>Implemented</td>
    </tr>
    <tr>
        <td><code>/ck_access</code></td>
        <td>Check the user's access type</td>
        <td>Admin</td>
        <td>Unlimited</td>
        <td>Implemented</td>
    </tr>
    <tr>
        <td><code>/disable_access</code></td>
        <td>Disable a user's access type</td>
        <td>Admin</td>
        <td>Unlimited</td>
        <td>Implemented</td>
    </tr>
</table>

### Command Channel Commands

<table>
    <tr>
        <th>Command</th>
        <th>Description</th>
        <th>Access Type</th>
        <th>Limitation</th>
        <th>Status</th>
    </tr>
    <tr>
        <td><code>/add_ch</code></td>
        <td>Add a specific channel to the allowed command channels</td>
        <td>Admin</td>
        <td>Unlimited</td>
        <td>Implemented</td>
    </tr>
    <tr>
        <td><code>/ls_ch</code></td>
        <td>List channels where commands can be executed</td>
        <td>Not Blocked</td>
        <td>Unlimited</td>
        <td>Implemented</td>
    </tr>
    <tr>
        <td><code>/rm_ch</code></td>
        <td>Remove a specific channel from the allowed command channels</td>
        <td>Admin</td>
        <td>Unlimited</td>
        <td>Implemented</td>
    </tr>
</table>

### Interaction (with AIchan) Commands

<table>
    <tr>
        <th>Command</th>
        <th>Description</th>
        <th>Access Type</th>
        <th>Limitation</th>
        <th>Status</th>
    </tr>
    <tr>
        <td><code>/chat</code></td>
        <td>Chat with AIchan in message channel</td>
        <td>Not Blocked</td>
        <td>Enabled</td>
        <td>Implemented</td>
    </tr>
    <tr>
        <td><code>/fixpy</code></td>
        <td>Detect and fix bugs and errors in Python code</td>
        <td>Not Blocked</td>
        <td>Unlimited</td>
        <td>Implemented</td>
    </tr>
    <tr>
        <td><code>/talk</code></td>
        <td>Create thread and start chat with AIchan</td>
        <td>Not Blocked</td>
        <td>Enabled</td>
        <td>Implemented</td>
    </tr>
</table>

### Limit Commands

<table>
    <tr>
        <th>Command</th>
        <th>Description</th>
        <th>Access Type</th>
        <th>Limitation</th>
        <th>Status</th>
    </tr>
    <tr>
        <td><code>/ck_limit</code></td>
        <td>Check your current command usage count</td>
        <td>Not Blocked</td>
        <td>Unlimited</td>
        <td>Implemented</td>
    </tr>
    <tr>
        <td><code>/limit</code></td>
        <td>Set daily usage limits for restricted commands</td>
        <td>Admin</td>
        <td>Unlimited</td>
        <td>Implemented</td>
    </tr>
</table>

### Support Commands

<table>
    <tr>
        <th>Command</th>
        <th>Description</th>
        <th>Access Type</th>
        <th>Limitation</th>
        <th>Status</th>
    </tr>
    <tr>
        <td><code>/help</code></td>
        <td>Displays the list of available commands</td>
        <td>All users</td>
        <td>Unlimited</td>
        <td>Planned</td>
    </tr>
    <tr>
        <td><code>/info</code></td>
        <td>Shows information about the application</td>
        <td>All users</td>
        <td>Unlimited</td>
        <td>Planned</td>
    </tr>
</table>

## Contributing

For bug reports and feature proposals, please refer to [CONTRIBUTING.md](https://github.com/lilaenv/aichan/blob/main/docs/CONTRIBUTING.md). The document includes issue templates and guidelines for contributing. We welcome contributions from everyone.
