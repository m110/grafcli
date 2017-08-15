#!/bin/bash
/wait-for-it.sh grafana:3000
make run_integration
