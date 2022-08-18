# Start Here

If you've followed a link to this repo, but are not really sure what it contains
or how to use it, head over to [Multicloud Devsecops](https://hybrid-cloud-patterns.io/devsecops/)
for additional context and installation instructions

## Cluster requirements

This pattern depends on having three clusters.

* Central Hub - where all the infrastructure components run.
  * Advanced cluster management
  * Advanced cluster security
  * Image registry and supporting stoage
  * Secrets management
* Developement - where CI/CD pipelines and testing run
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
