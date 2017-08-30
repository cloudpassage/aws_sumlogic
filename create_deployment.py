import os
import subprocess
import zipfile
import yaml
import shutil


class CreateDeployments(object):
    def __init__(self):
        self.deployments_dir = "./deployments"
        self.pkg_reqs = "./requirements.txt"
        self.lib_reqs = os.path.join(os.path.dirname(__file__), './lib_requirements.yml')

    def read_package_requirements(self):
        with open(self.pkg_reqs, 'r') as f:
            install_requirements = f.readlines()

        return install_requirements

    def read_lib_requirements(self):
        return yaml.load(file(self.lib_reqs, 'r'))['modules']

    def get_immediate_subdirectories(self, a_dir):
        return [name for name in os.listdir(a_dir)
                if os.path.isfile(os.path.join(a_dir, name))]

    def remove_file_extension(self, filename):
        if filename.endswith('.zip'):
            return filename[:-4]

    def make_deployment_dir(self, name):
        all_deployment_directories = self.get_immediate_subdirectories(self.deployments_dir)
        max_deployment_number = -1
        matching_dir = []
        for directory in all_deployment_directories:
            if name in directory:
                matching_dir.append(directory)

        for deployment_dir in matching_dir:
            deployment_dir = self.remove_file_extension(deployment_dir)

            dir_name_elements = deployment_dir.split("_")
            if int(dir_name_elements[-1]) > max_deployment_number:
                max_deployment_number = int(dir_name_elements[-1])

        if max_deployment_number == -1:
            max_deployment_number = 0

        deployment_name = "{0}_{1}".format(name, max_deployment_number + 1)
        new_deployment_dir_path = "{0}/{1}".format(self.deployments_dir, deployment_name)

        if not os.path.exists(new_deployment_dir_path):
            os.mkdir(new_deployment_dir_path)

        return (new_deployment_dir_path, deployment_name)

    def install_requirements(self, deployment_requirements, deployment_dir):
        if os.path.exists(deployment_dir):
            for requirement in deployment_requirements:
                cmd = "pip install {0} -t {1}".format(requirement, deployment_dir).split()
                return_code = subprocess.call(cmd, shell=False)

    def copy_deployment_files(self, deployment_dir, deployment_files):
        for deployment_file in deployment_files:
            if os.path.exists(deployment_file):
                cmd = "cp {0} {1}".format(deployment_file, deployment_dir).split()
                return_code = subprocess.call(cmd, shell=False)
            else:
                raise NameError("Deployment file not found [{0}]".format(deployment_file))

    def delete_deployment_files(self, deployment_name):
        shutil.rmtree("%s/%s" % (self.deployments_dir, deployment_name))

    def trimPath(self, path, parentDir, dirToZip, includeDirInZip = False):
            archivePath = path.replace(parentDir, "", 1)
            if parentDir:
                archivePath = archivePath.replace(os.path.sep, "", 1)
            if not includeDirInZip:
                archivePath = archivePath.replace(dirToZip + os.path.sep, "", 1)
            return os.path.normcase(archivePath)

    def zipdir(self, dirPath=None, zipFilePath=None, includeDirInZip=False):
        if not zipFilePath:
            zipFilePath = dirPath + ".zip"
        if not os.path.isdir(dirPath):
            raise OSError("dirPath argument must point to a directory. "
                "'%s' does not." % dirPath)
        parentDir, dirToZip = os.path.split(dirPath)

        outFile = zipfile.ZipFile(zipFilePath, "w",
            compression=zipfile.ZIP_DEFLATED)
        for (archiveDirPath, dirNames, fileNames) in os.walk(dirPath):
            for fileName in fileNames:
                filePath = os.path.join(archiveDirPath, fileName)
                outFile.write(filePath, self.trimPath(filePath, parentDir, dirToZip))
            if not fileNames and not dirNames:
                zipInfo = zipfile.ZipInfo(self.trimPath(archiveDirPath, parentDir, dirToZip) + "/")
                outFile.writestr(zipInfo, "")
        outFile.close()

def main():
    d = CreateDeployments()
    files = d.read_lib_requirements()
    for key_name in files:
        deployment_dir, name = d.make_deployment_dir(key_name)
        d.copy_deployment_files(deployment_dir, files[key_name])
        package_requirements = d.read_package_requirements()
        d.install_requirements(package_requirements, deployment_dir)
        d.zipdir(deployment_dir, "{0}/{1}.zip".format(d.deployments_dir, name))
        d.delete_deployment_files(name)

if __name__ == "__main__":
    main()
