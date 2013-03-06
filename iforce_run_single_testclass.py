import os, platform, sys
import shutil
import sublime, sublime_plugin
import iforceutil

from MetadataService_client import *

class iforce_run_single_testclassCommand(sublime_plugin.WindowCommand):
    currentFile = None
    prjFolder = None
    payloadFolderName = 'payload'
    payloadFolder = None
    payloadType = None
    payloadMetaTag = None
    pathSep = None
    antBin = None

    def set_environment_variables(self):
        if platform.system() == 'Windows':
            self.pathSep = '\\'
            self.antBin = 'ant.bat'
        else:
            self.pathSep = '/'
            self.antBin = 'ant'

    def is_enabled(self, *args):
        self.set_environment_variables()
        self.currentFile = self.window.active_view().file_name()
        return (self.pathSep != None) and \
            (self.pathSep + 'classes' in self.currentFile) and \
            (self.currentFile.endswith('.cls'))

    def call_metadata_api(self):
        loc = MetadataServiceLocator()
        kw = { 'tracefile' : sys.stdout }
        url = loc.getMetadataAddress()
        portType = loc.getMetadata(url, **kw)

        query = ns0.ListMetadataQuery_Def("C")
        query._folder = None
        query._type = "ApexClass"

        request = listMetadataRequest()
        request._queries = [query]
        request._asOfVersion = 26.0

        response = portType.listMetadata(request)
        print response

    def run(self, *args, **kwargs):
        self.call_metadata_api()
        return

        if self.window.active_view().is_dirty():
            self.window.active_view().run_command('save')

        self.set_environment_variables()

        self.prjFolder = self.window.folders()[0]
        print 'iForce: Project folder path' + self.prjFolder
        self.payloadFolder = self.prjFolder + '/' + self.payloadFolderName
        print 'iForce: Payload folder name' + self.payloadFolder

        try:
            shutil.rmtree(self.payloadFolder)
            print 'iForce: Old payload deleted'
        except Exception, e:
            print 'iForce: Couldn\'t delete old payload dir'

        self.currentFile = self.window.active_view().file_name()
        print 'iForce: Current File: ' + self.currentFile

        fileHead, fileTail = os.path.split(self.currentFile)
        print 'iForce: Filename: '+ fileTail + ' head: '+fileHead

        self.payloadType = 'classes'
        payloadMetaTag = 'ApexClass'

        print 'iForce: payloadmeta ' + payloadMetaTag

        # create dir
        os.makedirs(self.payloadFolder);
        os.makedirs(self.payloadFolder + '/' + self.payloadType);
        destFile = self.payloadFolder + '/' + self.payloadType + '/' + fileTail
        print 'iForce: DestFile '+destFile
        shutil.copyfile(self.currentFile, destFile)

        pfilename, pfileext = os.path.splitext(fileTail)
        print 'iForce: filename without extension ' + pfilename

        # try to copy existing meta file
        # if it does not exist, create one
        pmetapath = self.currentFile + '-meta.xml'

        # If meta file does not exist, create it
        if not os.path.exists(pmetapath):
            metaFileContent = '<?xml version="1.0" encoding="UTF-8"?>\n<'+payloadMetaTag+' xmlns="http://soap.sforce.com/2006/04/metadata"><apiVersion>25.0</apiVersion><status>Active</status></'+payloadMetaTag+'>'
            iforceutil.write_to_file(pmetapath, metaFileContent)

        pmetaname = os.path.basename(pmetapath)
        destFile = self.payloadFolder + '/' + self.payloadType + '/' + pmetaname
        shutil.copyfile(pmetapath, destFile)

        # write package file
        packageFileContent = '<?xml version="1.0" encoding="UTF-8"?>\n<Package xmlns="http://soap.sforce.com/2006/04/metadata"> <types> <members>'+pfilename+'</members> <name>'+payloadMetaTag+'</name> </types> <version>22.0</version> </Package>'
        packageFile = self.payloadFolder + '/package.xml'
        iforceutil.write_to_file(packageFile, packageFileContent)

        iforceutil.run_ant(self,[
            "-file", "iForce_build.xml",
            "-propertyfile", "iForce_build.properties",
            "-Dtestclass=" + pfilename,
            "runtest"
            ])
        self.window.run_command('exec',{'cmd': [self.antBin, "-file", "iForce_build.xml", "-propertyfile", "iForce_build.properties", "-Dtestclass=" + pfilename, "runtest"], 'working_dir':self.prjFolder})