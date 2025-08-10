BUILD = """
#!/bin/bash

docker-compose build --force-rm
docker-compose pull
"""

DASHBOARD_AUTH = """
{ "dcm-processor": "dcm-processor" }
"""

SETTINGS = """
{
  "fullTags": true,
  "headerFields": ["SeriesInstanceUID", "ImagePositionPatient", "ImageOrientationPatient", "PerformedProcedureStepDescription", "seriesId", "dcmpath", "SeriesDescription", "ContrastBolusAgent", "Modality", "ImageType", "PatientID", "SeriesNumber", "StudyDate", "ImageComments", "BodyPartExamined"],
  "preServices": [
    {
      "jobName": "dicomAnonymizer",
      "worker": "base.DicomAnonymizerService.worker",
      "callback": "base.dicomAnonymizer",
      "dependsOn": null,
      "channel": "default",
      "timeout": "1h",
      "params": {
        "clean": true,
        "fhir": {
          "interface_url": "",
          "auth_server_url": "",
          "client_id": "",
          "client_secret": "",
          "identifier_system": ""
        }
      },
      "sortPosition": 0,
      "description": "Dicom Anonymizer Service"
    }
  ],
  "postServices":[
    {
      "jobName": "storageManager",
      "worker": "base.storageManager.worker",
      "callback": "base.storageManager",
      "dependsOn": null,
      "channel": "default",
      "timeout": "1h",
      "params": {
        "store_data": false
      },
      "sortPosition": 0,
      "description": "Storage Service"
    },
    {
      "jobName": "systemClearner",
      "worker": "base.systemcleaner.worker",
      "callback": "base.systemcleaner",
      "dependsOn": "storageManager",
      "channel": "default",
      "timeout": "1h",
      "params": {},
      "sortPosition": 1,
      "description": "System Cleaning Service"
    }
  ]
}
"""

CLEAN = """
#!/bin/bash

docker-compose down

SCRIPT=$(readlink -f "$0")
BASEDIR=$(dirname "$SCRIPT")

for i in $(echo $BASEDIR | tr "/" "\n")
do
  BASE="${i}"
done

filter="${BASE}_*:*"
docker rmi -f $(docker images --filter=reference="$filter" -q)

docker volume rm "${BASE}_mongo-data"
docker volume rm "${BASE}_orthanc-db"
docker volume rm "${BASE}_orthanc-dblight"
"""

BUILD_VOLUMES = """
#!/bin/bash
set -o allexport; source .env; set +o allexport

[ -z "$BASEDIR" ] && echo "set BASEDIR variable in the .env file" && exit 1
[ -z "$MODULES" ] && echo "set MODULES variable in the .env file" && exit 1
[ -z "$REGISTRY" ] && echo "set REGISTRY variable in the .env file" && exit 1
[ -z "$DATA" ] && echo "set DATA variable in the .env file" && exit 1
[ -z "$LOGS" ] && echo "set  variable in the .env file" && exit 1

mkdir -p "$BASEDIR/$MODULES"
mkdir -p "$BASEDIR/$REGISTRY"
mkdir -p "$BASEDIR/$DATA"
mkdir -p "$BASEDIR/$LOGS"
"""

RUN = """
#!/bin/bash

docker-compose down

docker-compose up -d orthanc scheduler

sleep 5

if [ -z "$1" ]
then
  docker-compose up -d
else
  docker-compose up $1 -d
fi
"""

REBUILD = """
#!/bin/bash

docker-compose stop $1
docker-compose rm $1


SCRIPT=$(readlink -f "$0")
BASEDIR=$(dirname "$SCRIPT")

for i in $(echo $BASEDIR | tr "/" "\n")
do
  BASE="${i}"  
done

docker rmi "${BASE}_$1"

docker-compose build $1

docker-compose up -d $1
"""

STOP = """
#!/bin/bash

docker-compose down
"""

INIT = """
#!/bin/bash

bash service.sh install base -p ./services/base
bash service.sh install dcm2nii -p ./services/dcm2nii

"""

