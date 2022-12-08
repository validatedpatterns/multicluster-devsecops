# Multicluster Devsecops

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Start Here

If you've followed a link to this repository, but are not really sure what it contains
or how to use it, head over to [Multicluster Devsecops](https://hybrid-cloud-patterns.io/devsecops/)
for additional context and installation instructions

## Cluster requirements

This pattern depends on having three clusters.

* Central Hub - where all the infrastructure components run.
  * Red Hat Advanced Cluster Management
  * Red Hat Advanced Cluster Security (Central)
  * Red Hat Quay Enterprise
  * Secrets management
* Development - where CI/CD pipelines and testing run
  * Red Hat OpenShift Pipelines
  * Red Hat OpenShift GitOps
  * Red Hat Advanced Cluster Security (Secured)
* Production - where the applications run

It can be modified to run everything in a single cluster. Components of `values-development.yaml` and `values-production.yaml` would need to be merged into `values-hub.yaml` where applicable. *Use caution*. In the future the pattern may be enhanced to combine into a single cluster.

## Products/projects used

* Red Hat OpenShift GitOps
* Red Hat Advanced Cluster Management
* Red Hat Advanced Cluster Security
* Red Hat Open Data Foundation
* Red Hat Quay
* Red Hat OpenShift Pipelines
* Hashicorp Vault (Community)
