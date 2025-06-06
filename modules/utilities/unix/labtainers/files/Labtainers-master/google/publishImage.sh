# Create a base labtainer image.
# First:
#    delete_vm.sh base24
#    base_create22.sh base24
#    stop_vm.sh base24
#
# Then use 
#    gcloud compute instances describe base-labtainervm | grep disks
# to find the disk name, it is a url.
#
# Then 
#    Cycle through image names.  Most recently used should be in the gcloud binding command.
#    gcloud compute images create labtainervm5 --source-disk=https://www.googleapis.com/compute/v1/projects/labtainers/zones/us-west1-a/disks/base-labtainervm
#
# Only then run this script
#
#
gcloud compute images add-iam-policy-binding labtainervm1 \
    --member='allAuthenticatedUsers' \
    --role='roles/compute.imageUser'
