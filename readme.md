# usbmidihost
inspired by: https://neuma.studio/rpi-midi-complete.html

## installation

### from a remote host

1. clone the repo and cd into it(`git clone https://github.com/ljurk/usbmidihost.git && cd usbmidihost`)
2. find IP address of the pi(f.e. 192.168.0.23)
3. copy your public key to the pi(`ssh-copy-id pi@192.168.0.23`)
4. run the playbook(`ansible-playbook playbook.yml -i 192.168.0.23,`)

### from the pi itself

1. clone the repo and cd into it(`git clone https://github.com/ljurk/usbmidihost.git && cd usbmidihost`)
3. run the playbook(`ansible-playbook playbook.yml -i localhost,`)