SERVICE = """
#!/bin/bash

set -o allexport; source .env; set +o allexport

compose="docker-compose -f docker-compose.yml"

usage()
{
  echo "Usage: $0 [-h] [action] [servicename] [ -p SERVICE_PATH ] [ -b BACKUP_PATH  ]"
  echo "actions: [install | remove | backup]"
  echo "-h      To show this help message"
  echo "-p      Path to the folder where the service data is. this is a directory with two sub-directories [registry and module]"
  echo "-b      Path to the folder where the service backup will be place. supported by [remove and backup] actions"
  exit 2
}

set_variable()
{
  local varname=$1
  shift
  if [ -z "${!varname}" ]; then
    eval "$varname=\"$@\""
  else
    echo "Error: $varname already set"
    usage
  fi
}

valid_action_type()
{
    case "$1" in
    "install"|"remove"|"backup")
        return 0;;
    *)
        echo "Action $1 is not supported"
        return 1;;
    esac
}

[ -z "$BASEDIR" ] && echo "set BASEDIR variable in the .env file" && exit 1
[ -z "$MODULES" ] && echo "set MODULES variable in the .env file" && exit 1
[ -z "$REGISTRY" ] && echo "set REGISTRY variable in the .env file" && exit 1

unset ACTION SERVICENAME SERVICEPATH BACKUPPATH

if ! valid_action_type "$1"; then
    usage
    exit 1
fi

ACTION=$1
SERVICENAME=$2
shift 2

[ -z "$SERVICENAME" ] && usage && exit 1

[[ $SERVICENAME == -* ]] && usage && exit 1


# Install
if [ $ACTION = "install" ]
then

  while getopts ':p:?h:' c; do
    case $c in
      p) set_variable SERVICEPATH $OPTARG ;;
      h|?) usage ;;
    esac
  done

  if [ -z "$SERVICEPATH" ]
  then
    read -p "Enter Service Path :" SERVICEPATH
  fi

  echo "stopping containers..."
  # bash stop.sh
  if [ -d "$BASEDIR/$MODULES/$SERVICENAME" ]
  then
    echo "removing existing service module entry..."
    rm -rf "$BASEDIR/$MODULES/$SERVICENAME"
  fi

  if [ -d "$BASEDIR/$REGISTRY/$SERVICENAME" ]
  then
    echo "removing existing service registry entry..."
    rm -rf "$BASEDIR/$REGISTRY/$SERVICENAME"
  fi

  echo "copying module folder..."
  cp -r "$SERVICEPATH/module" "$BASEDIR/$MODULES/$SERVICENAME"
  echo "copying registry folder..."
  cp -r "$SERVICEPATH/registry" "$BASEDIR/$REGISTRY/$SERVICENAME"
  echo "starting workers..."
  # bash run.sh
fi



# Backup
if [ $ACTION = "backup" ]
then

  while getopts ':b:?h:' c; do
    case $c in
      b) set_variable BACKUPPATH $OPTARG ;;
      h|?) usage ;;
    esac
  done

  if [ -z "$BACKUPPATH" ]
  then
    read -p "Enter Backup Path :" SERVICEPATH
  fi

  mkdir -p "$BACKUPPATH/$SERVICENAME"
  echo "Copying registry entry"
  cp -r "${BASEDIR}${REGISTRY}/$SERVICENAME" "$BACKUPPATH/$SERVICENAME/registry"
  echo "Copying modules entry"
  cp -r "${BASEDIR}${MODULES}/$SERVICENAME" "$BACKUPPATH/$SERVICENAME/module"
fi




# Remove
if [ $ACTION = "remove" ]
then

  while getopts ':b:?h:' c; do
    case $c in
      b) set_variable BACKUPPATH $OPTARG ;;
      h|?) usage ;;
    esac
  done

  if [ -z "$BACKUPPATH" ]
  then
    echo "removing registry entry"
    rm -rf "$BASEDIR/$REGISTRY/$SERVICENAME"
    echo "removing modules entry"
    rm -rf "$BASEDIR/$MODULES/$SERVICENAME"
  else
    mkdir -p "$BACKUPPATH/$SERVICENAME"
    echo "Moving registry entry"
    mv "$BASEDIR/$REGISTRY/$SERVICENAME" "$BACKUPPATH/$SERVICENAME/registry"
    echo "Moving modules entry"
    mv "$BASEDIR/$MODULES/$SERVICENAME" "$BACKUPPATH/$SERVICENAME/module"
  fi

fi
"""

ENV = """
BASEDIR=./mapped_folders
MODULES=/modules
DATA=/data
REGISTRY=/registry
LOGS=/logs
DASHBOARD=/dashboard

SCHEDULER_HOST=http://scheduler
SCHEDULER_PORT=5000
SCHEDULER_SETTINGS=/settings.json

ORTHANC_REST_USERNAME=dcm-processor
ORTHANC_REST_PASSWORD=dcm-processor
ORTHANC_REST_URL=http://orthanc:8042
ORTHANC_DEFUALT_STORE=pac
ORTHANC_LOGLEVEL=2
CLEAN_ORTHANC=0

ORTHANC_DICOM_PORT=4242
ORTHANC_BROWSER_PORT=8042
DASHBOARD_PORT=5000
SUPPORTED_MODALITY=CT,MR
ACCEPTED_FILES=primary,original
JUNK_FILES=derived,projection,sbi,surv,bersi,racker,ssde,results,mip,mono,spectal,scout,localizer,lokali,konturen,sectrareconstruction,zeffect,iodoinekein,smartplan,doseinf
INSTANCE_REQUIRED_TAGS=SeriesInstanceUID,InstanceNumber,ImageOrientationPatient,ImagePositionPatient
NO_PROXY=scheduler,orthanc,mongo,localhost,127.0.0.*

JOBS_CONNECTION=mongodb://mongo:27017/
JOBS_DBNAME=jobs
JOBS_COLNAME=jobs
DEFUALT_CHANNEL=default

IMAGE_VERSION=0.0.2
"""

