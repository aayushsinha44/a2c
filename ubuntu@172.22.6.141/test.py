from paramiko import SSHClient, AutoAddPolicy

ssh=SSHClient()
ssh.set_missing_host_key_policy(AutoAddPolicy())
ssh.connect('172.22.6.140', username='ubuntu', password='intern1')
stdin, stdout, stderr = ssh.exec_command(
    "sudo dmesg")
stdin.write('intern1\n')
stdin.flush()
print("output")
data = stdout.readlines()
for line in data:
        print(line)
print("error")
data = stderr.readlines()
for line in data:
        print(line)