#!/bin/bash
# CTD='/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots'
# CTD_overlayFS='/run/containerd/io.containerd.runtime.v2.task/fos/'

CTDFS='/run/containerd/io.containerd.runtime.v2.task/fos/'
inotifywait -m /home/marco/fos/new -e create -e moved_to |
    while read _dir _action _uuid_old; do
        echo "The file '$_uuid_old' appeared in directory '$_dir' via '$_action'"
		{ IFS= read -r _uuid_new && IFS= read -r _dest; } < '/home/marco/fos/new/'"$_uuid_old"
		sudo rsync -e "ssh -i /home/marco/.ssh/root_key -o StrictHostKeyChecking=no" -aEAXz "$CTDFS""$_uuid_old"'/rootfs/' "$_dest":"$CTDFS""$_uuid_new"'/rootfs'
        unset -v _uuid_new _dest
	done 
	
# sudo apt install inotify-tools	
#inotifywait -m <path-to-monitor> -e create -e moved_to |
#while read dir action file; do
	#echo "The file '$file' appeared in directory '$dir' via '$action'"
