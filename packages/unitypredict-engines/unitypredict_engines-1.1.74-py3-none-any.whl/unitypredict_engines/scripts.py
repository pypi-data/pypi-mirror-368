import sys, os, shutil
from .unitypredictcli import UnityPredictCli
from .unitypredictUtils import ReturnValues as Ret
import argparse

def main():
    cliExec = "UnityPredict SDK"
    parser = argparse.ArgumentParser(
            description="Welcome to {}".format(cliExec)
    )
   
    parser.add_argument("--configure", action="store_true", help="unitypredict --configure")
    parser.add_argument("--profile", default="default", help="""unitypredict <options> --profile <profileName>""")
    parser.add_argument("--list_profiles", action="store_true", help="unitypredict --list_profiles")
    parser.add_argument("--engine", action="store_true", help="unitypredict --engine <options>")
    parser.add_argument("--create", default=None, help="""unitypredict --engine --create <EngineName>""")
    parser.add_argument("--remove", default=None, help="""unitypredict --engine --remove <EngineName>""")
    parser.add_argument("--run", action="store_true", help="""unitypredict --engine --run""")
    parser.add_argument("--deploy", action="store_true", help="""unitypredict --engine --deploy""")
    parser.add_argument("--forceDeploy", action="store_true", help="""unitypredict --engine --deploy --forceDeploy""")
    parser.add_argument("--delete", action="store_true", help="""unitypredict --engine --delete""")
    parser.add_argument("--uploadTimeout", type=int, default=600, help="""unitypredict --engine --deploy --uploadTimeout <TimeoutInSeconds (default: %(default)s)>""")
    parser.add_argument("--deployTimeout", type=int, default=600, help="""unitypredict --engine --deploy --deployTimeout <TimeoutInSeconds (default: %(default)s)>""")
    parser.add_argument("--getLastDeployLogs", action="store_true", help="""unitypredict --engine --getLastDeployLogs""")
    parser.add_argument("--pull", action="store_true", help="""unitypredict --engine --pull""")
    parser.add_argument("-y","--yes", action="store_true", help="""unitypredict <options> -y / unitypredict <options> --yes""")
    parser.add_argument("--env", default="prod", help=argparse.SUPPRESS)
    parser.add_argument("--verbose", action="store_true", help=argparse.SUPPRESS)


    args = parser.parse_args()

    num_args = len(sys.argv) - 1
    
    if (num_args == 0):
        parser.print_help()
        sys.exit(0)

    cliDriver = UnityPredictCli(uptVerbose=args.verbose)

    if args.configure:
        inputApiKey = input("Enter your UnityPredict account API Key: ")
        inputApiKey = inputApiKey.strip()
        ret = cliDriver.configureCredentials(uptApiKey=inputApiKey, uptProfile=args.profile)
        if ret == Ret.CRED_CREATE_SUCCESS:
            print(f"API Key for {args.profile} profile added successfully!")
        sys.exit(0)

    if args.list_profiles:
        cliDriver.showProfiles()
        sys.exit(0)

    if args.engine:
        
        if args.create != None:
            print (f"Creating Engine {args.create} ...")
            ret = cliDriver.createEngine(engineName=args.create, uptProfile=args.profile)
            if ret == Ret.ENGINE_CREATE_ERROR:
                cliDriver.removeEngine(engineName=args.create, uptProfile=args.profile)
                print (f"Removing Engine {args.create} due to Engine Creation errors!")
            else:
                print (f"Created Engine {args.create} Successfully!")
            sys.exit(0)

        elif args.remove != None:
            print (f"Removing Engine {args.remove} ...")
            ret = cliDriver.removeEngine(engineName=args.remove, uptProfile=args.profile)
            if ret == Ret.ENGINE_REMOVE_SUCCESS:
                print(f"Removed the engine {args.remove} Successfully!")
            elif ret == Ret.ENGINE_REMOVE_ERROR:
                print(f"Engine {args.remove} not detected!")
            sys.exit(0)
        
        elif args.run:

            # Change to parent dir for proper engine validation in local system
            engineDir = os.getcwd()
            engineName = os.path.basename(engineDir)
            engineParent = os.path.dirname(engineDir)

            os.chdir(engineParent)

            print (f"Run engine: {engineName} ...")
            cliDriver.runEngine(engineName=engineName, uptProfile=args.profile)
            
            os.chdir(engineDir)
            sys.exit(0)
        
        elif args.pull:
            engineDir = os.getcwd()
            engineName = os.path.basename(engineDir)
            engineParent = os.path.dirname(engineDir)

            os.chdir(engineParent)

            print (f"Pulling {engineName} ... ")
            print (f"Warning: This will overwrite the current engine {engineName} components with the latest version from UnityPredict!")
            if not args.yes:
                cont = input("Do you want to continue? ([y]/n): ")
                if cont.casefold() == "n":
                    os.chdir(engineDir)
                    sys.exit(0)

            ret = cliDriver.pullDeployedEngine(engineName=engineName, uptEnv=args.env, uptProfile=args.profile)
            if ret == Ret.UPT_ENGINE_PULL_ERROR:
                print (f"Error in pulling engine {engineName} from UnityPredict!")
            else:
                print (f"Pulled engine {engineName} from UnityPredict Successfully!")

            os.chdir(engineDir)
            sys.exit(0)
        
        elif args.deploy:

            # Change to parent dir for proper engine validation in local system
            engineDir = os.getcwd()
            engineName = os.path.basename(engineDir)
            engineParent = os.path.dirname(engineDir)

            os.chdir(engineParent)

            print (f"Deploying {engineName} ... ")
            cliDriver.setUptUploadTimeout(uploadTimeout=args.uploadTimeout)
            cliDriver.setUptDeployTimeout(deployTimeout=args.deployTimeout)
            cliDriver.setUptForceDeploy(forceDeploy=args.forceDeploy)
            ret = cliDriver.deployEngine(engineName=engineName, uptEnv=args.env, uptProfile=args.profile)
            if ret == Ret.ENGINE_DEPLOY_ERROR:
                print (f"Error in deploying Engine {engineName}!")
            else:
                print (f"Deployed Engine {engineName} on UnityPredict Successfully!")
            
            print (f"\nTo get detailed deploy logs, please run the following command:")
            print (f"unitypredict --engine --getLastDeployLogs \n")
            os.chdir(engineDir)

            sys.exit(0)

        elif args.getLastDeployLogs:
            engineDir = os.getcwd()
            engineName = os.path.basename(engineDir)
            engineParent = os.path.dirname(engineDir)

            os.chdir(engineParent)

            print (f"Getting Last Deploy Logs for {engineName} ... ")
            cliDriver.getLastDeployLogs(engineName=engineName, uptEnv=args.env, uptProfile=args.profile)
            sys.exit(0)
        
        elif args.delete:

            # Change to parent dir for proper engine validation in local system
            engineDir = os.getcwd()
            engineName = os.path.basename(engineDir)
            engineParent = os.path.dirname(engineDir)

            os.chdir(engineParent)

            print (f"Deleting {engineName} ... ")
            ret = cliDriver.deleteDeployedEngine(engineName=engineName, uptEnv=args.env, uptProfile=args.profile)
            if ret == Ret.UPT_ENGINE_DELETE_ERROR:
                print (f"Error in deleting Engine {engineName} on UnityPredict")
            else:
                print (f"Deleted Engine {engineName} on UnityPredict Successfully!")
            os.chdir(engineDir)
            sys.exit(0)

        else:
            print ("Incomplete arguements present. Please check the help section for the usage")
            parser.print_help()
        sys.exit(0)
    


