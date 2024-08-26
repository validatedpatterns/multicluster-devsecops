# Running tests

## Prerequisites

* Openshift clusters with multicluster-devsecops pattern installed
  * prod and devel clusters are managed via rhacm
* kubeconfig files for Openshift clusters
* oc client installed at ~/oc_client/oc

## Steps

* create python3 venv, clone multicluster-devsecops repository
* export KUBECONFIG=\<path to hub kubeconfig file>
* export KUBECONFIG_PROD=\<path to prod kubeconfig file>
* export KUBECONFIG_DEVEL=\<path to devel kubeconfig file>
* export INFRA_PROVIDER=\<infra platform description>
* (optional) export WORKSPACE=\<dir to save test results to> (defaults to /tmp)
* cd multicluster-devsecops/tests/interop
* pip install -r requirements.txt
* ./run_tests.sh

## Results

* results .xml files will be placed at $WORKSPACE
* test logs will be placed at $WORKSPACE/.results/test_execution_logs/
* CI badge file will be placed at $WORKSPACE
