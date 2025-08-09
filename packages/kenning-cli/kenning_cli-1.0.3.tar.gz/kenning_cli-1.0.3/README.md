# Kenning CLI


## Quick Setup (Copy & Paste)

```bash
# 1. Install Python 3 and pip (if not already installed)
sudo dnf install -y python3 python3-pip

# 2. Install kenning-cli from PyPI
# Kenning CLI

Kenning CLI is an AI-powered contextual risk analysis tool for AWS. It finds and explains where cloud cost and security risks amplify each other—helping you prioritize what truly matters.

---

## 🚀 Quick Start (Copy & Paste)

**Choose one method below. All major Linux distros, macOS, and Windows are supported.**

### Option 1: PyPI (Recommended)
```bash
# Install Python 3 and pip (choose your OS):
# Ubuntu/Debian: sudo apt update && sudo apt install -y python3 python3-pip
# Fedora/RHEL/Alma: sudo dnf install -y python3 python3-pip
# Mac: brew install python3
# Windows: choco install python

pip3 install kenning-cli awscli
aws configure

# (Optional) For AI explanations:
./scripts/setup-aws.sh
ollama serve &
ollama pull phi3

kenning --help
```

### Option 2: Docker (No Python Needed)
```bash
# Install Docker & Docker Compose (see https://docs.docker.com/get-docker/)
git clone https://github.com/kenningproject/kenning-cli.git
cd kenning-cli/docker
docker compose up --build
# To run CLI commands:
docker compose run kenning scan
```

### Option 3: GitHub (For Developers)
```bash
git clone https://github.com/kenningproject/kenning-cli.git
cd kenning-cli
pip3 install -e .
aws configure
```

---

## What is Kenning CLI?

Kenning CLI is a command-line tool that:
- Scans your AWS account for cost and security risks
- Correlates findings to reveal high-impact "compound risks"
- Uses AI (OpenAI, Ollama, or local LLMs) to explain risks in plain English
- Generates actionable Markdown reports for teams and compliance

**Why?** Because real-world cloud risks are never just about cost or security—they’re about context.

---

## Features

- 🔍 **Comprehensive Audits:** EC2, S3, and more
- 🧠 **Contextual Correlation:** Finds where cost and security risks overlap
- 🤖 **AI Explanations:** Human-readable, actionable insights
- 📄 **Markdown Reports:** Shareable, compliance-ready output
- 🛠️ **CLI-First:** Fits DevOps, SRE, and CI/CD workflows

---

## Usage

```bash
# Scan your AWS account
kenning scan

# Explain findings with AI
kenning explain

# Generate a Markdown report
kenning report
```

See `kenning --help` for all options.

---

## Requirements

- Python 3.9+
- AWS account with read-only EC2/S3 permissions
- (Optional) Ollama or OpenAI API for AI explanations

---

## Contributing

Pull requests are welcome! See `CONTRIBUTING.md` for guidelines.

---

## License

Apache 2.0. See `LICENSE` for details.
```
Our interactive setup assistant will:
- Check if AWS CLI is installed
- Guide you through credential configuration
- Validate your permissions
- Run a test scan to ensure everything works

**Option B: Manual Configuration**
```bash
aws configure
```
You'll need:
- AWS Access Key ID (from IAM user)
- AWS Secret Access Key (from IAM user)
- Default region (e.g., us-east-1)

**Option C: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

**Option D: Check Current Configuration**
```bash
kenning check-config
```
This command validates your AWS setup and permissions.

📚 **For detailed AWS setup instructions, see [AWS_SETUP.md](AWS_SETUP.md)**

**Required AWS Permissions:**
Kenning CLI needs read-only access to EC2 and S3 services. You can either:
- Attach the `ReadOnlyAccess` managed policy (easiest)
- Create a custom policy with specific permissions (most secure - see AWS_SETUP.md)

### 3. Run Your First Scan

```bash
# Basic scan
kenning scan

# Scan specific region with verbose output
kenning scan --region us-west-2 --verbose

# Use specific AWS profile
kenning scan --profile production
```

---


## 🧩 Components & Responsibilities

### 1️⃣ Audit Engine (Core)

* Collect AWS metadata for **EC2 instances and S3 buckets**.
* Identify **cost inefficiencies**:

  * Idle/underutilized EC2 instances.
  * Public S3 buckets (increased data egress potential).
