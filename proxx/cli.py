import argparse 
import configparser
import os
from subprocess import call


proxy_var={
    'http_username':None,
    'http_password':None,
    'http_proxy':None,
    'http_port':None,
    'https_username':None,
    'https_password':None,
    'https_proxy':None,
    'https_port':None,
    'no_proxy':None,
    'use_proxy':None,
}

apps={
    'docker':{},
    'git'   :{},
    'npm'   :{},
    'yarn'  :{},
    'shell' :{},
}

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def msg(title,data,type='ok'):
    title_color=bcolors.OKGREEN
    if type == 'ok':
        title_color=bcolors.OKGREEN
    if type == 'warn':
        title_color=bcolors.WARNING
    if type == 'fail':
        title_color=bcolors.FAIL
    if type == 'underline':
        title_color=bcolors.UNDERLINE
        
    print ("{2}***[{3}{0}{2}]***{4} {1}".format(title,data,bcolors.OKBLUE,title_color,bcolors.ENDC))

def is_cmd_installed(cmd):
    res=call(['which',cmd])
    if 0==res:
        return True
    return False

def load_config():
    global apps
    config_file=os.path.expanduser('~/.proxx.ini')
    exists = os.path.isfile(config_file)
    if True != exists:
        return
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(config_file)
    try:
        for key in apps:
            if  True == config.has_section(key):
                for sub_key in proxy_var:
                    if  True == config.has_option(key,sub_key):
                        #print (key,sub_key)
                        if 'use_proxy' == sub_key:
                            apps[key][sub_key]=config[key].getboolean(sub_key)
                        else:
                            apps[key][sub_key]=config[key][sub_key]
            set_targets(key)
    except Exception as ex:
        msg("Loading config Err:",ex,"fail")

def save_config():
    #return
    config_file=os.path.expanduser('~/.proxx.ini')

    config = configparser.ConfigParser(allow_no_value=True)
    try:
        header="""[defaults]
http_username      = sam         ; HTTP proxy credential (Not needed if setup in CNTLM)
http_password      = sampwd      ; HTTP proxy credential (Not needed if setup in CNTLM)
http_proxy         = localhost   ; HTTP proxy uri
http_port          = 3128        ; HTTP proxy port
https_username     = sam         ; * The same as above, but for HTTPS
https_password     = sampw       ; * If omitted, the http option is used
https_proxy        = localhost   ; *
https_port         = 3128        ; *
no_proxy           = website.com website2.com website 3.com   ; usually internal sites
use_proxy          = comments    ; enable or disable this proxy config


"""

        #print proxy_var
        for key in apps:
            config[key]={}
            remove_section=True
            for sub_key in apps[key]:
                if sub_key in proxy_var:
                    if None != apps[key][sub_key]:
                        value="{0}".format(apps[key][sub_key])
                        config[key][sub_key]=value
                        remove_section=False
            if True == remove_section:
                config.remove_section(key)

        config.remove_section('defaults')
        with open(config_file, 'w') as configfile:
            #configfile.write(header)
            config.write(configfile)
    except Exception as ex:
        msg("Saving config",ex,"fail")


def set_targets(config):
    http_proxy       =None
    http_port        =None
    http_username    =None
    http_password    =None
    https_proxy      =None
    https_port       =None
    https_username   =None
    https_password   =None
    no_proxy         =None

    if 'http_proxy'     in apps[config]:
        http_proxy    = apps[config]['http_proxy']
    if 'http_port'      in apps[config]:
        http_port     = apps[config]['http_port']
    if 'http_username'  in apps[config]:
        http_username = apps[config]['http_username']
    if 'http_password'  in apps[config]:
        http_password = apps[config]['http_password']
    if 'https_proxy'    in apps[config]:
        https_proxy   = apps[config]['https_proxy']
    if 'https_port'     in apps[config]:
        https_port    = apps[config]['https_port']
    if 'https_username' in apps[config]:
        https_username= apps[config]['https_username']
    if 'https_password' in apps[config]:
        https_password= apps[config]['https_password']
    if 'no_proxy'        in apps[config]:
        no_proxy      = apps[config]['no_proxy']

    
    apps[config]=set_proxy(http_proxy ,http_port ,http_username ,http_password,
                           https_proxy,https_port,https_username,https_password,no_proxy,dont_set_use=True)


