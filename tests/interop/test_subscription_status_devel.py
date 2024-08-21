import logging

import pytest
from validatedpatterns_tests.interop import subscription

from . import __loggername__

logger = logging.getLogger(__loggername__)


@pytest.mark.subscription_status_devel
def test_subscription_status_devel(openshift_dyn_client):
    # These are the operator subscriptions and their associated namespaces
    expected_subs = {
        "openshift-gitops-operator": ["openshift-operators"],
        "openshift-pipelines-operator-rh": ["openshift-operators"],
        "quay-bridge-operator": ["openshift-operators"],
        "rhacs-operator": ["openshift-operators"],
    }

    (
        operator_versions,
        missing_subs,
        unhealthy_subs,
        missing_installplans,
        upgrades_pending,
    ) = subscription.subscription_status(openshift_dyn_client, expected_subs)

    if missing_subs:
        logger.error(f"FAIL: The following subscriptions are missing: {missing_subs}")
    if unhealthy_subs:
        logger.error(
            f"FAIL: The following subscriptions are unhealthy: {unhealthy_subs}"
        )
    if missing_installplans:
        logger.error(
            f"FAIL: The install plan for the following subscriptions is missing: {missing_installplans}"
        )
    if upgrades_pending:
        logger.error(
            f"FAIL: The following subscriptions are in UpgradePending state: {upgrades_pending}"
        )

    cluster_version = subscription.openshift_version(openshift_dyn_client)
    logger.info(f"Openshift version:\n{cluster_version.instance.status.history}")

    for line in operator_versions:
        logger.info(line)

    if missing_subs or unhealthy_subs or missing_installplans or upgrades_pending:
        err_msg = "Subscription status check failed"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Subscription status check passed")
