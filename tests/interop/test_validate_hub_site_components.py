import logging
import os

import pytest
from ocp_resources.storage_class import StorageClass
from validatedpatterns_tests.interop import application, components

from . import __loggername__

logger = logging.getLogger(__loggername__)

oc = os.environ["HOME"] + "/oc_client/oc"


@pytest.mark.test_validate_hub_site_components
def test_validate_hub_site_components(openshift_dyn_client):
    logger.info("Checking Openshift version on hub site")
    version_out = components.dump_openshift_version()
    logger.info(f"Openshift version:\n{version_out}")

    logger.info("Dump PVC and storageclass info")
    pvcs_out = components.dump_pvc()
    logger.info(f"PVCs:\n{pvcs_out}")

    for sc in StorageClass.get(dyn_client=openshift_dyn_client):
        logger.info(sc.instance)


@pytest.mark.validate_hub_site_reachable
def test_validate_hub_site_reachable(kube_config, openshift_dyn_client):
    logger.info("Check if hub site API end point is reachable")
    err_msg = components.validate_site_reachable(kube_config, openshift_dyn_client)
    if err_msg:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Hub site is reachable")


@pytest.mark.check_pod_status_hub
def test_check_pod_status(openshift_dyn_client):
    logger.info("Checking pod status")
    projects = [
        "openshift-operators",
        "open-cluster-management",
        "open-cluster-management-hub",
        "openshift-gitops",
        "multicluster-engine",
        "multicluster-devsecops-hub",
        "open-cluster-management-agent",
        "open-cluster-management-agent-addon",
        "vault",
    ]
    err_msg = components.check_pod_status(openshift_dyn_client, projects)
    if err_msg:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Pod status check succeeded.")


# No longer needed for ACM 2.7
#
# @pytest.mark.validate_acm_route_reachable
# def test_validate_acm_route_reachable(openshift_dyn_client):
#     namespace = "open-cluster-management"

#     logger.info("Check if ACM route is reachable")
#     try:
#         for route in Route.get(
#             dyn_client=openshift_dyn_client,
#             namespace=namespace,
#             name="multicloud-console",
#         ):
#             acm_route_url = route.instance.spec.host
#     except StopIteration:
#         err_msg = (
#             "ACM url/route is missing in open-cluster-management namespace"
#         )
#         logger.error(f"FAIL: {err_msg}")
#         assert False, err_msg

#     final_acm_url = f"{'http://'}{acm_route_url}"
#     logger.info(f"ACM route/url : {final_acm_url}")

#     bearer_token = get_long_live_bearer_token(
#         dyn_client=openshift_dyn_client,
#         namespace=namespace,
#         sub_string="multiclusterhub-operator-token",
#     )
#     if not bearer_token:
#         err_msg = (
#             "Bearer token is missing for ACM in open-cluster-management"
#             " namespace"
#         )
#         logger.error(f"FAIL: {err_msg}")
#         assert False, err_msg
#     else:
#         logger.debug(f"ACM bearer token : {bearer_token}")

#     acm_route_response = get_site_response(
#         site_url=final_acm_url, bearer_token=bearer_token
#     )

#     logger.info(f"ACM route response : {acm_route_response}")

#     if acm_route_response.status_code != 200:
#         err_msg = "ACM is not reachable. Please check the deployment"
#         logger.error(f"FAIL: {err_msg}")
#         assert False, err_msg
#     else:
#         logger.info("PASS: ACM is reachable.")


@pytest.mark.validate_argocd_reachable_hub_site
def test_validate_argocd_reachable_hub_site(openshift_dyn_client):
    logger.info("Check if argocd route/url on hub site is reachable")
    err_msg = components.validate_argocd_reachable(openshift_dyn_client)
    if err_msg:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Argocd is reachable")


@pytest.mark.validate_acm_self_registration_managed_clusters
def test_validate_acm_self_registration_managed_clusters(openshift_dyn_client):
    logger.info("Check ACM self registration for edge site")
    kubefiles = [os.getenv("KUBECONFIG_DEVEL"), os.getenv("KUBECONFIG_PROD")]
    err_msg = components.validate_acm_self_registration_managed_clusters(
        openshift_dyn_client, kubefiles
    )
    if err_msg:
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info(f"PASS: Edge site is self registered")


@pytest.mark.validate_argocd_applications_health_hub_site
def test_validate_argocd_applications_health_hub_site(openshift_dyn_client):
    logger.info("Get all applications deployed by argocd on hub site")
    projects = ["openshift-gitops", "multicluster-devsecops-hub"]
    unhealthy_apps = application.get_argocd_application_status(
        openshift_dyn_client, projects
    )
    if unhealthy_apps:
        err_msg = "Some or all applications deployed on hub site are unhealthy"
        logger.error(f"FAIL: {err_msg}:\n{unhealthy_apps}")
        assert False, err_msg
    else:
        logger.info("PASS: All applications deployed on hub site are healthy.")
