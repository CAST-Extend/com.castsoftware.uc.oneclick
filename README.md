# What is OneClick
OneClick is an automation tool designed to perform a due diligence assessment from beginning to end for one or more applications in a project. This includes:

1. Code discovery
1. Run CAST MRI Analysis
1. Run CAST Highlight Analysis
1. Generate Due Diligence Assessment Report

# OneClick Installation
## Prerequisites

Running OneClick requires access to:
* AIP Console – version 1.28 or higher
* Highlight – version 5.4.70 or higher
* AIP Dashboard REST API – version 2.9.1 or higher
* Cast Storage System (CSS) – version 4 or higher
* Python – version 3.10

In addition, it requires the installation and location of CAST Imaging Console and Highlight automation tools. These tools are available either on the CAST Extend website or Highlight portal.

## Installation
1.  [Download Python \| Python.org](https://www.python.org/downloads/) (if not already installed).
    * The tool was tested using python version 3.10
    * When installing python be sure to check the “Add Python to Path option”

        ![Expected folder structure](https://raw.githubusercontent.com/CAST-Extend/com.castsoftware.uc.oneclick/main/media/bc9c224100a437083c551e4bfb2da76d.png)
        
2.  Download the OneClick extension from the CAST Extend web site.
3.  Expand the nugget file into a folder, using zip.
4.  Open a command prompt, hold down windows key and press r, then type cmd enter.
5.  Go to the folder containing the expanded nugget file.
6.  Type: install \<base folder location\>
    * The base folder location will hold all files used and/or created by the OneClick tool.
    * For more on this see the Environment section below.
# Command Line Arguments

OneClick has two types of arguments, config and run. The first is used to configure the global and/or project configuration files. The second to run discovery, analyses, and reporting.

```
oneClick config -b <base location> [-p <project name>] 
		or
oneClick run -b <base location> -p <project name>
```

# Global Configuration

Running oneClick requires access to the CAST Imaging Console tools, Highlight portal toolset, and Imaging Dashboard REST API. This information is stored in the OneClick global configuration file, *\<base folder location\>/.oneclick/config.json*. When a new project is created, the global configuration is included in the project configuration file. The following sections describes how to configure the global configuration file.

## Imaging Console

OneClick has been tested using both 1.x and 2.x Enterprise version of AIP Console. The AIP Console integration tools is used to access the Console which can be downloaded:

-   [Console Enterprise Edition](https://extend.castsoftware.com/#/extension?id=com.castsoftware.aip.console&version=1.28.2-funcrel)
-   [AIP Console integration tools](https://extend.castsoftware.com/#/extension?id=com.castsoftware.uc.aip.console.tools&version=1.0.1)

Make sure the integration tools and AIP Console version matches. After both are installed update the common configuration file:

```
oneClick config -b <base location> [-p <project name>] --consoleURL=http:\\<server>\ --consoleKey=<console-key> --consoleCLI=<console-integration-tool-location> --enable-security-assessment <true> --blueprint <true>
```

| Parameter                    | Description                                                                                      | Default Value                                                                                                                                        |
|------------------------------|--------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| --consoleURL                 | The URL of AIP Console                                                                           |                                                                                                                                                      |
| --consoleKey                 | The console key provides access to the AIP Console and is retrieved from the user profile.       | ![Graphical user interface, text, application, chat or text message Description automatically generated](https://raw.githubusercontent.com/CAST-Extend/com.castsoftware.uc.oneclick/main/media/f9d987571d6ba95cc1be2dce08915052.png) |
| --consoleCLI                 | The absolute location of the “aip-console-cli.jar” included with *AIP Console integration tools* |                                                                                                                                                      |
| --enable-security-assessment | This is a Boolean parameter, if set to true the analysis will be run with security turned on.    | True                                                                                                                                                 |
| --blueprint                  | This is a Boolean parameter, if set to true the analysis will be run in full blueprint mode.     | True                                                                                                                                                 |

## Highlight

To run Highlight scans and upload them to the portal, both the Agent and CLI tool must be installed. They can be downloaded from the Application Scans page in the Highlight portal. ![Graphical user interface, text, application, email Description automatically generated](m[edia](https://raw.githubusercontent.com/CAST-Extend/com.castsoftware.uc.oneclick/main/media/655e6bf3ea23051dcde0c76e0df1410b.png)

```
oneClick config -b <base location> [-p <project name>] --hlURL=<portal-url> --hlUser=<username> --hlPassword=<password> --hlInstance=<Instance-ID> --hlCLI=<CLI-location> --HLPerlInstallDir=<agent-location>/strawberry/perl> --HLAnalyzerDir=<agent-location>/perl
```

| Parameter        | Description                                              | Default Value |
|------------------|----------------------------------------------------------|---------------|
| --hlURL          | The Highlight portal URL hlUser User Id                  |               |
| --hlPassword     | Password                                                 |               |
| --hlCLI Absolute | folder location for the Highlight command line interface |               |
| --HLAgent        | Absolute folder location for the Highlight agent         |               |

## Dashboard Rest API

The AIP Rest API is part of the Health and Engineering Portal (HDED) installation and is used to generate the assessment report. There are two distinct portal versions Standalone and Integrated and OneClick will work with both. The OneClick configuration is as follows:

```
oneClick config -b <code location> [-p <project name>] --aipURL <URL> --aipUser <username> --aipPassword <password>
```

| Parameter     | Description               | Default Value |
|---------------|---------------------------|---------------|
| --aipURL      | The Imaging dashboard URL |               |
| --aipUser     | User Id                   | admin         |
| --aipPassword | Password                  | admin         |

## Other

```
oneClick config -b <code location> [-p <project name>] [--java_home <java>] --report_template <template> [cloc_version <cloc-1.96.exe>]
```

| Parameter       | Description                                                                                                                                                    | Default Value |
|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------|
| java_home       | Location of the java installation. This parameter can be omitted if the java bin folder is already part the system path.                                       |               |
| report_template | The absolute location of the assessment report template.                                                                                                       |               |
| cloc_version    | The cloc executable is located in the scripts folder and is set by default to cloc-1.96.exe. A new executable name can be added here to override this version. |               |

# Running the tool

## Creating a New Project

### Environment

The first step in creating a new project is to create a folder in the DELIVER folder. The folder name is used to identify the project, it is recommended that the name be self-descriptive. Under the project folder, one or more application folders should be created. As with the project, the application folder names are used to identify each application going forward. OneClick uses this folder structure to create the application project file and tracks all projects using this folder structure.

![Graphical user interface, application Description automatically generated](https://raw.githubusercontent.com/CAST-Extend/com.castsoftware.uc.oneclick/main/media/a8a164e65148353b0e8f8253f432fd80.png)

### Project Configuration

Projects are maintained using the DELIVER folder and a json file, found in the “.oneClick” folder. The project configuration file has the same name as the project and is maintained by OneClick. It is maintained by OneClick and should not be directly updated by the user.

### The Command Line

```
oneClick run -b <base location> -p <project name>
```

When running a project two pieces of information are required, the base location and the project name. When a project is run for the first time, OneClick, generates the project configuration file, then incorporates all global configuration items. Next, the DELIVER/project folder is scanned for applications and added to the configuration. Going forward a combination of the project configuration file and DELIVER contents are used to maintain the project integrity.

### Other Parameters

| Parameter     | Description                                               | Default Value |
|---------------|-----------------------------------------------------------|---------------|
| --consoleNode | Use the specified to run the MRI analysis.                |               |
| --start       | Start at the specified phase. (Analysis, Report)          |               |
| --end         | End at the specified phase. (Discovery, Analysis, Report) | Report        |

<a name="AIPcompatibility"></a>
# CAST AIP versions compatibility

This extension is compatible with **all AIP versions from 8.3.3** and above, and will be also in future versions.

<a name="expect"></a>

1. Code discovery
1. Run CAST MRI Analysis
1. Run CAST Highlight Analysis
1. Generate Due Diligence Assessment Report

<a name="KnownIssues"></a>
# Known issues

- None

<a name="Limitations"></a>
# Limitations and potential enhancements

- None