* Identify **security risks**:

  * Open security groups (0.0.0.0/0).
  * Public S3 buckets (misconfiguration).
* Output structured `RiskItem` objects containing:

  * Resource Type, ID, Region
  * Risk Type (Cost, Security, Both)
  * Metadata for correlation.

### 2️⃣ Correlator

* Identify **compound risks** (e.g., idle EC2 with open SSH).
* Assign **severity scores**:

  * Low / Medium / High
  * Based on cost impact, security risk, and exposure.
* Maintain a simple rule engine for extensibility.

### 3️⃣ AI Explainer Agent

* Uses **OpenAI GPT API / Ollama**.
* Generates **plain-English explanations**:

  * Risk cause.
  * Why it matters.
  * One actionable remediation step.
* Supports structured output in Markdown.

### 4️⃣ Report Generator

* Generates **Markdown reports**:

  * Table of identified risks with metadata.
  * GPT-based explanations.
  * Severity overview.
* Allows easy sharing with teams or for documentation pipelines.


### 6️⃣ Testing & Validation

* Includes **comprehensive pytest-based test suite** with:
  * **8 core tests** for audit engine correctness and correlator logic
  * **AI data packaging** demos for OpenAI, Claude, local LLMs, and custom ML models
  * **Mocked AWS services** using moto for reliable, fast testing
  * **Future scalability** examples demonstrating enterprise-grade compatibility

#### Quick Test Commands
```bash
# Easy way - run all tests
./run_tests.sh

# Or run specific categories
./run_tests.sh core      # Core logic tests (8 tests)
./run_tests.sh ai        # AI agent data formatting demos
./run_tests.sh debug     # Debug data collection flow
./run_tests.sh future    # Future scalability examples
```

* **Cross-platform compatibility**: Tests work on Linux, macOS, and Windows
* **No hardcoded paths**: Uses dynamic path resolution for open source distribution
* **Complete documentation**: See [`tests/README.md`](tests/README.md) for detailed guidance

* Ensures reliability during CLI usage and validates AI integration pipeline.

---

## ⚙️ Tech Stack

* **Language**: Python 3.11+
* **CLI**: click
* **AWS SDK**: boto3
* **LLM Integration**: OpenAI SDK (GPT-4, GPT-3.5) / Ollama
* **Reporting**: Markdown generation
* **Testing**: pytest
* **Formatting/Linting**: black, flake8
* **Version Control**: Git + GitHub
* **CI/CD**: GitHub Actions (optional, for test automation)

---

## 💡 Novelty & Research Contributions

* ✅ **Fills a research gap** by combining **cost optimization** and **security auditing** in AWS within a single, context-aware tool.
* ✅ Uses **LLMs to generate human-readable explanations** for technical audit results, improving clarity for DevOps engineers.
* ✅ CLI-first design for **practical DevOps/SRE workflows**.
* ✅ Modular and extensible architecture for further research and productization.
* ✅ Evaluated in live AWS environments, providing measurable practical value.

---

## 📦 Final Deliverables

* ✅ **Working CLI tool** with core commands (`scan`, `explain`, `report`).
* ✅ **Structured JSON outputs** from audit for further processing.
* ✅ **Markdown reports** summarizing audit findings with GPT explanations.
* ✅ **Unit-tested core modules** (audit, correlator, GPT integration).
* ✅ **Clean, well-documented GitHub repository** with clear structure.
* ✅ **Demo video** showcasing the CLI tool in action.

---


## 🛠️ Development Workflow

* ✅ Use **Git and GitHub** for version control.
* ✅ Use **VS Code with Python, Pylance, and Copilot** extensions.
* ✅ Use **GitHub Actions** for optional test automation.
* ✅ Format regularly using `black .` and lint using `flake8 .`.
* ✅ Test frequently with `pytest`.
* ✅ Commit using a **consistent structured format**:

```
feat(audit): add EC2 idle instance detection
```

✅ Use branches for features:

```
git checkout -b feat/cli-scan
```

✅ Push regularly and use Pull Requests for clean history.

---

## 🛡️ Why Kenning CLI Matters

* **Cloud cost optimization and security are deeply interconnected** in real-world DevOps and SRE environments.
* Existing tools often focus on **either cost or security in isolation**, lacking context-aware compound risk analysis.
* LLMs can transform raw audit data into **actionable insights** for engineers, improving decision-making and response times.

---