def set_proxy(http_proxy ="127.0.0.1",http_port ="3128",http_username =None,http_password=None,
              https_proxy=None       ,https_port=None  ,https_username=None,https_password=None,noproxy=None,dont_set_use=False):
    """Configure individual proxy settings per application"""
    app_proxy={}
    app_proxy['no_proxy']=noproxy
    
    if http_proxy == None and https_proxy == None:
        app_proxy['use_proxy']=False
        

    if None == http_username:
        if http_proxy == None:
            app_proxy['http_proxy_target']=None
        else:
            app_proxy['http_proxy_target']="{0}:{1}".format(http_proxy,http_port)
        app_proxy['http_proxy']  =http_proxy
        app_proxy['http_port']   =http_port
        app_proxy['http_username']=http_username
        app_proxy['http_password']=http_password
    else:
        app_proxy['http_proxy_target']="{0}:{1}@{2}:{3}".format(http_username,http_password,http_proxy,http_port)
        app_proxy['http_proxy']   =http_proxy
        app_proxy['http_port']    =http_port
        app_proxy['http_username']=http_username
        app_proxy['http_password']=http_password


    # if no https is set.. duplicate parameters
    if None == https_proxy:
        app_proxy['https_proxy_target']=app_proxy['http_proxy_target']
        app_proxy['https_proxy']   =http_proxy
        app_proxy['https_port']    =http_port
        app_proxy['https_username']=http_username
        app_proxy['https_password']=http_password
    else:
        # if one is set, make target like http
        if None == https_username:
            app_proxy['https_proxy_target']="{0}:{1}".format(https_proxy,https_port)
            app_proxy['https_proxy']   =https_proxy
            app_proxy['https_port']    =https_port
        else:
            app_proxy['https_proxy_target']="{0}:{1}@{2}:{3}".format(https_username,https_password,https_proxy,https_port)
            app_proxy['https_proxy']   =https_proxy
            app_proxy['https_port']    =https_port
            app_proxy['https_username']=https_username
            app_proxy['https_password']=https_password
    if False == dont_set_use:
        app_proxy['use_proxy']=True
    return app_proxy


def create_file(path,filename,data):
    file_path=path+filename
    with open(file_path, 'wb') as temp_file:
        temp_file.write(data)


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def configure_shell():
    msg("Perform ","shell config")
    proxy=apps['shell']

    if True== proxy['use_proxy']:
        call(["export","HTTP_PROXY={0} ".format(proxy['http_proxy_target'])])
        call(["export","HTTPS_PROXY={0}".format(proxy['https_proxy_target'])])
    else:
        call(["unset","HTTP_PROXY"])
        call(["unset","HTTPS_PROXY"])
    

def configure_docker():
    if False == is_cmd_installed("docker"):
        msg("System","docker is not installed","warn")
        return False
    msg("Perform ","docker config")
    proxy_dir        = '/etc/systemd/system/docker.service.d/'
    http_proxy_file  = 'http-proxy.conf'
    https_proxy_file = 'https-proxy.conf'

    proxy=apps['docker']
    if True== proxy['use_proxy']:
        comment=""
    else:
        comment="#"
    
    # Data
    http_proxy_content="""[Service]
    {1}Environment="HTTP_PROXY={0}"
    """.format(proxy['http_proxy_target'],comment)

    https_proxy_content="""[Service]
    {1}Environment="HTTPS_PROXY={0}"
    """.format(proxy['https_proxy_target'],comment)

    # action 
    create_dir(proxy_dir)
    create_file(proxy_dir,http_proxy_file ,http_proxy_content)
    create_file(proxy_dir,https_proxy_file,https_proxy_content)
    call(["service","docker","restart"])
    call(["systemctl","daemon-reload"])


def configure_npm():
    if False == is_cmd_installed("npm"):
        msg("System","npm is not installed","warn")
        return False

    msg("Perform ","npm config")
    proxy=apps['npm']

    if True== proxy['use_proxy']:
        call(["npm","config","set","proxy"      ,"{0}".format(proxy['http_proxy_target'])])
        call(["npm","config","set","https-proxy","{0}".format(proxy['https_proxy_target'])])
    else :
        call(["npm","config","rm","proxy"])
        call(["npm","config","rm","https-proxy"])
    # TODO or persistent file
    #~/.npmrc file:
    #proxy=http://username:password@proxy:port
    #https-proxy=http://username:password@proxy:port
    #https_proxy=http://username:password@proxy:port
    