DOCKER_COMPOSE = """
version: '3.7'

volumes:
  mongo-data:
    driver: local
  orthanc-db:
    driver: local
  orthanc-dblight:
    driver: local

services:
  mongo:
    image: mongo
    volumes:
      - mongo-data:/data/db
    expose:
      - "27017"

  worker:
    image: giesekow/dcm-processor-worker:${IMAGE_VERSION}
    depends_on:
      - mongo
    environment:
      JOBS_CONNECTION: ${JOBS_CONNECTION}
      JOBS_DBNAME: ${JOBS_DBNAME}
      JOBS_COLNAME: ${JOBS_COLNAME}
      ORTHANC_REST_USERNAME: ${ORTHANC_REST_USERNAME}
      ORTHANC_REST_PASSWORD: ${ORTHANC_REST_PASSWORD}
      ORTHANC_REST_URL: ${ORTHANC_REST_URL}
      ORTHANC_DEFUALT_STORE: ${ORTHANC_DEFUALT_STORE}
      CLEAN_ORTHANC: ${CLEAN_ORTHANC}
      DATA: /data
      MODULES: /modules
      LOGS: /logs
      NO_PROXY: ${NO_PROXY}
      no_proxy: ${NO_PROXY}
    volumes:
      - ${BASEDIR}${MODULES}:/modules:cached
      - ${BASEDIR}${DATA}:/data:rw
      - ${BASEDIR}${LOGS}:/logs:rw

  scheduler:
    image: giesekow/dcm-processor-scheduler:${IMAGE_VERSION}
    depends_on:
      - mongo
    expose:
      - "5000"
    environment:
      JOBS_CONNECTION: ${JOBS_CONNECTION}
      JOBS_DBNAME: ${JOBS_DBNAME}
      JOBS_COLNAME: ${JOBS_COLNAME}
      DATA: /data
      REGISTRY: /registry
      LOGS: /logs
      DEFUALT_CHANNEL: ${DEFUALT_CHANNEL}
      SETTINGS: ${SCHEDULER_SETTINGS}
      NO_PROXY: ${NO_PROXY}
      no_proxy: ${NO_PROXY}
    volumes:
      - ${BASEDIR}${REGISTRY}:/registry:cached
      - ${BASEDIR}${DATA}:/data:rw
      - ${BASEDIR}${LOGS}:/logs:rw
      - ./settings.json:/settings.json
  
  dashboard:
    image: giesekow/mongo-qas-dashboard:latest
    expose:
      - "5000"
    ports:
      - ${DASHBOARD_PORT}:5000
    depends_on:
      - mongo
    environment:
      DB_CONNECTION: ${JOBS_CONNECTION}
      DB_NAME: ${JOBS_DBNAME}
      COL_NAME: ${JOBS_COLNAME}
      NO_PROXY: ${NO_PROXY}
      no_proxy: ${NO_PROXY}
    volumes:
      - ${BASEDIR}${DASHBOARD}:/data

  orthanc:
    image: giesekow/dcm-processor-orthanc:${IMAGE_VERSION}
    command: /run/secrets/  # Path to the configuration files (stored as secrets)
    expose:
      - "4242"
      - "8042"
    ports:
      - ${ORTHANC_DICOM_PORT}:4242
      - ${ORTHANC_BROWSER_PORT}:8042
    volumes:
      - orthanc-db:/var/lib/orthanc/db
      - orthanc-dblight:/var/lib/orthanc/dblight
      - ${BASEDIR}${DATA}:/data:rw
      - ${BASEDIR}${LOGS}:/logs:rw
    secrets:
      - orthanc.json
    environment:
      SCHEDULER_HOST: ${SCHEDULER_HOST}
      SCHEDULER_PORT: ${SCHEDULER_PORT}
      SUPPORTED_MODALITY: ${SUPPORTED_MODALITY}
      JUNK_FILES: ${JUNK_FILES}
      ACCEPTED_FILES: ${ACCEPTED_FILES}
      INSTANCE_REQUIRED_TAGS: ${INSTANCE_REQUIRED_TAGS}
      NO_PROXY: ${NO_PROXY}
      no_proxy: ${NO_PROXY}
      DATA: /data
      LOGS: /logs
      LOGLEVEL: ${ORTHANC_LOGLEVEL}

secrets:
  orthanc.json:
    file: ./orthanc.json
"""

