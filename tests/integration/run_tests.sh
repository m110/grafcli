#!/usr/bin/env bats
load helpers

readonly DASHBOARD_SLUG=collectd-server-metrics
readonly NEW_DASHBOARD_SLUG=collectd-server-metrics-two

@test "Ensure there are no dashboards" {
    assert_no_dashboards
}

@test "Import dashboard" {
    grafcli import /app/tests/integration/example-dashboard.json /remote/localhost
    assert_only_dashboard "$DASHBOARD_SLUG"
}

@test "Import dashboard with the same slug name" {
    grafcli import /app/tests/integration/example-dashboard.json /remote/localhost
    assert_only_dashboard "$DASHBOARD_SLUG"
}

@test "Remove dashboards" {
    grafcli rm "/remote/localhost/$DASHBOARD_SLUG"
    assert_no_dashboards
}
