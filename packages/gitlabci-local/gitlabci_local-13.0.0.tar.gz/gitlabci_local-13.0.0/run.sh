#!/bin/sh

# Job selection
if [ -z "${*}" ] && [ -z "${JOB}" ]; then
  echo ''
  printf " \033[1;33m> Run job \033[1;36m[JOB] \033[1;33m: \033[0m"
  read -r JOB
fi

# Iterate through jobs
for job in ${@:-${JOB}}; do

  # Header
  echo ''
  printf " \033[1;32m===[ \033[1;33mrun: ${job:?} \033[1;36m(local, native) \033[1;32m]===\033[0m\n"
  echo ''

  # Execute job scripts
  sed -n "
        /^${job}.*:$/,/^$/{
          /^  script:$/{
            :s
            n
            /^    - /{
              s/^ *- //p
              bs
            }
          }
        }
      " ./.gitlab-ci.yml \
    | while [ "${?}" -eq 0 ] && read -r line; do
      if ! type sudo >/dev/null 2>&1 || [ "${OSTYPE}" = 'msys' ]; then
        line=$(echo "${line}" | sed 's/sudo //g')
      fi
      if ! type python3 >/dev/null 2>&1 || [ "${OSTYPE}" = 'msys' ]; then
        line=$(echo "${line}" | sed 's/python3 /python /g')
      fi
      if ! type python >/dev/null 2>&1 && type wine >/dev/null 2>&1; then
        line=$(echo "${line}" | sed 's/python /wine python /g')
      fi
      echo "+ ${line}"
      sh -c "${line}"
    done
  result=${?}

  # Footer
  echo ''
  if [ "${result}" -eq 0 ]; then
    printf " \033[1;33m> ${job}: \033[1;32mSuccess\033[0m\n"
  else
    printf " \033[1;33m> ${job}: \033[1;31mFailure\033[0m\n"
  fi
  echo ''

done # Iterate through jobs
