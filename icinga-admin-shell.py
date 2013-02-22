#!/usr/bin/python
# coding: utf-8

import cmd
import socket
import prettytable
import logging
from pynag import Model

_logfile = 'iciadmin.log'
Model.cfg_file = '/etc/icinga/icinga.cfg'

class IcingaAdminShell(cmd.Cmd):
	"""Icinga administration shell"""

	def __init__(self):
		cmd.Cmd.__init__(self)
		self.prompt = "{iciadmin} -> "
		self.show_args = ['hostgroups', 'hosts', 'servicegroups', 'services']
		self.add_args = ['hostgroup', 'host', 'servicegroup', 'service']
		self._all_hosts = Model.Host.objects.all
		logging.basicConfig(filename=_logfile, format='[%(asctime)s] %(levelname)s %(message)s', level=logging.DEBUG)
		logging.info("Starting UP...")

	def emptyline(self):
		return

	def _table(self, tabledef, align="l"):
		t = prettytable.PrettyTable(tabledef)
		t.align = align
		return t

	def _is_valid_input(self, input, values):
		if input not in values:
			print "Invalid input \"%s\"" % input
			return False
		else:
			return True

	def do_show(self, line):
		if line == 'hostgroups':
			_groups = Model.Hostgroup.objects.all
			t = self._table(["Name", "Alias"])
			for g in _groups:
				t.add_row([g.get_shortname(), g.alias])
			print t.get_string(sortby="Name")
		elif line == 'hosts':
			_host = Model.Host.objects.all
			t = self._table(["Name", "Address"])
			for h in _host:
				t.add_row([h.get_shortname(), h.address])
			print t.get_string(sortby="Name")
		elif line == 'services':
			_service = Model.Service.objects.all
			t = self._table(["Name", "Description"])
			for s in _service:
				t.add_row([s.get_shortname(), s.service_description])
			print t.get_string(sortby="Name")
		elif line == 'servicegroups':
			_sgroup = Model.Servicegroup.objects.all
			t = self._table(["Name", "Description"])
			for s in _sgroup:
				t.add_row([s.get_shortname(), s.alias])
			print t.get_string(sortby="Name")
		else:
			print "Unknown argument: %s" % line
			self.help_show()

	def do_showhost(self, line):
		try:
			_host = Model.Host.objects.get_by_shortname(line)
			print _host
		except(KeyError):
			print "Host \"%s\" not found..." % line
			self.help_showhost()

	def do_showservice(self, line):
		try:
			_service = Model.Service.objects.get_by_shortname(line)
			print _service
		except(KeyError):
			print "Service \"%s\" not found..." % line
			self.help_showservice()
	
	def do_create(self, line):
		if line == 'host':
			_host = Model.Host()
			while True:
				os = raw_input('OS Family [windows|linux]: ')
				if self._is_valid_input(os, ['windows', 'linux']): break
				else: continue
			while True:
				env = raw_input('Role [prod|svil]: ')
				if self._is_valid_input(env, ['prod', 'svil']): break
				else: continue
			hostname = raw_input('Hostname: ')
			try:
				_address = socket.gethostbyname(hostname)
			except:
				_address = ""
				pass
			address = raw_input('Ip address [%s]: ' % _address)
			if not address: address = _address
			_host.use = '%s-server' % os
			_host.host_name = hostname
			_host.address = address
			_host.alias = hostname
			_host.set_filename('/etc/icinga/cup2000/%s/%s.cfg' % (env, hostname))
			if raw_input('Write changes to file(s)? [yes/no]') == 'yes':
				_host.save()
				logging.info('Created host: %s, address: %s' % (hostname, address))
			else:
			print _host
		else:
			print "Unknown argument: %s" % line
			self.help_add()

	def complete_show(self, text, line, begidx, endidx):
		if not text:
			completions = self.show_args[:]
		else:
			completions = [f
							for f in self.show_args
							if f.startswith(text)
							]
		return completions

	def complete_showhost(self, text, line, begidx, endidx):
		hosts = []
		for h in _all_hosts:
			if h.get_shortname is not None: hosts.append(h.get_shortname())
		if not text:
			completions = hosts[:]
		else:
			completions = [f
							for f in hosts
							if f.startswith(text)
							]
		return completions

	def complete_create(self, text, line, begidx, endidx):
		if not text:
			completions = self.add_args[:]
		else:
			completions = [f
							for f in self.add_args
							if f.startswith(text)
							]
		return completions
	
	def help_show(self):
		print """show: shows objects\nUsage: show [hosts, hostgroups, services, servicegroups]"""

	def help_showhost(self):
		print """showhost: shows host details\nUsage: showhost <hostname>"""
	
	def help_showservice(self):
		print """showservice: shows service details\nUsage: showservice <service name>"""
	
	def help_add(self):
		print """add: adds new objects\nUsage: add [host, hostgroup, service, servicegroup]"""
	
	def do_EOF(self, line):
		logging.shutdown()
		return True
	
	def do_exit(self, line):
		"""Quit from this CLI"""
		logging.shutdown()
		return True

if __name__ == '__main__':
	IcingaAdminShell().cmdloop()
