#!/usr/bin/env bash

# in a directory full of repos, this will cd into each and
# scrape every branch from origin
#
# you'll need to clone every single repo into a directory first
#
# this is used in cs4118 to pull down every commit from everyone's repo
# (there's probably a better way to do this using git clone --mirror but this
# was the easiest)

set -e

dir=${1:-.}

for repo in ${dir}/*; do
	[[ -d "$repo" ]] || continue
	pushd $repo
	for b in `git branch -r | grep -v -- '->'`; do
		set +e # may fail, in particular on master
		git branch --track ${b##origin/} $b
		set -e
	done
	git fetch --all
	git pull --all
	popd
done
