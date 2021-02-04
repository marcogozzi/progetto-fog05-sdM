#!/bin/bash
# CTD='/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots'
# CTD_overlayFS='/run/containerd/io.containerd.runtime.v2.task/fos/'

# /home/marco/fos/fs/_uuid_old		is created by demon ctr_fdu_association, 	it contains _fs_num_old
# /home/marco/fos/new/_uuid_old	  	is created by migration script, 		it contains _uuid_new
# /home/marco/fos/dest/_uuid_old 		is created by migration script,		it contains the destination needed by the remote copy mechanism

inotifywait -m /home/marco/fos/tar -e create -e moved_to |
    while read _dir _action _uuid_new; do
		#scp "$FOLDER" marco@192.168.31.232:/home/marco/fos/new/

		# retrieve destination
		_dest=$(cat '/home/marco/fos/dest/'$_uuid_new)
		
		# copy fs tar file to correct destination
		scp '/home/marco/fos/tar/'"$_uuid_new" "$_dest"':/home/marco/fos/newfs/'
		
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
