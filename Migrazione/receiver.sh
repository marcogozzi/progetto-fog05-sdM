#!/bin/bash
# CTD='/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots/' 
# CTD_overlayFS='/run/containerd/io.containerd.runtime.v2.task/fos/'
inotifywait -m /home/marco/fos/newfs -e create -e moved_to |
    while read _dir _action _uuid_new; do
    	#_fs_num_new=$(cat '/home/marco/fos/fs/'$_uuid_new)
    	# sudo tar -xf '/home/marco/fos/newfs/'"$_uuid_new" --directory="$CTD" --strip-components=1 --one-top-level="$_fs_num_new"
    	sudo tar -xf '/home/marco/fos/newfs/'"$_uuid_new" --directory='/run/containerd/io.containerd.runtime.v2.task/fos/'"$_uuid_new"'/rootfs/'  --skip-old-files
    	rm -f '/home/marco/fos/new/'"$_uuid_new"
    done
    
    	
#inotifywait -m /home/marco/fos/old -e create -e moved_to |
#while read dir action file; do
	#echo "The file '$file' appeared in directory '$dir' via '$action'"
