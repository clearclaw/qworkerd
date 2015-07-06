#! /bin/sh

install -d -g root -o root -m 0755 -p /etc/qworkerd/plugins
install -D -g root -o root -m 0644 -p -t /etc/qworkerd configs/*.templ
install -D -g root -o root -m 0644 -p -t /etc/qworkerd/plugins configs/sample_plugin.conf
install -D -g root -o root -m 0644 -p configs/qworkerd.cfgtool /etc/cfgtool/module.d/qworkerd
install -D -g root -o root -m 0644 -p configs/qworkerd.upstart.conf.templ /etc/init/qworkerd.conf.templ