ORTHANC = """
{
  /**
   * General configuration of Orthanc
   **/

  // The logical name of this instance of Orthanc. This one is
  // displayed in Orthanc Explorer and at the URI "/system".
  "Name": "dcm-processor",

  // Path to the directory that holds the heavyweight files (i.e. the
  // raw DICOM instances). Backslashes must be either escaped by
  // doubling them, or replaced by forward slashes "/".
  "StorageDirectory": "/var/lib/orthanc/db",

  // Path to the directory that holds the SQLite index (if unset, the
  // value of StorageDirectory is used). This index could be stored on
  // a RAM-drive or a SSD device for performance reasons.
  "IndexDirectory": "/var/lib/orthanc/dblight",

  // Path to the directory where Orthanc stores its large temporary
  // files. The content of this folder can be safely deleted if
  // Orthanc once stopped. The folder must exist. The corresponding
  // filesystem must be properly sized, given that for instance a ZIP
  // archive of DICOM images created by a job can weight several GBs,
  // and that there might be up to "min(JobsHistorySize,
  // MediaArchiveSize)" archives to be stored simultaneously. If not
  // set, Orthanc will use the default temporary folder of the
  // operating system (such as "/tmp/" on UNIX-like systems, or
  // "C:/Temp" on Microsoft Windows).
  "TemporaryDirectory": "/tmp",

  // Enable the transparent compression of the DICOM instances
  "StorageCompression": false,

  // Maximum size of the storage in MB (a value of "0" indicates no
  // limit on the storage size)
  "MaximumStorageSize": 0,

  // Maximum number of patients that can be stored at a given time
  // in the storage (a value of "0" indicates no limit on the number
  // of patients)
  "MaximumPatientCount": 0,

  // List of paths to the custom Lua scripts that are to be loaded
  // into this instance of Orthanc
  "LuaScripts": [
    "/scripts/dicom_listener.lua"
  ],

  // List of paths to the plugins that are to be loaded into this
  // instance of Orthanc (e.g. "./libPluginTest.so" for Linux, or
  // "./PluginTest.dll" for Windows). These paths can refer to
  // folders, in which case they will be scanned non-recursively to
  // find shared libraries. Backslashes must be either escaped by
  // doubling them, or replaced by forward slashes "/".
  "Plugins": [
    "/usr/share/orthanc/plugins", "/usr/local/share/orthanc/plugins"
  ],

  // Maximum number of processing jobs that are simultaneously running
  // at any given time. A value of "0" indicates to use all the
  // available CPU logical cores. To emulate Orthanc <= 1.3.2, set
  // this value to "1".
  "ConcurrentJobs": 2,


  /**
   * Configuration of the HTTP server
   **/

  // Enable the HTTP server. If this parameter is set to "false",
  // Orthanc acts as a pure DICOM server. The REST API and Orthanc
  // Explorer will not be available.
  "HttpServerEnabled": true,

  // HTTP port for the REST services and for the GUI
  "HttpPort": 8042,

  // When the following option is "true", if an error is encountered
  // while calling the REST API, a JSON message describing the error
  // is put in the HTTP answer. This feature can be disabled if the
  // HTTP client does not properly handles such answers.
  "HttpDescribeErrors": true,

  // Enable HTTP compression to improve network bandwidth utilization,
  // at the expense of more computations on the server. Orthanc
  // supports the "gzip" and "deflate" HTTP encodings.
  "HttpCompressionEnabled": true,



  /**
   * Configuration of the DICOM server
   **/

  // Enable the DICOM server. If this parameter is set to "false",
  // Orthanc acts as a pure REST server. It will not be possible to
  // receive files or to do query/retrieve through the DICOM protocol.
  "DicomServerEnabled": true,

  // The DICOM Application Entity Title (cannot be longer than 16
  // characters)
  "DicomAet": "DCM-PROCESSOR",

  // Check whether the called AET corresponds to the AET of Orthanc
  // during an incoming DICOM SCU request
  "DicomCheckCalledAet": false,

  // The DICOM port
  "DicomPort": 4242,

  // The default encoding that is assumed for DICOM files without
  // "SpecificCharacterSet" DICOM tag, and that is used when answering
  // C-Find requests (including worklists). The allowed values are
  // "Ascii", "Utf8", "Latin1", "Latin2", "Latin3", "Latin4",
  // "Latin5", "Cyrillic", "Windows1251", "Arabic", "Greek", "Hebrew",
  // "Thai", "Japanese", "Chinese", "JapaneseKanji", "Korean", and
  // "SimplifiedChinese".
  "DefaultEncoding": "Latin1",

  // The transfer syntaxes that are accepted by Orthanc C-Store SCP
  "DeflatedTransferSyntaxAccepted": true,
  "JpegTransferSyntaxAccepted": true,
  "Jpeg2000TransferSyntaxAccepted": true,
  "JpegLosslessTransferSyntaxAccepted": true,
  "JpipTransferSyntaxAccepted": true,
  "Mpeg2TransferSyntaxAccepted": true,
  "RleTransferSyntaxAccepted": true,
  "Mpeg4TransferSyntaxAccepted": true, // New in Orthanc 1.6.0

  // Whether Orthanc accepts to act as C-Store SCP for unknown storage
  // SOP classes (aka. "promiscuous mode")
  "UnknownSopClassAccepted": false,

  // Set the timeout (in seconds) after which the DICOM associations
  // are closed by the Orthanc SCP (server) if no further DIMSE
  // command is received from the SCU (client).
  "DicomScpTimeout": 30,



  /**
   * Security-related options for the HTTP server
   **/

  // Whether remote hosts can connect to the HTTP server
  "RemoteAccessAllowed": true,

  // Whether or not SSL is enabled
  "SslEnabled": false,

  // Path to the SSL certificate in the PEM format (meaningful only if
  // SSL is enabled)
  "SslCertificate": "certificate.pem",

  // Whether or not the password protection is enabled (using HTTP
  // basic access authentication). Starting with Orthanc 1.5.8, if
  // "AuthenticationEnabled" is not explicitly set, authentication is
  // enabled iff. remote access is allowed (i.e. the default value of
  // "AuthenticationEnabled" equals that of "RemoteAccessAllowed").
  /**
     "AuthenticationEnabled" : true,
   **/

  // The list of the registered users. Because Orthanc uses HTTP
  // Basic Authentication, the passwords are stored as plain text.
  "RegisteredUsers": {
    "dcm-processor": "dcm-processor"
  },



  /**
   * Network topology
   **/

  // The list of the known DICOM modalities
  "DicomModalities": {
    /**
     * Uncommenting the following line would enable Orthanc to
     * connect to an instance of the "storescp" open-source DICOM
     * store (shipped in the DCMTK distribution), as started by the
     * command line "storescp 2000". The first parameter is the
     * AET of the remote modality (cannot be longer than 16 
     * characters), the second one is the remote network address,
     * and the third one is the TCP port number corresponding
     * to the DICOM protocol on the remote modality (usually 104).
     **/
    "pacs": ["D_ANDUIN_NEURO", "10.32.17.10", 10007]

    /**
     * A fourth parameter is available to enable patches for
     * specific PACS manufacturers. The allowed values are currently:
     * - "Generic" (default value),
     * - "GenericNoWildcardInDates" (to replace "*" by "" in date fields 
     *   in outgoing C-Find requests originating from Orthanc),
     * - "GenericNoUniversalWildcard" (to replace "*" by "" in all fields
     *   in outgoing C-Find SCU requests originating from Orthanc),
     * - "StoreScp" (storescp tool from DCMTK),
     * - "Vitrea",
     * - "GE" (Enterprise Archive, MRI consoles and Advantage Workstation
     *   from GE Healthcare).
     *
     * This parameter is case-sensitive.
     **/
    // "vitrea" : [ "VITREA", "192.168.1.1", 104, "Vitrea" ]

    /**
     * By default, the Orthanc SCP accepts all DICOM commands (C-ECHO,
     * C-STORE, C-FIND, C-MOVE, and storage commitment) issued by the
     * registered remote SCU modalities. Starting with Orthanc 1.5.0,
     * it is possible to specify which DICOM commands are allowed,
     * separately for each remote modality, using the syntax
     * below. The "AllowEcho" (resp.  "AllowStore") option only has an
     * effect respectively if global option "DicomAlwaysAllowEcho"
     * (resp. "DicomAlwaysAllowStore") is set to false.
     **/
    //"untrusted" : {
    //  "AET" : "ORTHANC",
    //  "Port" : 104,
    //  "Host" : "127.0.0.1",
    //  "Manufacturer" : "Generic",
    //  "AllowEcho" : false,
    //  "AllowFind" : false,
    //  "AllowMove" : false,
    //  "AllowStore" : true,
    //  "AllowStorageCommitment" : false  // new in 1.6.0
    //}
  },

  // Whether to store the DICOM modalities in the Orthanc database
  // instead of in this configuration file (new in Orthanc 1.5.0)
  "DicomModalitiesInDatabase": false,

  // Whether the Orthanc SCP allows incoming C-Echo requests, even
  // from SCU modalities it does not know about (i.e. that are not
  // listed in the "DicomModalities" option above). Orthanc 1.3.0
  // is the only version to behave as if this argument was set to "false".
  "DicomAlwaysAllowEcho": true,

  // Whether the Orthanc SCP allows incoming C-Store requests, even
  // from SCU modalities it does not know about (i.e. that are not
  // listed in the "DicomModalities" option above)
  "DicomAlwaysAllowStore": true,

  // Whether Orthanc checks the IP/hostname address of the remote
  // modality initiating a DICOM connection (as listed in the
  // "DicomModalities" option above). If this option is set to
  // "false", Orthanc only checks the AET of the remote modality.
  "DicomCheckModalityHost": false,

  // The timeout (in seconds) after which the DICOM associations are
  // considered as closed by the Orthanc SCU (client) if the remote
  // DICOM SCP (server) does not answer.
  "DicomScuTimeout": 10,

  // The list of the known Orthanc peers
  "OrthancPeers": {
    /**
     * Each line gives the base URL of an Orthanc peer, possibly
     * followed by the username/password pair (if the password
     * protection is enabled on the peer).
     **/
    // "peer"  : [ "http://127.0.0.1:8043/", "alice", "alicePassword" ]
    // "peer2" : [ "http://127.0.0.1:8044/" ]

    /**
     * This is another, more advanced format to define Orthanc
     * peers. It notably allows to specify HTTP headers, a HTTPS
     * client certificate in the PEM format (as in the "--cert" option
     * of curl), or to enable PKCS#11 authentication for smart cards.
     **/
    // "peer" : {
    //   "Url" : "http://127.0.0.1:8043/",
    //   "Username" : "alice",
    //   "Password" : "alicePassword",
    //   "HttpHeaders" : { "Token" : "Hello world" },
    //   "CertificateFile" : "client.crt",
    //   "CertificateKeyFile" : "client.key",
    //   "CertificateKeyPassword" : "certpass",
    //   "Pkcs11" : false
    // }
  },

  // Whether to store the Orthanc peers in the Orthanc database
  // instead of in this configuration file (new in Orthanc 1.5.0)
  "OrthancPeersInDatabase": false,

  // Parameters of the HTTP proxy to be used by Orthanc. If set to the
  // empty string, no HTTP proxy is used. For instance:
  //   "HttpProxy" : "192.168.0.1:3128"
  //   "HttpProxy" : "proxyUser:proxyPassword@192.168.0.1:3128"
  "HttpProxy": "",

  // If set to "true", debug messages from libcurl will be issued
  // whenever Orthanc makes an outgoing HTTP request. This is notably
  // useful to debug HTTPS-related problems.
  "HttpVerbose": false,

  // Set the timeout for HTTP requests issued by Orthanc (in seconds).
  "HttpTimeout": 60,

  // Enable the verification of the peers during HTTPS requests. This
  // option must be set to "false" if using self-signed certificates.
  // Pay attention that setting this option to "false" results in
  // security risks!
  // Reference: http://curl.haxx.se/docs/sslcerts.html
  "HttpsVerifyPeers": true,

  // Path to the CA (certification authority) certificates to validate
  // peers in HTTPS requests. From curl documentation ("--cacert"
  // option): "Tells curl to use the specified certificate file to
  // verify the peers. The file may contain multiple CA
  // certificates. The certificate(s) must be in PEM format." On
  // Debian-based systems, this option can be set to
  // "/etc/ssl/certs/ca-certificates.crt"
  "HttpsCACertificates": "",



  /**
   * Advanced options
   **/

  // Dictionary of symbolic names for the user-defined metadata. Each
  // entry must map an unique string to an unique number between 1024
  // and 65535. Reserved values:
  //  - The Orthanc whole-slide imaging plugin uses metadata 4200
  "UserMetadata": {
    // "Sample" : 1024
  },

  // Dictionary of symbolic names for the user-defined types of
  // attached files. Each entry must map an unique string to an unique
  // number between 1024 and 65535. Optionally, a second argument can
  // provided to specify a MIME content type for the attachment.
  "UserContentType": {
    // "sample" : 1024
    // "sample2" : [ 1025, "application/pdf" ]
  },

  // Number of seconds without receiving any instance before a
  // patient, a study or a series is considered as stable.
  "StableAge": 60,

  // By default, Orthanc compares AET (Application Entity Titles) in a
  // case-insensitive way. Setting this option to "true" will enable
  // case-sensitive matching.
  "StrictAetComparison": false,

  // When the following option is "true", the MD5 of the DICOM files
  // will be computed and stored in the Orthanc database. This
  // information can be used to detect disk corruption, at the price
  // of a small performance overhead.
  "StoreMD5ForAttachments": true,

  // The maximum number of results for a single C-FIND request at the
  // Patient, Study or Series level. Setting this option to "0" means
  // no limit.
  "LimitFindResults": 0,

  // The maximum number of results for a single C-FIND request at the
  // Instance level. Setting this option to "0" means no limit.
  "LimitFindInstances": 0,

  // The maximum number of active jobs in the Orthanc scheduler. When
  // this limit is reached, the addition of new jobs is blocked until
  // some job finishes.
  "LimitJobs": 10,

  // If this option is set to "true" (default behavior until Orthanc
  // 1.3.2), Orthanc will log the resources that are exported to other
  // DICOM modalities or Orthanc peers, inside the URI
  // "/exports". Setting this option to "false" is useful to prevent
  // the index to grow indefinitely in auto-routing tasks (this is the
  // default behavior since Orthanc 1.4.0).
  "LogExportedResources": false,

  // Enable or disable HTTP Keep-Alive (persistent HTTP
  // connections). Setting this option to "true" prevents Orthanc
  // issue #32 ("HttpServer does not support multiple HTTP requests in
  // the same TCP stream"), but can possibly slow down HTTP clients
  // that do not support persistent connections. The default behavior
  // used to be "false" in Orthanc <= 1.5.1. Setting this option to
  // "false" is also recommended if Orthanc is compiled against
  // Mongoose.
  "KeepAlive": true,

  // Enable or disable Nagle's algorithm. Only taken into
  // consideration if Orthanc is compiled to use CivetWeb. Experiments
  // show that best performance can be obtained by setting both
  // "KeepAlive" and "TcpNoDelay" to "true". Beware however of
  // caveats: https://eklitzke.org/the-caveats-of-tcp-nodelay
  "TcpNoDelay": true,

  // Number of threads that are used by the embedded HTTP server.
  "HttpThreadsCount": 50,

  // If this option is set to "false", Orthanc will run in index-only
  // mode. The DICOM files will not be stored on the drive. Note that
  // this option might prevent the upgrade to newer versions of Orthanc.
  "StoreDicom": true,

  // DICOM associations initiated by Lua scripts are kept open as long
  // as new DICOM commands are issued. This option sets the number of
  // seconds of inactivity to wait before automatically closing a
  // DICOM association used by Lua. If set to 0, the connection is
  // closed immediately. This option is only used in Lua scripts.
  "DicomAssociationCloseDelay": 5,

  // Maximum number of query/retrieve DICOM requests that are
  // maintained by Orthanc. The least recently used requests get
  // deleted as new requests are issued.
  "QueryRetrieveSize": 100,

  // When handling a C-Find SCP request, setting this flag to "true"
  // will enable case-sensitive match for PN value representation
  // (such as PatientName). By default, the search is
  // case-insensitive, which does not follow the DICOM standard.
  "CaseSensitivePN": false,

  // Configure PKCS#11 to use hardware security modules (HSM) and
  // smart cards when carrying on HTTPS client authentication.
  /**
     "Pkcs11" : {
       "Module" : "/usr/local/lib/libbeidpkcs11.so",
       "Module" : "C:/Windows/System32/beidpkcs11.dll",
       "Pin" : "1234",
       "Verbose" : true
     }
   **/

  // If set to "false", Orthanc will not load its default dictionary
  // of private tags. This might be necessary if you cannot import a
  // DICOM file encoded using the Implicit VR Endian transfer syntax,
  // and containing private tags: Such an import error might stem from
  // a bad dictionary. You can still list your private tags of
  // interest in the "Dictionary" configuration option below.
  "LoadPrivateDictionary": true,

  // Locale to be used by Orthanc. Currently, only used if comparing
  // strings in a case-insensitive way. It should be safe to keep this
  // value undefined, which lets Orthanc autodetect the suitable locale.
  // "Locale" : "en_US.UTF-8",

  // Register a new tag in the dictionary of DICOM tags that are known
  // to Orthanc. Each line must contain the tag (formatted as 2
  // hexadecimal numbers), the value representation (2 upcase
  // characters), a nickname for the tag, possibly the minimum
  // multiplicity (> 0 with defaults to 1), possibly the maximum
  // multiplicity (0 means arbitrary multiplicity, defaults to 1), and
  // possibly the Private Creator (for private tags).
  "Dictionary": {
    // "0014,1020" : [ "DA", "ValidationExpiryDate", 1, 1 ]
    // "00e1,10c2" : [ "UI", "PET-CT Multi Modality Name", 1, 1, "ELSCINT1" ]
    // "7053,1003" : [ "ST", "Original Image Filename", 1, 1, "Philips PET Private Group" ]
    // "2001,5f" : [ "SQ", "StackSequence", 1, 1, "Philips Imaging DD 001" ]
    "0405,0010": ["LO", "Private data element", 1, 1, "DCM-PROCESSOR"],
    "0405,1001": ["ST", "Action", 1, 1, "DCM-PROCESSOR"],
    "0405,1003": ["ST", "ActionType", 1, 1, "DCM-PROCESSOR"],
    "0405,1005": ["ST", "ActionSource", 1, 1, "DCM-PROCESSOR"],
    "0405,1007": ["ST", "ActionDestination", 1, 1, "DCM-PROCESSOR"],
    "0405,1009": ["ST", "ReferenceSeries", 1, 1, "DCM-PROCESSOR"],
    "0405,1011": ["ST", "DcmProcessorStatus", 1, 1, "DCM-PROCESSOR"]
  },

  // Whether to run DICOM C-Move operations synchronously. If set to
  // "false" (asynchronous mode), each incoming C-Move request results
  // in the creation of a new background job. Up to Orthanc 1.3.2, the
  // implicit behavior was to use synchronous C-Move ("true"). Between
  // Orthanc 1.4.0 and 1.4.2, the default behavior was set to
  // asynchronous C-Move ("false"). Since Orthanc 1.5.0, the default
  // behavior is back to synchronous C-Move ("true", which ensures
  // backward compatibility with Orthanc <= 1.3.2).
  "SynchronousCMove": true,

  // Maximum number of completed jobs that are kept in memory. A
  // processing job is considered as complete once it is tagged as
  // "Success" or "Failure". Since Orthanc 1.5.0, a value of "0"
  // indicates to keep no job in memory (i.e. jobs are removed from
  // the history as soon as they are completed), which prevents the
  // use of some features of Orthanc (typically, synchronous mode in
  // REST API) and should be avoided for non-developers.
  "JobsHistorySize": 10,

  // Whether to save the jobs into the Orthanc database. If this
  // option is set to "true", the pending/running/completed jobs are
  // automatically reloaded from the database if Orthanc is stopped
  // then restarted (except if the "--no-jobs" command-line argument
  // is specified). This option should be set to "false" if multiple
  // Orthanc servers are using the same database (e.g. if PostgreSQL
  // or MariaDB/MySQL is used).
  "SaveJobs": true,

  // Specifies how Orthanc reacts when it receives a DICOM instance
  // whose SOPInstanceUID is already stored. If set to "true", the new
  // instance replaces the old one. If set to "false", the new
  // instance is discarded and the old one is kept. Up to Orthanc
  // 1.4.1, the implicit behavior corresponded to "false".
  "OverwriteInstances": true,

  // Maximum number of ZIP/media archives that are maintained by
  // Orthanc, as a response to the asynchronous creation of archives.
  // The least recently used archives get deleted as new archives are
  // generated. This option was introduced in Orthanc 1.5.0, and has
  // no effect on the synchronous generation of archives.
  "MediaArchiveSize": 1,

  // Performance setting to specify how Orthanc accesses the storage
  // area during C-FIND. Three modes are available: (1) "Always"
  // allows Orthanc to read the storage area as soon as it needs an
  // information that is not present in its database (slowest mode),
  // (2) "Never" prevents Orthanc from accessing the storage area, and
  // makes it uses exclusively its database (fastest mode), and (3)
  // "Answers" allows Orthanc to read the storage area to generate its
  // answers, but not to filter the DICOM resources (balance between
  // the two modes). By default, the mode is "Always", which
  // corresponds to the behavior of Orthanc <= 1.5.0.
  "StorageAccessOnFind": "Always",

  // Whether Orthanc monitors its metrics (new in Orthanc 1.5.4). If
  // set to "true", the metrics can be retrieved at
  // "/tools/metrics-prometheus" formetted using the Prometheus
  // text-based exposition format.
  "MetricsEnabled": true,

  // Whether calls to URI "/tools/execute-script" is enabled. Starting
  // with Orthanc 1.5.8, this URI is disabled by default for security.
  "ExecuteLuaEnabled": false,

  // Set the timeout for HTTP requests, in seconds. This corresponds
  // to option "request_timeout_ms" of Mongoose/Civetweb. It will set
  // the socket options "SO_RCVTIMEO" and "SO_SNDTIMEO" to the
  // specified value.
  "HttpRequestTimeout": 30,

  // Set the default private creator that is used by Orthanc when it
  // looks for a private tag in its dictionary (cf. "Dictionary"
  // option), or when it creates/modifies a DICOM file (new in Orthanc 1.6.0).
  "DefaultPrivateCreator": "",

  // Maximum number of storage commitment reports (i.e. received from
  // remote modalities) to be kept in memory (new in Orthanc 1.6.0).
  "StorageCommitmentReportsSize": 100
}
"""