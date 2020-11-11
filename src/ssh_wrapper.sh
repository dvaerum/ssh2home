#!/usr/bin/env bash
# ex: set tabstop=8 softtabstop=0 expandtab shiftwidth=4 smarttab:

set -ue

DEBUG="${BASH_SHELL_DEBUG:-}"

################### Args Parser ###################
POSITIONAL=()
ARGS=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -4|-6|-A|-a|-C|-f|-G|-g|-K|-k|-M|-N|-n|-q|-s|-T|-t|-V|-v|-X|-x|-Y|-y)
    if [ "${#POSITIONAL[@]}" == 0 ]; then
     	ARGS+=("$1")
    else
      	POSITIONAL+=("$1")
    fi
    shift # past argument
    ;;

    -B|-b|-c|-D|-E|-e|-F|-I|-i|-J|-L|-l|-m|-O|-o|-p|-Q|-R|-S|-W|-w)
    if [ "${#POSITIONAL[@]}" == 0 ]; then
      	ARGS+=("$1")
      	ARGS+=("$2")
      	shift # past argument
      	shift # past value
    else
      	POSITIONAL+=("$1")
      	shift # past argument
    fi
    ;;

    *)    # unknown option
    	POSITIONAL+=("$1") # save it in an array for later
    shift # past argument
    ;;
esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

if [ -n "${DEBUG}" ]; then
    >&2 echo "All Args: ${ARGS[@]}"
    >&2 echo "All Args (count): ${#ARGS[@]}"
    >&2 echo "Host & CMD (followed by args): ${POSITIONAL[@]}"
    >&2 echo "Host & CMD (count): ${#POSITIONAL[@]}"
fi
###################################################

source "/tmp/$USER/env"

PORT="${PORT:-7654}"
SSH_BIN_PATH="${SSH_BIN_PATH:-ssh}"
SHELL="${SHELL}"

### Get Hostname
if [ "${#POSITIONAL[@]}" -ne 0 ]; then
    HOSTNAME="${POSITIONAL[0]}"
else
    "$SSH_BIN_PATH"
fi

if [ -n "${DEBUG}" ]; then
    >&2 echo "Host: ${POSITIONAL[0]}"
    >&2 echo "CMD (followed by args): ${POSITIONAL[@]:1}"
fi

source <(cat "/tmp/$USER/check_shells.sh" | "$SSH_BIN_PATH" "${HOSTNAME}" "/bin/sh")

if [ -n "${DEBUG}" ]; then
    >&2 echo "SHELL:    '${SHELL}'"
    >&2 echo "ISO_8601: '${ISO_8601:-}'"
fi

if [ "$(expr "$(date --date=${ISO_8601:-1970-01-01} '+%s')" + ${UPDATE_INTERVAL:-0})" -lt "$(date '+%s')" ]; then
    curl --location \
         --silent \
         --show-error \
         "http://localhost:${PORT}/startup-script/${HOSTNAME}/${ID:-}" | \
    "$SSH_BIN_PATH" "${HOSTNAME}" "/bin/sh"
fi

if [ "${#POSITIONAL[@]}" -eq 1 ]; then
    exec "$SSH_BIN_PATH" -t "${HOSTNAME}" "${SHELL}"
else
    exec "$SSH_BIN_PATH" ${ARGS[@]} "${HOSTNAME}" "${POSITIONAL[@]:1}"
fi


