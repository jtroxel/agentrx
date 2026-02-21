---
title: "AgenTrx Templates"
description: "Template files for AgentRx projects, including documentation templates, prompt templates, and example artifacts."
arx: template
---

# AgenTrx Templates
This folder contains template files for AgentRx projects, including documentation templates, prompt templates, and example artifacts.

This (top-level) directory corresponds to the target project directory (defined in the ARX_TARGET_PROJ environment variable) from initialization. It contains templates for project code and documentation that are overlayed onto the target project during initialization or other agentrx commands.

Typically, this directory is backed by a separate repo that is linked into the ARX_PROJECT_ROOT during initialization.

