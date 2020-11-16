#!/usr/bin/env bash

# WAITING FOR UNLOCK FILES
if [[ -d /tmp/unlock-file ]]; then
  REQUIRED_UNLOCK_FILES=($REQUIRED_UNLOCK_FILES)
  echo "Waiting for unlock files (${REQUIRED_UNLOCK_FILES[@]})"
  all_files_exist=0
  while [[ $all_files_exist -eq 0 ]]; do
    all_files_exist=1
    for filename in "${REQUIRED_UNLOCK_FILES[@]}"; do
      unlock_file=/tmp/unlock-file/$filename
      if [[ ! -e $unlock_file ]]; then
        all_files_exist=0
      fi
    done
    sleep 1
  done
fi

# WAITING FOR REQUIRED SERVERS STARTUP

function is_server_up(){
  local server="$(sed 's/:/ /' <<< "$1")"
  local server=($server)
  local host="${server[0]}"
  local port="${server[1]}"
  local nmap_res="$(nmap -p $port $host)"
  local open="$(grep open <<< $nmap_res)"
  if [[ -n "$open" ]]; then
    return 0;
  else
    return 1;
  fi
}

if [[ -n "$REQUIRED_SERVERS" ]]; then
  REQUIRED_SERVERS=($REQUIRED_SERVERS)
  echo "Waiting for required servers startup: (${REQUIRED_SERVERS[@]})"
  while true; do
    INACTIVE_SERVERS=()
    for server in "${REQUIRED_SERVERS[@]}"; do
        is_server_up $server
        if [[ "$?" -eq 0 ]]; then
          echo "Server $server started"
        else
          INACTIVE_SERVERS+=("$server")
          echo "Server $server inactive"
        fi
    done
    if [[ "${#INACTIVE_SERVERS[@]}" -eq 0 ]]; then
      break
    else
      REQUIRED_SERVERS=(${INACTIVE_SERVERS[@]})
    fi
    sleep 5
  done
fi

# EXECUTING ORIGINAL ENTRYPOINT
original_entrypoint_script=$1
shift
$original_entrypoint_script $@
SCRIPT_RESULT="$?"
# CREATING UNLOCK FILE IF REQUIRED
if [[ -n "UNLOCK_FILENAME" ]]; then
  if [[ "$SCRIPT_RESULT" -eq "0" ]]; then
    UNLOCK_FILENAME=/tmp/unlock-file/$UNLOCK_FILENAME
    touch $UNLOCK_FILENAME
    echo "Unlock file $UNLOCK_FILENAME created"
  else
    echo "Script returned non zero code: $SCRIPT_RESULT, unlock file not created"
    exit 1
  fi
fi
