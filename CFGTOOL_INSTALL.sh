#! /bin/sh

install -D -g root -o root -p -t /etc/qworkerd configs/*.templ
install -D -g root -o root -p configs/qworkerd.cfgtool /etc/cfgtool/module.d/qworkerd
install -D -g root -o root -p configs/qworkerd.upstart.conf.templ /etc/init/qworkerd.conf.templ
