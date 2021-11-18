#
## unconnect everything
#system "aconnect -x"
#
#t = `aconnect -i -l`
#ports = []
#names = []
#t.lines.each do |l|
#  /client (\d*)\: '(.*)'/=~l
#  port = $1
#  name = $2
#  # we skip empty lines and the "Through" port
#  unless $1.nil? || $1 == '0' || /Through/=~l
#    ports << port
#    names << name
#  end
#end
#
#ports.each do |p1|
#  ports.each do |p2|
#    unless p1 == p2 # probably not a good idea to connect a port to itself
#      system  "aconnect #{p1}:0 #{p2}:0"
#    end
#  end
#end
#
#cmd = "/usr/local/bin/lcd-show.py"
#if names.length>1 then
#  command = "#{cmd} #{names.map(&:inspect).join(' ')} "
#else
#  command = "#{cmd} '' 'No MIDI' 'connections' "
#end
#
#pid = spawn(command)
#Process.detach(pid)

import re
import subprocess
from lib import display
def getDeviceList():
    command = 'aconnect -i -l'
    result = subprocess.run(command.split(' '), stdout=subprocess.PIPE)
    # create a list for each line in the command output and remove lines containing 'Through'
    devices = [i for i in result.stdout.decode('utf-8').split('\n') if 'Through' not in i]
    # find id and name for each device
    deviceDict = []
    for dev in devices:
        match = re.match("client (\d*)\: '(.*)'", dev)
        if match:
            deviceDict.append({'id': match.group(1), 'name': match.group(2)})
    return deviceDict

display = display.Display()
print(getDeviceList())
for dev in getDeviceList():
    display.lcd_string(dev['id'] + ':' + dev['name'], 0)
