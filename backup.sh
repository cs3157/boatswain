#!/bin/bash
# Back up student repos from Github using a base assignment repo
# Requires that base assignment repo contains the base commit in student repos

if [[ $# != 1 ]]; then
	echo "usage: backup.sh <manifest-file>"
	exit 1
fi

HWS=(hw3 hw4 hw5 hw6 hw7 hw8)
MANIFEST=$1
ORG=cs4118-hw

for hw in ${HWS[@]}; do
	grep "$hw" "$MANIFEST" > "$hw.txt"
	git clone "git@github.com:$ORG/$hw.git" "$hw"
	for repo in $(cat "$hw.txt"); do
		repo_name=${repo##*/}
		echo "$repo_name"
		if [[ -d "$repo_name" ]]; then
			continue
		fi
		git clone "$hw" "$repo_name" || continue
		cd "$repo_name" || continue
		git remote set-url origin "git@github.com:$repo"
		git pull origin
		cd ..
	done
	rm -f "$hw.txt"
done
