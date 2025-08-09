#!/usr/bin/env bash
cd "$(dirname "$0")"
llms . "*.txt"
uvx hatch clean
gitnextver .
uvx hatch build
uvx hatch publish
