# `call` Command

Call a tool from a template (via stdio or HTTP transport).

## Functionality
- Executes the specified tool, prompting for missing configuration if needed.
- Handles both stdio and HTTP transports.
- Beautifies the tool response and error output.

## Options & Arguments
- `<template_name>`: Name of the template to use.
- `<tool_name>`: Name of the tool to call.
- `[json_args]`: Optional JSON string of arguments for the tool (e.g. '{"param": "value"}').

## Configuration
- Configuration for the template may be required; CLI will prompt if missing.
- For HTTP templates, server must be running.

## Example
```
call my_template my_tool '{"input": "value"}'
```

## When and How to Run
- Use to execute a tool from a deployed template.
- Run after configuring the template and ensuring the server is running (for HTTP transport).

## Example Output
```mcpt> call demo say_hello {"name": "Sam"}
🚀 Calling tool 'say_hello' from template 'demo'
Using stdio transport...
╭───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── MCP Tool Execution ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ 🔧 Running tool say_hello from template demo                                                                                                                                                                                                                                                                                                                                                                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
✅ Tool executed successfully
                                     Tool Result (1 properties)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Property                  ┃ Value                                                   ┃ Type       ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ result                    │ Hello Sam! Greetings from "MCP Platform"!               │ str        │
└───────────────────────────┴─────────────────────────────────────────────────────────┴────────────┘
```
