#!/bin/bash

set -xe

THIS_DIR=$(realpath $(dirname ${0}))
SAMPLES_DIR=${THIS_DIR}/samples
TMP_DIR=/tmp/deploy-tools-output

rm -rf "${SAMPLES_DIR}"
rm -rf "${TMP_DIR}"
mkdir -p "${TMP_DIR}"

deploy-tools sync --from-scratch ${TMP_DIR} ${THIS_DIR}/../src/deploy_tools/demo_configuration

# don't keep the sif or git files, also remove binaries
rm -rf $(find ${TMP_DIR} -name "*.sif")
rm -rf ${TMP_DIR}/.git*
rm ${TMP_DIR}/modules/edge-containers-cli/0.1/entrypoints/argocd

rm -rf ${SAMPLES_DIR}
mkdir -p ${SAMPLES_DIR}
cp -r ${TMP_DIR} ${SAMPLES_DIR}
