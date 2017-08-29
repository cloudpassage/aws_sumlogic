import os
import subprocess
import zipfile

root_deployments_dir = "./deployments"
# deployment_files = ['halo_events_to_sumologic.py', 'queue_utility.py', 'sumologic_https.py']
deployment_files = ['halo_metrics_to_sumologic.py', 'metrics_utility.py', 'sumologic_https.py']


def _read_requirements():
    with open("./requirements.txt", 'r') as f:
        install_requirements = f.readlines()

    return install_requirements

def _get_immediate_subdirectories(a_dir):
    return [name for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

def _make_deployment_dir():
    all_deployment_directories = _get_immediate_subdirectories(root_deployments_dir)
    max_deployment_number = -1
    for deployment_dir in all_deployment_directories:
        dir_name_elements = deployment_dir.split("_")
        if( len(dir_name_elements) == 2):
            if int(dir_name_elements[1]) > max_deployment_number:
                max_deployment_number = int(dir_name_elements[1])

    if max_deployment_number == -1:
        max_deployment_number = 0

    deployment_name = "deployment_{0}".format(max_deployment_number+1)
    new_deployment_dir_path = "{0}/{1}".format(root_deployments_dir, deployment_name)

    if not os.path.exists(new_deployment_dir_path):
        os.mkdir(new_deployment_dir_path)

    return (new_deployment_dir_path, deployment_name)

def _install_requirements(deployment_requirements, deployment_dir):
    if os.path.exists(deployment_dir):
        for requirement in deployment_requirements:
            cmd = "pip install {0} -t {1}".format(requirement, deployment_dir).split()
            return_code = subprocess.call(cmd, shell=False)

def _copy_deployment_files(deployment_dir):
    for deployment_file in deployment_files:
        if os.path.exists(deployment_file):
            cmd = "cp {0} {1}".format(deployment_file, deployment_dir).split()
            return_code = subprocess.call(cmd, shell=False)
        else:
            raise NameError("Deployment file not found [{0}]".format(deployment_file))


def zipdir(dirPath=None, zipFilePath=None, includeDirInZip=False):
    if not zipFilePath:
        zipFilePath = dirPath + ".zip"
    if not os.path.isdir(dirPath):
        raise OSError("dirPath argument must point to a directory. "
            "'%s' does not." % dirPath)
    parentDir, dirToZip = os.path.split(dirPath)

    def trimPath(path):
        archivePath = path.replace(parentDir, "", 1)
        if parentDir:
            archivePath = archivePath.replace(os.path.sep, "", 1)
        if not includeDirInZip:
            archivePath = archivePath.replace(dirToZip + os.path.sep, "", 1)
        return os.path.normcase(archivePath)

    outFile = zipfile.ZipFile(zipFilePath, "w",
        compression=zipfile.ZIP_DEFLATED)
    for (archiveDirPath, dirNames, fileNames) in os.walk(dirPath):
        for fileName in fileNames:
            filePath = os.path.join(archiveDirPath, fileName)
            outFile.write(filePath, trimPath(filePath))
        if not fileNames and not dirNames:
            zipInfo = zipfile.ZipInfo(trimPath(archiveDirPath) + "/")
            outFile.writestr(zipInfo, "")
    outFile.close()

if __name__ == "__main__":
    (deployment_dir, deployment_name) = _make_deployment_dir()
    _copy_deployment_files(deployment_dir)
    install_requirements = _read_requirements()
    _install_requirements(install_requirements, deployment_dir)

    zipdir(deployment_dir, "{0}/{1}.zip".format(root_deployments_dir, deployment_name))