def configure_git():
    if False == is_cmd_installed("git"):
        msg("System","git is not installed","warn")
        return False

    msg("Perform ","git config")
    proxy=apps['git']


    print proxy['use_proxy']
    
    if True == proxy['use_proxy']:
        print "Setting"
        call(["/usr/bin/git","config","--global","http.proxy" ,"{0}".format(proxy['http_proxy_target']) ])
        call(["/usr/bin/git","config","--global","https.proxy","{0}".format(proxy['https_proxy_target']) ])
    else:
        print ("Unsetting")
        call(["/usr/bin/git","config","--global","--unset","http.proxy"])
        call(["/usr/bin/git","config","--global","--unset","https.proxy"])
    # TODO persistent config
    #~/.gitconfig file:
    #[http]
    #    proxy = http://username:password@proxy:port
    #[https]
    #    proxy = http://username:password@proxy:port


def configure_yarn():
    if False == is_cmd_installed("yarn"):
        msg("System","yarn is not installed","warn")
        return False

    msg("Perform ","yarn config")
    proxy=apps['yarn']

    if True== proxy['use_proxy']:
        call(["yarn","config","set","proxy"      ,"{0}".format(proxy['http_proxy_target'])])
        call(["yarn","config","set","https-proxy","{0}".format(proxy['https_proxy_target'])])
    else:
        call(["yarn","config","delete","proxy"])
        call(["yarn","config","delete","https-proxy"])


#def configure_maven():
#    "~/.m2/settings.xml"
#
#    """<proxies>
#        <proxy>
#            <id>id</id>
#            <active>true</active>
#            <protocol>http</protocol>
#            <username>username</username>
#            <password>password</password>
#            <username>{0}</username>
#            <password>{1}</password>
#            <proxy>{2}</proxy>
#            <port>{3}</port>
#            <nonProxyproxys>{4}</nonProxyproxys>
#        </proxy>
#        <proxy>
#            <id>HTTPS_PROXY</id>
#            <active>true</active>
#            <protocol>https</protocol>
#            <username>{0}</username>
#            <password>{1}</password>
#            <proxy>{2}</proxy>
#            <port>{3}</port>
#            <nonProxyproxys>{4}</nonProxyproxys>
#        </proxy>
#    </proxies>""".format(proxy_username,proxy_password,proxy_proxy,proxy_port,no_proxy)
#    
#
#def configure_gradel():
#    ox.path.
#    ~/.gradle/gradle.properties
#    ## Proxy setup
#    systemProp.proxySet="true"
#    systemProp.http.keepAlive="true"
#    systemProp.http.proxyproxy=proxy
#    systemProp.http.proxyPort=port
#    systemProp.http.proxyUser=username
#    systemProp.http.proxyPassword=password
#    systemProp.http.nonProxyproxys=local.net|some.proxy.com
#
#    systemProp.https.keepAlive="true"
#    systemProp.https.proxyproxy=proxy
#    systemProp.https.proxyPort=port
#    systemProp.https.proxyUser=username
#    systemProp.https.proxyPassword=password
#    systemProp.https.nonProxyproxys=local.net|some.proxy.com
#
def am_i_behind_a_proxy():
    return False


def is_this_a_docker():
    exit_code=call(['/usr/bin/grep','docker','/proc/self/cgroup','-qa'])
    if 0 == exit_code:
        return True
    return False

