#!/opt/labtainer/venv/bin/python3
'''
This software was created by United States Government employees at 
The Center for Cybersecurity and Cyber Operations (C3O) 
at the Naval Postgraduate School NPS.  Please note that within the 
United States, copyright protection is not available for any works 
created  by United States Government employees, pursuant to Title 17 
United States Code Section 105.   This software is in the public 
domain and is not subject to copyright. 
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
  1. Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT,
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
'''
import os
import sys
import json
import subprocess
import VersionInfo
import LabtainerLogging
'''
Return creation date and user of a given image from the Docker Hub
without pulling the image.
'''
def inspectRemote(image, lgr):
    lgr.debug('inspectRemote image %s' % image)
    use_tag = 'latest'
    token = getToken(image)
    if token is None or len(token.strip()) == 0:
        return None, None
    digest = getDigest(token, image, 'latest')
    if digest is None:
        return None, None
    created, user = getCreated(token, image, digest)
    #print('created %s  user %s' % (created, user))
    return created, user

def extractJson(output):
    output=output.strip()
    if output.startswith('{'):
        return output
    start = output.find('{"arch')
    if start >=0:
        return output[start:]
    else:
        print('Failed to find start of json')
        return output

def getTags(image, token):
    cmd =   'curl --silent --header "Accept: application/vnd.docker.distribution.manifest.v2+json" --header "Authorization: Bearer %s"  "https://registry-1.docker.io/v2/%s/tags/list"' % (token, image)
    ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output = ps.communicate()
    if len(output[0].strip()) > 0:
        jstring = extractJson(output[0].decode('utf-8'))
        try:
            j = json.loads(jstring)
        except:
            print('Unable to reach docker registry.  Is your network connection working?')
            exit(1)
        if 'tags' in j:
            return j['tags']
        else:
            return None
    else:
        return None

def getToken(image):
    cmd = 'curl --silent "https://auth.docker.io/token?scope=repository:%s:pull&service=registry.docker.io"' % (image) 
    #cmd = 'curl --silent "https://auth.docker.io/token?service=registry.docker.io&scope=repository:%s:pull,push"' % (image)
    #print('cmd is %s' % cmd)
    ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output = ps.communicate()
     
    if len(output[0].strip()) > 0:
        jstring = extractJson(output[0].decode('utf-8'))
        j = json.loads(jstring)
        return j['token']
        #return j['access_token']
    else:
        return None

        
def getDigest(token, image, tag):
    cmd = 'curl --silent --header "Accept: application/vnd.docker.distribution.manifest.v2+json" --header "Authorization: Bearer %s" "https://registry-1.docker.io/v2/%s/manifests/%s"' % (token, image, tag) 
    ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output = ps.communicate()
    if len(output[0].strip()) > 0:
        jstring = extractJson(output[0].decode('utf-8'))
        try:
            j = json.loads(jstring)
        except ValueError:
            with open('/tmp/docker_error.txt', 'w') as fh:
                fh.write(cmd+'\n'+output[0].decode('utf-8'))
            print('Error getting digest for image: %s tag: %s' % (image, tag))
            print('please email the file at /tmp/docker_error.txt to mfthomps@nps.edu')
            exit(1)
        if 'config' in j:
            return j['config']['digest']
        else:
            ''' assume not found error? '''
            return None
    else:
        return None

def getCreated(token, image, digest):
    cmd = 'curl -L --silent --header "Authorization: Bearer %s" "https://registry-1.docker.io/v2/%s/blobs/%s"' % (token, image, digest)
    ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    output = ps.communicate()
    
    if len(output[0].strip()) > 0:
        ''' Sometimes get redirected, and authentication then fails? '''
        jstring = extractJson(output[0].decode('utf-8'))
        try:
            j = json.loads(jstring)
        except ValueError:
            with open('/tmp/docker_error.txt', 'w') as fh:
                fh.write(cmd+'\n'+output[0])
            print('Error getting blob for image: %s digest: %s' % (image, digest))
            print('please email the file at /tmp/docker_error.txt to mfthomps@nps.edu')
            exit(1)
        return j['created'], j['container_config']['User']
    else:
        return None, None

if __name__ == '__main__':
    logger = LabtainerLogging.LabtainerLogging("remotebase.log", 'none', "../../config/labtainer.config")
    inspectRemote(sys.argv[1], logger)
