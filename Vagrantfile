
Vagrant.configure(2) do |config|
    config.vm.box = "fedora/24-cloud-base"

    config.vm.provision "shell" do |shell|
      shell.inline = "dnf install -y python2 python2-dnf libselinux-python"
    end

    # Optional provisioners
    #
    # check for '--provision-with' argument manually because "run: 'never'"
    # doesn't work with ansible 2.2.0
    if ARGV.include? '--provision-with'

      config.vm.provision "selinux", type: "ansible" do |ansible|
        ansible.playbook = "example-SELinux.yml"
      end

      config.vm.provision "kdump", type: "ansible" do |ansible|
        ansible.playbook = "example-plbk-kdump.yml"
      end

    end
end
