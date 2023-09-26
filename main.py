import pytest
import yaml
from execute_command import execute_command
import paramiko

hostname = "ip"
port = 22
username = "username"
password = "password"
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(hostname, port=port, username=username, password=password)

@pytest.fixture
def update_stat_fixture():
    current_time = ssh_client.exec_command("date +'%Y-%m-%d %H:%M:%S'")
    
    config_file = "config.yaml"
    config_content = ssh_client.exec_command(f"cat {config_file}")
    config = yaml.safe_load(config_content)
    folderin = config.get('folderin')
    folderout = config.get('folderout')
    folderext = config.get('folderext')

    count_files_in = ssh_client.exec_command(f"ls -1 {folderin} | wc -l")
    count_files_out = ssh_client.exec_command(f"ls -1 {folderout} | wc -l")
    count_files_ext = ssh_client.exec_command(f"ls -1 {folderext} | wc -l")
    file_size_in = ssh_client.exec_command(f"du -sh {folderin} | cut -f1")
    file_size_out = ssh_client.exec_command(f"du -sh {folderout} | cut -f1")
    file_size_ext = ssh_client.exec_command(f"du -sh {folderext} | cut -f1")

    # Читаем статистику загрузки процессора из файла /proc/loadavg на удаленном сервере
    cpu_load = execute_command(ssh_client, "cat /proc/loadavg")
    
    # Дописываем строку в файл stat.txt на удаленном сервере
    stat_file = "stat.txt"
    execute_command(ssh_client, f"echo '{current_time} - Files In: {count_files_in}, Size In: {file_size_in}, Files Out: {count_files_out}, Size Out: {file_size_out}, Files Ext: {count_files_ext}, Size Ext: {file_size_ext}, CPU Load: {cpu_load}' >> {stat_file}")
    
    # Закрываем соединение с удаленным сервером
    ssh_client.close()

@pytest.mark.usefixtures("update_stat_fixture")
def test_list_files(command, expected_files):
    assert execute_command(ssh_client, command, '\n'.join(expected_files)) == True, f"Ошибка: файлы {expected_files} не найдены"

@pytest.mark.usefixtures("update_stat_fixture")
def test_extract_archive(command, expected_files):
    assert execute_command(ssh_client, command, '\n'.join(expected_files)) == True, f"Ошибка: файлы {expected_files} не удалось разархивировать"

test_extract_archive("unzip -j archive.zip", ["file1.txt", "file2.txt", "file3.txt"])

test_list_files("ls", ["file1.txt", "file2.txt", "file3.txt"])