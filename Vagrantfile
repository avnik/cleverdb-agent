# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.ssh.forward_agent = true
  config.vm.synced_folder Dir.getwd, "/home/vagrant/cleverdb-agent", nfs: true

  # master db
  config.vm.define 'master-db', primary: true do |c|
    c.vm.network "private_network", ip: "192.168.100.2"
    c.vm.box = "trusty-server-cloudimg-amd64-vagrant-disk1"
  	c.vm.box_url = "https://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"
  end

  # slave db:
  config.vm.define 'slave-db' do |c|
  	c.vm.network "private_network", ip: "192.168.100.3"
    c.vm.box = "trusty-server-cloudimg-amd64-vagrant-disk1"
  	c.vm.box_url = "https://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"
  end
end
