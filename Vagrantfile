
Vagrant.configure(2) do |config|
    config.vm.define "fedora", primary: true do |fedora|
      fedora.vm.box = "fedora/24-cloud-base"
      fedora.vm.provision "shell", inline: "dnf install -y python2 python2-dnf libselinux-python"
    end

    config.vm.define "centos" do |centos|
      centos.vm.box = "centos/6"
      centos.vm.provision "shell", inline: "yum install -y python2 libselinux-python"
    end

    # Optional provisioners
    #
    # check for '--provision-with' argument manually because "run: 'never'"
    # doesn't work with ansible 2.2.0
    if ARGV.include? '--provision-with'

      config.vm.provision "system-api", type: "ansible" do |ansible|
        ansible.playbook = "example-playbook.yml"
      end

    end
end
