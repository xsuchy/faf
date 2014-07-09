#!/bin/bash

if [[ "$1" == "org.fedoraproject.prod.buildsys.repo.done" && "$2" == "rawhide" && "$3" == "primary" ]];then
    # update metadata for each koji regen repo
    faf reposync $therepo
fi
