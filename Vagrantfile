# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"
  # config.vm.box = "trusty"
  config.vm.box_url = "https://cloud-images.ubuntu.com/trusty/current/trusty-server-cloudimg-i386-root.tar.gz"
  config.vm.network :private_network, ip: "192.168.7.77"
  config.vm.synced_folder ".", "/home/vagrant/projects/django-tornado-celery-example"

  config.vm.provision :shell, path: "./scripts/install.sh"

  # при любом reload поднимаем все, что нужно
  config.vm.provision :shell, path: "./scripts/venv.sh", run: "always", privileged: false
  config.vm.provision :shell, path: "./scripts/up.sh", run: "always"

  config.vm.provider "virtualbox" do |v|
    v.memory = 512
    # v.cpus = 2
  end
end
