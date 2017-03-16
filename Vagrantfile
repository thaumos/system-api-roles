
Vagrant.configure(2) do |config|
    config.vm.define "fedora", primary: true do |fedora|
      fedora.vm.box = "fedora/24-cloud-base"
      fedora.vm.provision "shell", inline: "dnf install -y python2 python2-dnf libselinux-python"
    end

    config.vm.define "centos" do |centos|
      centos.vm.box = "centos/6"
      centos.vm.provision "shell", inline: "yum install -y python2 libselinux-python"
    end

    config.vm.provision "system-api", type: "ansible" do |ansible|
      ansible.playbook = "example-playbook.yml"
    end
end
