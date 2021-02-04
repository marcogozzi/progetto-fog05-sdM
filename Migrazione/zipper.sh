#!/bin/bash
# CTD='/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots'
# CTD_overlayFS='/run/containerd/io.containerd.runtime.v2.task/fos/'

# /home/marco/fos/fs/_uuid_old		is created by demon ctr_fdu_association, 	it contains _fs_num_old
# /home/marco/fos/new/_uuid_old	  	is created by migration script, 		it contains _uuid_new
# /home/marco/fos/dest/_uuid_old 		is created by migration script,		it contains the destination needed by the remote copy mechanism

inotifywait -m /home/marco/fos/new -e create -e moved_to |
    while read _dir _action _uuid_old; do
        	#rm -f "$FOLDER"
		#sudo tar -cpzf "$FOLDER" "$CTD""$FOLDER"'/fs'

		# retrieve uuid_new from uuid_old - uuid_new association
		_uuid_new=$(cat '/home/marco/fos/new/'$_uuid_old)
		
		#create fs tar file
		sudo tar -cpzf '/home/marco/fos/tar/'"$_uuid_new" -C '/run/containerd/io.containerd.runtime.v2.task/fos/'"$_uuid_old"'/rootfs' 'tmp'
		
		# delete uuid-fs ctd_fdu association
		#rm -f '/home/marco/fos/fs/'"$_uuid_old"
		# delete uuid_old - uuid_new association
		#rm -f '/home/marco/fos/new/'"$_uuid_old"
		# delete destination
		#rm -f '/home/marco/fos/new/'"$_dest"
		# delete tar file
		#rm -f '/home/marco/fos/new/'"$_uuid_new"
		
	done 
	
# sudo apt install inotify-tools	
#inotifywait -m /home/marco/fos/old -e create -e moved_to |
#while read dir action file; do
	#echo "The file '$file' appeared in directory '$dir' via '$action'"
