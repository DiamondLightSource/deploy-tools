#!/bin/bash

set -xe

THIS_DIR=$(realpath $(dirname ${0}))
SAMPLES_DIR=${THIS_DIR}/samples
CONFIGS_DIR=${THIS_DIR}/configs
TMP_DIR=/tmp/deploy-tools-output

rm -rf "${SAMPLES_DIR}"
rm -rf "${TMP_DIR}"
mkdir -p "${TMP_DIR}"

# Copy the current state of the deployment area into the samples directory as the golden
# master for the named lifecycle stage. Files that should not be committed are dropped
# from the copy only (not from the live area): .sif images are large and not
# reproducible, and .git/.gitignore belong to the deployment area's own history rather
# than its deployed content. The live area keeps its git repository so that the
# subsequent (non --from-scratch) syncs can run against it.
save_sample () {
    local stage=${1}
    local stage_dir=${SAMPLES_DIR}/${stage}

    mkdir -p "${stage_dir}"
    cp -r "${TMP_DIR}" "${stage_dir}"

    local dest=${stage_dir}/$(basename ${TMP_DIR})
    find "${dest}" -name "*.sif" -delete
    rm -rf "${dest}"/.git*
}

# Capture the change summary that 'validate' prints for the upcoming sync. validate is
# read-only and previews the next sync, so it runs against the deployment area in its
# current (pre-sync) state. The 'set -x' trace goes to stderr, so only the summary is
# written to the file.
capture_validate () {
    local stage=${1}
    shift
    mkdir -p "${SAMPLES_DIR}/${stage}"
    deploy-tools validate "$@" "${TMP_DIR}" "${CONFIGS_DIR}/${stage}" \
        > "${SAMPLES_DIR}/${stage}/validate.txt"
}

# The lifecycle stages share a single deployment area and must run in order, as
# each stage builds on the previous deployment state. Only the first sync
# uses --from-scratch.

# Stage 1: deploy the initial configuration into an empty area.
capture_validate 01-initial --from-scratch
deploy-tools sync --from-scratch "${TMP_DIR}" "${CONFIGS_DIR}/01-initial"
save_sample 01-initial

# Stage 2: add a new module (example-module-extra/1.0) on an incremental sync.
capture_validate 02-added
deploy-tools sync "${TMP_DIR}" "${CONFIGS_DIR}/02-added"
save_sample 02-added

# Stage 3: update example-module-extra/1.0 in place (allowed via allow_updates).
capture_validate 03-updated
deploy-tools sync "${TMP_DIR}" "${CONFIGS_DIR}/03-updated"
save_sample 03-updated

# Stage 4: deprecate example-module-deps/0.2 and example-module-extra/1.0.
capture_validate 04-deprecated
deploy-tools sync "${TMP_DIR}" "${CONFIGS_DIR}/04-deprecated"
save_sample 04-deprecated

# Stage 5: restore (un-deprecate) example-module-extra/1.0.
capture_validate 05-restored
deploy-tools sync "${TMP_DIR}" "${CONFIGS_DIR}/05-restored"
save_sample 05-restored

# Stage 6: remove the now-deprecated example-module-deps/0.2 entirely.
capture_validate 06-removed
deploy-tools sync "${TMP_DIR}" "${CONFIGS_DIR}/06-removed"
save_sample 06-removed