def print_config(config):
    print ("[{}]".format(config))
    for key in apps[config]:
        if None != apps[config][key]:
            print ("{0} = {1}".format(key,apps[config][key]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("proxx", usage='%(prog)s [options]'
                    ,description=
                    """proxy configurator for applications
                       https* variables are optional, and willl be set to the http counterparts if not set
                    """, epilog="And that's how you'd proxx")

    # actions
    parser.add_argument('-l'      ,'--list'           , help= 'show available proxy applications'   , action='store_true')
    parser.add_argument('-c'      ,'--config'         , help= 'show config'                         , action='store_true')
    parser.add_argument('-r'      ,'--remove'         , help= 'remove all proxy configurations'     , nargs='?', default=False)
    
    # config parameters
    parser.add_argument('-uri'    ,'--proxy'          , help= 'the endpoint http proxy')
    parser.add_argument('-prt'    ,'--port'           , help= 'the endpoint http proxy')
    parser.add_argument('-usr'    ,'--username'       , help= 'the http user for the http proxy')
    parser.add_argument('-pwd'    ,'--password'       , help= 'the password for the http proxy')
    parser.add_argument('-suri'   ,'--https-proxy'    , help= 'the endpoint https proxy')
    parser.add_argument('-sprt'   ,'--https-port'     , help= 'the endpoint https proxy')
    parser.add_argument('-susr'   ,'--https-username' , help= 'the http user for the https proxy')
    parser.add_argument('-spwd'   ,'--https-password' , help= 'the password for the https proxy')
    parser.add_argument('-np'     ,'--no-proxy'       , help= 'the password for the https proxy')
 
    # app configs
    parser.add_argument('-s'      ,'--shell'          , help= 'apply to "shell/bash/this instance"' , action='store_true')
    parser.add_argument('-g'      ,'--git'            , help= 'apply to "git"'                      , action='store_true')
    parser.add_argument('-d'      ,'--docker'         , help= 'apply to "docker"'                   , action='store_true')
    parser.add_argument('-n'      ,'--npm'            , help= 'apply to "npm"'                      , action='store_true')
    parser.add_argument('-y'      ,'--yarn'           , help= 'apply to "yarn"'                     , action='store_true')
    parser.add_argument('-a'      ,'--all'            , help= 'apply to "all applications"'         , action='store_true')
 

    args = parser.parse_args()
    config_changed=False
    use_proxy=True
    is_docker=is_this_a_docker()
    msg("Status","This is not a Docker")
    load_config()
    
    #print (apps)

    if True== args.list:
        msg("Applications","shell")
        msg("Applications","git")
        msg("Applications","npm")
        msg("Applications","yarn")
        msg("Applications","docker")

    # set proxy vars
    proxy=set_proxy(http_proxy =args.proxy      ,http_port =args.port      ,http_username =args.username      ,http_password =args.password,
                    https_proxy=args.https_proxy,https_port=args.https_port,https_username=args.https_username,https_password=args.https_password,
                    noproxy=args.no_proxy,dont_set_use=False)
    updates=[]
    if True == args.all or True == args.docker:
        msg('Status','docker  updated')
        apps['docker']=proxy
        config_changed=True
    if True == args.all or True == args.git:
        msg('Status','git     updated')
        apps['git']=proxy
        config_changed=True
    if True == args.all or True == args.npm:
        msg('Status','npm     updated')
        apps['npm']=proxy
        config_changed=True
    if True == args.all or True == args.yarn:
        msg('Status','yarn    updated')
        apps['yarn']=proxy
        config_changed=True
    if True == args.all or True == args.shell:
        msg('Status','shell   updated')
        apps['shell']=proxy
        config_changed=True

    # update use proxy per app
    if False !=  args.remove:
        if None == args.remove or args.remove=='docker':
            msg('Status','docker proxy is off')
            apps['docker']['use_proxy']=False
            config_changed=True
        if None == args.remove or args.remove=='npm':
            msg('Status','npm    proxy is off')
            apps['npm']['use_proxy']=False
            config_changed=True
        if None == args.remove or args.remove=='yarn':
            msg('Status','yarn   proxy is off')
            apps['yarn']['use_proxy']=False
            config_changed=True
        if None == args.remove or args.remove=='git':
            msg('Status','git    proxy is off')
            apps['git']['use_proxy']=False
            config_changed=True
        if None == args.remove or args.remove=='shell':
            msg('Status','shell  proxy is off')
            apps['shell']['use_proxy']=False
            config_changed=True

    
    if True == config_changed:
        msg('Status','Saving')
        save_config()


    if True == args.config:
        print_config('docker')
        print_config('npm')
        print_config('yarn')
        print_config('git')
        print_config('shell')
        
    
    if False == is_docker:
        # cant configure a docker inside a docker
        if True == args.all or True == args.docker:
            configure_docker()
    
    if True == args.all or True == args.git:
        configure_git()
    if True == args.all or True == args.npm:
        configure_npm()
    if True == args.all or True == args.yarn:
        configure_yarn()
    if True == args.all or True == args.shell:
        configure_shell()
