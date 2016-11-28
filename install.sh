#!/bin/bash

rand=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 16 | head -n 1)

PWD=$(pwd)

dialog_installed=$(dpkg-query -W --showformat='${Status}\n' dialog|grep "install ok installed")

if [[ "$dialog_installed" == "" ]]; then
    sudo apt-get install dialog
fi

function e {
    echo "$*"
    }

function menu_ {
    echo ''
    }

function ret {
    e
    read -p "Press [enter] to continue"
    e
    }


rr() {
    if [[ "$2" == "" ]]; then
      read -p "$1" retvalue
    else
      read -p "$1[$2]" retvalue
      if [[ "$retvalue" == "" ]]; then
	retvalue="$2"
      fi
    fi
    echo "$retvalue"
    }

function menu_exit {
    exit
    }

function conf {
    # call with a prompt string or use a default
    read -r -p "${1:-Are you sure? [Y/n]} " response
    if [[ "$response" == "" ]]; then
	true
    else 
    case $response in
        [yY][eE][sS]|[yY]) 
            true
            ;;
        *)
            false
            ;;
    esac
    fi
}

function get_main_domain {
    echo "from main_domain import MAIN_DOMAIN
print(MAIN_DOMAIN)" | python
}

function down {
    filetoget=$1
    if [[ "$2" == "" ]]; then
	filetoput=${1##*/}
    else
	filetoput=$2
	
    fi

    filetobak="$3"

    ntaxauser=$(rr 'Enter ntaxa username:')
    ntaxapass=$(rr "Enter ntaxa password:")
    if [[ "$3" != '' ]]; then
	echo "  mv $filetoget $filetobak"
    fi
    command="wget --user='$ntaxauser' --password='$ntaxapass' -O /tmp/"$rand"tmpfile http://x.m.ntaxa.com/profireader/$filetoget
if [[ \"\$?\" == \"0\" ]]; then"
    if [[ "$3" != '' ]]; then
	command="$command
    mv $filetoput $filetobak"
    fi
    command="$command
    mv /tmp/"$rand"tmpfile $filetoput
else
    echo 'wget failed!'
fi"
    conf_comm "$command" nosudo $4
    }

conf_comm() {
rd=`tput setaf 1`
    rst=`tput sgr0`

    if [[ "$2" == "sudo" ]]; then
	echo "${rd}"
        echo "Command we're going to execute (with sudo):"
    else
	echo "Command we're going to execute:"
    fi
    e
    echo "$1" | sed -e 's/^/    /g'
    echo "${rst}"
    if conf; then
	e
	echo "$1" > /tmp/"$rand"menu_command_run_confirmed.sh
	if [[ "$2" == "sudo" ]]; then
	    sudo bash /tmp/"$rand"menu_command_run_confirmed.sh
	else
	    bash /tmp/"$rand"menu_command_run_confirmed.sh
	fi
#        eval `echo "$1" | sed -e 's/"/\"/g' -e 's/^/sudo bash -c "/g' -e 's/$/";/g'`
	if [[ "$4" == "" ]]; then
	    ret
	fi
	if [[ "$3" != "" ]]; then
	    next="$3"
	fi
        true
    else
      false
    fi
}

function warn_about_rm {
    if [[ -e $1 ]]; then
    	    echo "warning: $1 exists and will be removed"
    fi
    }

function error_if_exists {
    if [[ -e $1 ]]; then
    	    echo "warning: $1 exists and will be removed"
    fi
    }

function get_profidb {
    echo `cat scrt/secret_data.py | grep 'DB_NAME\s*=' | sed -e 's/^\s*DB_NAME\s*=\s*['"'"'"]\([^'"'"'"]*\).*$/\1/g' `
    }

function runsql {
    conf_comm "systemctl restart postgresql.service
su postgres -c \"echo \\\"$1\\\" | psql\"" sudo "$2"
    }

function runsql_dump {
    profidb=$(get_profidb)
    filenam=$(rr "$1" "$2")
    conf_comm "systemctl restart postgresql.service
su postgres -c 'cat $filenam | psql $profidb'" sudo "$3"
    }

function menu_origin {
    destination=`git remote -v | grep 'fetch' | sed -e 's/^.*github.com:\([^\/]*\)\/.*$/\1/g'`
    conf_comm "git remote rename origin $destination
git remote add origin git@github.com:kakabomba/profireader.git" nosudo postgres_9_4
    }

function menu_deb {
    conf_comm "apt-get update
apt-get install $(cat deb.list)" sudo venv
    }

function menu_venv {
    destdir=$(rr 'destination dir for virtual directory' .venv)
    pythondir=$(rr 'python dir' /usr/local/opt/python-3.4.2)
    if [[ -e $destdir ]]; then
	echo "error: $destdir exists"
    else
	conf_comm "$pythondir/bin/pyvenv $destdir
cp ./activate_this.py $destdir/bin" nosudo modules
    fi
    }

function menu_modules {
    req=$(rr 'file with modules' requirements.txt)
    destdir=$(rr 'venv directory' .venv)
    conf_comm "
cd `pwd`
source $destdir/bin/activate
pip3 install -I -r $req" nosudo exit
    }


next='_'

#a="/bin/ls;
#/bin/ls"


	#eval $a

#exit
if [[ "$1" == "" ]]; then
  while :
  do
#next='exit'
#"haproxy_compile" "compile and install haproxy" \
#
    dialog --title "profireader" --nocancel --default-item $next --menu "Choose an option" 22 78 17 \
      "deb" "install deb packages" \
      "venv" "create virtual environment" \
      "modules" "install required python modules (via pip)" \
      "exit" "Exit" 2> /tmp/"$rand"selected_menu_
  reset
  datev="date +%y_%m_%d___%H_%M_%S"
  gitv='git rev-parse --short HEAD'
  menu_`cat /tmp/"$rand"selected_menu_`
  done
else
  menu_$1
fi

