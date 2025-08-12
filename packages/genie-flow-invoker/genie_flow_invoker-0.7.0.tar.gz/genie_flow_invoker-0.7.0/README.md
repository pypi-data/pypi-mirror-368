# Genie Flow Invoker framework
[![PyPI version](https://badge.fury.io/py/genie-flow-invoker.svg?icon=si%3Apython)](https://badge.fury.io/py/genie-flow-invoker)
![PyPI - Downloads](https://img.shields.io/pypi/dm/genie-flow-invoker)

This package contains the base classes for Genie Flow Invokers.

## What are Invokers
An Invoker is a class that gets used when an external service needs to be called. That
external service may be a known GenAI API, or a Vector Database or anything else. Calling
that external service should follow the pattern of input -> process -> output.