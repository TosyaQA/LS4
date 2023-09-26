import paramiko

def execute_command(ssh_client, command, text):
    try:
        stdin, stdout, stderr = ssh_client.exec_command(command)
        
        output = stdout.read().decode().strip()
        
        stdin.close()
        stdout.close()
        stderr.close()
        
        return text in output
    except paramiko.SSHException:
        return False