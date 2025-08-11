<h1 align="center">Codius CLI</h1>
<p align="center">
    Coding assistant for domain-driven design projects in ASP.NET Core.
</p>

<p align="center"><code>pip install codius</code></p>

<p align="center">
  <img src="resources/images/screenshot_3.png" alt="Codius CLI screenshot" width="650"/>
</p>

<p align="center">
  <a href="https://pypi.org/project/codius/">
    <img src="https://img.shields.io/pypi/v/codius" alt="PyPI version">
  </a>
  <a href="https://github.com/runemalm/codius-cli/actions/workflows/release.yml">
    <img src="https://github.com/runemalm/codius-cli/actions/workflows/release.yml/badge.svg" alt="Build status">
  </a>
  <img src="https://img.shields.io/pypi/l/codius" alt="License">
  <a href="https://pepy.tech/project/codius">
    <img src="https://static.pepy.tech/badge/codius" alt="Downloads">
  </a>
  <a href="https://pypi.org/project/codius/">
    <img src="https://img.shields.io/pypi/pyversions/codius" alt="Python versions">
  </a>
</p>

---

## Why Codius?

> Free domain-driven designers from boilerplate and let them focus on modeling.


Codius is your coding assistant for domain-driven design — built to take care of the repetitive tasks that just have to get done.

Instead of manually writing boilerplate for aggregates, methods, repositories, and other building blocks, you describe the changes you want to make. Codius takes care of translating those changes into code, aligned with the [OpenDDD.NET](https://www.openddd.net) framework.

This frees you up to focus on what really matters: modeling your domain and evolving your design.  
Refinements become faster, iteration cycles shorter, and the feedback loop tighter.

With Codius, your ideas move from thought to implementation without getting lost in scaffolding.

If you’re passionate about DDD, code quality, and improving developer flow, try Codius — or help shape it by contributing to its development.

---

## Example

Say you want a `Book` aggregate with `Title`, `Author`, and `Price`, and a method to apply discounts.

Just tell Codius:

```
> Create a Book aggregate with Title, Author, and Price.  
Add a method to apply a discount to the Price.
```

Codius handles the boilerplate — aggregate, method, repository — so you can focus on the model.

---

## Quickstart

```bash
$ pip install codius    # Temporary package name
$ cd /your/project/root # Go to your project's root
$ codius                # Starts Codius CLI
```

On first run, Codius will create `.codius/config.yaml` and initialize a modeling session.

---

## Compatibility

Codius is designed for projects built with [OpenDDD.NET](https://www.openddd.net) — a framework for Domain-Driven Design in .NET.

It works directly on your existing codebase, generating and modifying code according to OpenDDD.NET’s conventions.

Whether you’re evolving your domain model or adding new building blocks, Codius helps you stay consistent and productive within the framework’s structure.

---

## Slash Commands

| Command         | Description |
|----------------|-------------|
| `/clear`        | Reset session state and history |
| `/clearhistory` | Reset session history |
| `/compact`      | Summarize and condense history |
| `/model`        | Change LLM provider/model |
| `/approval`     | Switch approval mode (suggest/auto) |
| `/sessions`     | List previous sessions |
| `/history`      | Show session history |

---

## Requirements

- Python 3.9 to 3.12
- A project built with [OpenDDD.NET](https://www.openddd.net)
- OpenAI or Anthropic API key (set in `config.yaml` or use `/model` in the CLI)

---

## Configuration

When you run Codius for the first time, it creates a `.codius/config.yaml` file in your project root.

This file controls how Codius behaves — including which LLM provider it uses, how verbose it is, and whether changes are auto-approved or suggested.

### Example

```yaml
debug: true
debug_llm: false
log_level: warning
approval_mode: suggest

llm:
  provider: openai
  openai:
    model: gpt-4o
    api_key: sk-...         # Or leave blank to use the OPENAI_API_KEY environment variable
  anthropic:
    model: claude-3-opus
```

### Config Options

| Key              | Type     | Description |
|------------------|----------|-------------|
| `debug`          | `bool`   | Enables general debug output in the CLI |
| `debug_llm`      | `bool`   | Logs LLM request and response payloads |
| `log_level`      | `str`    | Controls log verbosity: `info`, `warning`, or `error` |
| `approval_mode`  | `str`    | Determines if changes are auto-applied:<br>• `suggest` — manual approval<br>• `auto` — apply immediately |
| `llm.provider`   | `str`    | Specifies which LLM provider to use:<br>• `openai`, `anthropic` |
| `llm.<provider>.model` | `str` | The name of the LLM model to use (e.g. `gpt-4o`, `claude-3-opus`) |
| `llm.<provider>.api_key` | `str` or `null` | The API key to use for that provider. Can be omitted to use env var (e.g. `OPENAI_API_KEY`) |

> 💡 If `api_key` is not specified in the YAML file, Codius falls back to environment variables like `OPENAI_API_KEY`.

---

## Contribute

Codius is **under active development**.

If you're into:
- Domain-Driven Design
- Developer tooling
- LLM-based assistants
- Improving the modeling experience

...then jump in! Try it out, explore the codebase, and open an issue or PR.

---

## License

Licensed under [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html).
