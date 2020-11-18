#! /bin/bash

source common.sh

# ==============================================================================
echo -e "\nCheck for unclaimed qualifiers."
kgtk ${KGTK_FLAGS} \
     ifnotexists $VERBOSE --use-mgzip=$USE_MGZIP --presorted \
     --input-file ${DATADIR}/qualifiers.${SORTED_KGTK} \
     --filter-file ${DATADIR}/claims.${SORTED_KGTK} \
     --output-file ${DATADIR}/qualifiers.unclaimed.${SORTED_KGTK} \
     --input-keys node1 \
     --filter-keys id
