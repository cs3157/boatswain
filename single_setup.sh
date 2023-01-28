#!/bin/bash
ROOT_DIR="~/team_tmp"
HANDLES_TXT="$ROOT_DIR/handles.txt"
TEAMS_CSV="$ROOT_DIR/teams.csv"
HANDLES_CSV="$ROOT_DIR/handles.csv"

ORG_TEAM="students-2023-1"

if [ $# -ne 2 ]; then
    echo "Usage: $0 <hw> <xx-team_name>"
    exit 1
fi

rm -rf "$ROOT_DIR"
mkdir -p "$ROOT_DIR"

hw=$1
team_name=$2

if [[ ! "$team_name" =~ ^[0-9]+ ]]; then
    echo "Team name must start with a number"
    exit 1
fi

echo "Enter github usernames line by line, blank line when done: "
while read user; do
    if [ -z "$user" ]; then
        break
    fi
    echo "$user" >> "$HANDLES_TXT"
done

echo -n "$team_name," >> $TEAMS_CSV
awk '{print $1}' "$HANDLES_TXT" | tr '\n' ',' >> "$TEAMS_CSV"

# create csv file with format team_name,x,github_username
awk -v team_name="$team_name" '{print team_name ",x," $1}' "$HANDLES_TXT" > "$HANDLES_CSV"

cat "$HANDLES_CSV"
source venv/bin/activate
echo "test"

./add_team_members.py -v cs4118-hw "$ORG_TEAM" "$HANDLES_TXT" member
read -p "Press enter to continue"

git clone git@github.com:cs4118-hw/$hw.git "$ROOT_DIR/$hw"
read -p "Press enter to continue"

./mk_group_repos.py --verbose --create \
        cs4118-hw "$hw" "$TEAMS_CSV" none
read -p "Press enter to continue"

git remote add "$team_name" git@github.com:cs4118-hw/"$hw"-"$team_name".git

git remote -v

read -p "You should see two cs4118 remotes. Press enter to continue"

git push "$team_name" master
read -p "Press enter to continue"

./mk_group_repos.py --verbose cs4118-hw "$hw" "$TEAMS_CSV" push

rm -rf "$ROOT_DIR"