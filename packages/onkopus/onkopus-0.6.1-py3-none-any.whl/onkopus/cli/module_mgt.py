import os
import subprocess
import traceback
import yaml
import onkopus.conf.read_config as conf_reader
import onkopus.conf.docker_config as docker_config


def remote_install(modules):
    """
    Script for downloading and installing Onkopus in a restricted environment.
    Downloads all Onkopus images and stores them as .tar files.
    The .tar files can then be uploaded (e.g. in a clinical infrastructure), and loaded using
    'docker load < *.tar'.

    :return:
    """
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    data_dir = __location__ + "/../conf"
    yml_file_dir = data_dir + '/docker_compose'

    file_list = []
    for root, dirs, files in os.walk(yml_file_dir):
        for file in files:
            file_list.append(os.path.join(root, file))

    # Download all images
    for yml_file in file_list:
        cmd = "docker-compose -f " + yml_file + " pull"
        subprocess.run(cmd, shell=True)

        # Store image as .tar files
        with open(yml_file, 'r') as file:
            data = yaml.full_load(file)

            #print(data)
            services = data.get('services', [])
            #print("Service: ",services)

            for image_key in services.keys():
                image_info = services[image_key]
                image = image_info.get('image')
                container_name = image_info.get('container_name')
                if not image:
                    print("Image name is missing in the YAML file.")
                    continue

            output_file = f"{image.replace('/', '_').replace(':', '_')}.tar"
            with open(output_file, 'wb') as f:
                print("Saving ",container_name," to ",output_file)
                subprocess.run(['docker', 'save', '-o', output_file, image], check=True)

            print(f"Image '{image}' saved to '{output_file}'")

def get_docker_compose_files(module):
    if module in docker_config.module_ids:
        return docker_config.module_ids[module]
    else:
        return []


def _add_new_module(module, __data_dir__):
    with open(__data_dir__ + "/" + conf_reader.config["DEFAULT"]["INSTALLED_MODULES_FILE"], "a") as file:
        file.write(module + '\n')


def install(module, installed_modules, available_modules):
    """
    Installs an Onkopus module

    :param module:
    :return:
    """
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    data_dir = __location__ + "/../conf"

    print("Install Onkopus module: ", module)

    # Check if module is already installed
    #if module in installed_modules:
    #    print("Module " + module + " is already installed")
    #    return

    # Download databases
    if module in available_modules:
        # add Docker compose entry
        #print("Adding Docker compose entry for " + module + "...", end='')
        template_files = get_docker_compose_files(module) #[data_dir + "/docker_compose/" + module + ".yml"]
        for tfile in template_files:
            os.system("cp -v " + data_dir + "/docker_compose/" + tfile + " " + data_dir + "/installed_modules/")

        #if module == "uta-adapter":
        #    template_files.append(data_dir + "/docker_compose/uta-database.yml")

        #for tfile in template_files:
        #    template_file = open(tfile)
        #    lines = []
        #    for line in template_file:
        #        lines.append(line)

        #    #docker_compose_file = data_dir + "/data/docker-compose.yml"
        #    #with open(docker_compose_file, "a") as dc_file:
        #    #    for line in lines:
        #    #        dc_file.write(line)
        #    #template_file.close()

        # pull Onkopus module Docker container
        #print("Pull Docker container for " + module, end='')
        print('Installing module ' + module + '...')
        #cmd = "docker-compose -f (ls " + data_dir + "/installed_modules | tr '\n' ' ') pull"
        #f"ls {data_dir}/installed_modules/*.yml | tr '\n' ' '"

        # get associated containers
        images = docker_config.module_ids[module]

        #list_command = f"ls {data_dir}/installed_modules/*.yml | tr '\n' ' '"
        # Execute the list command and capture the output
        #result = subprocess.run(list_command, shell=True, capture_output=True, text=True)

        # Check if the command was successful
        #if result.returncode == 0:
        for image in images:
            # Get the list of .yml files as a single string with spaces
            #yml_files = result.stdout.strip()

            #file_list = yml_files.split()
            #prefixed_files = ['-f ' + file for file in file_list]
            #prefixed_files_str = ' '.join(prefixed_files)
            yml_file = data_dir + '/docker_compose/' + image
            print("Pulling image " + yml_file)

            # Construct the docker-compose command
            cmd = f"docker-compose "
            cmd += '-f ' + yml_file
            #for yml_file in yml_files:
            #    cmd += f"-f {yml_file} "
            cmd += " pull"

            print(cmd)
            # os.system("docker-compose " + data_dir + "/data/docker-compose.yml pull")
            #os.system(cmd)

            # Execute the docker-compose command
            subprocess.run(cmd, shell=True)
        else:
            print(traceback.format_exc())

        _add_new_module(module, data_dir)

        #print("Onkopus module successfully installed: " + module)
    else:
        print(
            "[Error] No Onkopus module found: " + module + ". Get a list of all available modules with 'onkopus list-modules'")

