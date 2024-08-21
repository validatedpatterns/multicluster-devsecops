import logging
import os

import pytest
import yaml
from ocp_resources.storage_class import StorageClass
from validatedpatterns_tests.interop import application, components
from validatedpatterns_tests.interop.crd import ManagedCluster

from . import __loggername__

logger = logging.getLogger(__loggername__)

oc = os.environ["HOME"] + "/oc_client/oc"

"""
Validate following multicluster-devsecops components pods and endpoints
on hub site (central server):

1) ACM (Advanced Cluster Manager) and self-registration
2) argocd
3) openshift operators
4) applications health (Applications deployed through argocd)
"""


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
    namespace = "openshift-gitops"
    sub_string = "argocd-dex-server-token"
    try:
        hub_api_url = application.get_site_api_url(kube_config)
        hub_api_response = application.get_site_api_response(
            openshift_dyn_client, hub_api_url, namespace, sub_string
        )
    except AssertionError as e:
        logger.error(f"FAIL: {e}")
        assert False, e

    if hub_api_response.status_code != 200:
        err_msg = "Hub site is not reachable. Please check the deployment."
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Hub site is reachable")


@pytest.mark.check_pod_status_hub
def test_check_pod_status(openshift_dyn_client):
    logger.info("Checking pod status")

    err_msg = []
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

    missing_projects = components.check_project_absense(openshift_dyn_client, projects)
    missing_pods = []
    failed_pods = []

    for project in projects:
        logger.info(f"Checking pods in namespace '{project}'")
        missing_pods += components.check_pod_absence(openshift_dyn_client, project)
        failed_pods += components.check_pod_status(openshift_dyn_client, projects)

    if missing_projects:
        err_msg.append(f"The following namespaces are missing: {missing_projects}")

    if missing_pods:
        err_msg.append(
            f"The following namespaces have no pods deployed: {missing_pods}"
        )

    if failed_pods:
        err_msg.append(f"The following pods are failed: {failed_pods}")

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


@pytest.mark.validate_acm_self_registration_managed_clusters
def test_validate_acm_self_registration_managed_clusters(openshift_dyn_client):
    logger.info("Check ACM self registration for edge sites")
    unjoined_sites = []

    for kubefile in (os.getenv("KUBECONFIG_DEVEL"), os.getenv("KUBECONFIG_PROD")):
        kubefile_exp = os.path.expandvars(kubefile)

        with open(kubefile_exp) as stream:
            try:
                out = yaml.safe_load(stream)
                site_name = out["clusters"][0]["name"]
            except yaml.YAMLError:
                err_msg = "Failed to load kubeconfig file"
                logger.error(f"FAIL: {err_msg}")
                assert False, err_msg

        logger.info(f"Site name : {site_name}")

        clusters = ManagedCluster.get(dyn_client=openshift_dyn_client, name=site_name)
        cluster = next(clusters)
        (
            is_managed_cluster_joined,
            managed_cluster_status,
        ) = cluster.self_registered

        logger.info(f"Cluster Managed : {is_managed_cluster_joined}")
        logger.info(f"Managed Cluster Status : {managed_cluster_status}")

        if not is_managed_cluster_joined:
            logger.info(f"The site {site_name} is not self registered")
            unjoined_sites.append(site_name)

    if unjoined_sites:
        err_msg = "Some sites are not self registered"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: All sites are self registered")


@pytest.mark.validate_argocd_reachable_hub_site
def test_validate_argocd_reachable_hub_site(openshift_dyn_client):
    namespace = "openshift-gitops"
    name = "openshift-gitops-server"
    sub_string = "argocd-dex-server-token"
    logger.info("Check if argocd route/url on hub site is reachable")
    try:
        argocd_route_url = application.get_argocd_route_url(
            openshift_dyn_client, namespace, name
        )
        argocd_route_response = application.get_site_api_response(
            openshift_dyn_client, argocd_route_url, namespace, sub_string
        )
    except StopIteration:
        err_msg = "Argocd url/route is missing in open-cluster-management namespace"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    except AssertionError:
        err_msg = "Bearer token is missing for argocd-dex-server"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg

    logger.info(f"Argocd route response : {argocd_route_response}")

    if argocd_route_response.status_code != 200:
        err_msg = "Argocd is not reachable. Please check the deployment"
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Argocd is reachable")


@pytest.mark.validate_argocd_applications_health_hub_site
def test_validate_argocd_applications_health_hub_site(openshift_dyn_client):
    unhealthy_apps = []
    logger.info("Get all applications deployed by argocd on hub site")
    projects = ["openshift-gitops", "multicluster-devsecops-hub"]
    for project in projects:
        unhealthy_apps += application.get_argocd_application_status(
            openshift_dyn_client, project
        )
    if unhealthy_apps:
        err_msg = "Some or all applications deployed on hub site are unhealthy"
        logger.error(f"FAIL: {err_msg}:\n{unhealthy_apps}")
        assert False, err_msg
    else:
        logger.info("PASS: All applications deployed on hub site are healthy.")
