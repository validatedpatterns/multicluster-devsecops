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
Validate following multicluster-devsecops components pods and
endpoints on edge site (line server):

1) argocd
2) ACM agents
3) applications health (Applications deployed through argocd)
"""


@pytest.mark.test_validate_devel_site_components
def test_validate_devel_site_components():
    logger.info("Checking Openshift version on devel site")
    version_out = components.dump_openshift_version()
    logger.info(f"Openshift version:\n{version_out}")


@pytest.mark.validate_devel_site_reachable
def test_validate_devel_site_reachable(kube_config, openshift_dyn_client):
    logger.info("Check if devel site API end point is reachable")
    namespace = "openshift-gitops"
    sub_string = "argocd-dex-server-token"
    try:
        devel_api_url = application.get_site_api_url(kube_config)
        devel_api_response = application.get_site_api_response(
            openshift_dyn_client, devel_api_url, namespace, sub_string
        )
    except AssertionError as e:
        logger.error(f"FAIL: {e}")
        assert False, e

    if devel_api_response.status_code != 200:
        err_msg = "Devel site is not reachable. Please check the deployment."
        logger.error(f"FAIL: {err_msg}")
        assert False, err_msg
    else:
        logger.info("PASS: Devel site is reachable")


@pytest.mark.check_pod_status_devel
def test_check_pod_status(openshift_dyn_client):
    logger.info("Checking pod status")

    err_msg = []
    projects = [
        "openshift-operators",
        "openshift-gitops",
        "multicluster-devsecops-development",
        "open-cluster-management-agent",
        "open-cluster-management-agent-addon",
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


@pytest.mark.validate_argocd_reachable_devel_site
def test_validate_argocd_reachable_devel_site(openshift_dyn_client):
    namespace = "openshift-gitops"
    name = "openshift-gitops-server"
    sub_string = "argocd-dex-server-token"
    logger.info("Check if argocd route/url on devel site is reachable")
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


@pytest.mark.validate_argocd_applications_health_devel_site
def test_validate_argocd_applications_health_devel_site(openshift_dyn_client):
    unhealthy_apps = []
    logger.info("Get all applications deployed by argocd on devel site")
    projects = ["openshift-gitops"]
    for project in projects:
        unhealthy_apps += application.get_argocd_application_status(
            openshift_dyn_client, project
        )
    if unhealthy_apps:
        err_msg = "Some or all applications deployed on devel site are unhealthy"
        logger.error(f"FAIL: {err_msg}:\n{unhealthy_apps}")
        assert False, err_msg
    else:
        logger.info("PASS: All applications deployed on devel site are healthy.")