def start_modules(installed_modules):
        """
        Starts all installed Onkopus modules as Docker containers

        :return:
        """
        print("Starting locally installed Onkopus modules")
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        data_dir = __location__ + "/../conf"

        #print("Installed modules: " + ",".join(installed_modules))

        # Start Docker containers
        #dc_cmd = "docker-compose -f " + data_dir + "/data/docker-compose.yml up -d"
        #print(dc_cmd)
        #os.system(dc_cmd)
        list_command = f"ls {data_dir}/installed_modules/*.yml | tr '\n' ' '"

        # Execute the list command and capture the output
        result = subprocess.run(list_command, shell=True, capture_output=True, text=True)

        # Check if the command was successful
        if result.returncode == 0:
            # Get the list of .yml files as a single string with spaces
            yml_files = result.stdout.strip()
            file_list = yml_files.split()
            prefixed_files = ['-f ' + file for file in file_list]
            prefixed_files_str = ' '.join(prefixed_files)

            # Construct the docker-compose command
            #cmd = f"docker-compose -f {yml_files} up -d"
            cmd = f"docker-compose "
            cmd += prefixed_files_str
            #for yml_file in yml_files:
            #    cmd += f"-f {yml_file} "
            cmd += " up -d"

            print(cmd)
            # os.system("docker-compose " + data_dir + "/data/docker-compose.yml pull")
            # os.system(cmd)

            # Execute the docker-compose command
            subprocess.run(cmd, shell=True)
        else:
            print(f"Error listing .yml files: {result.stderr}")

        print("Onkopus started")

def stop_modules():
        """
        Stops all running Onkopus containers

        :return:
        """
        print("Stopping Onkopus modules")
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        data_dir = __location__ + "/../conf"

        #os.system("docker-compose -f " + data_dir + "/docker-compose.yml down")
        list_command = f"ls {data_dir}/installed_modules/*.yml | tr '\n' ' '"

        # Execute the list command and capture the output
        result = subprocess.run(list_command, shell=True, capture_output=True, text=True)

        # Check if the command was successful
        if result.returncode == 0:
            # Get the list of .yml files as a single string with spaces
            yml_files = result.stdout.strip()
            file_list = yml_files.split()
            prefixed_files = ['-f ' + file for file in file_list]
            prefixed_files_str = ' '.join(prefixed_files)

            # Construct the docker-compose command
            #cmd = f"docker-compose -f {yml_files} stop"
            cmd = f"docker-compose "
            cmd += prefixed_files_str
            #for yml_file in yml_files:
            #    cmd += f"-f {yml_file} "
            cmd += " stop"

            print(cmd)
            # os.system("docker-compose " + data_dir + "/data/docker-compose.yml pull")
            # os.system(cmd)

            # Execute the docker-compose command
            subprocess.run(cmd, shell=True)
        else:
            print(f"Error listing .yml files: {result.stderr}")

        print("Onkopus stopped")
