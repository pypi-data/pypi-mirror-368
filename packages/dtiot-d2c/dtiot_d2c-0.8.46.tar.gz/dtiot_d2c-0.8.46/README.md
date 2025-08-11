# Device to Cloud Command Line Interface
The command line program ```d2c``` implements for the IoT platform **Device to Cloud** (**D2C**) from **Deutsche Telekom IoT GmbH** (**DT IoT**) a command line interface. By this IoT system administrators shall be supported and the implementation of shell script automation shall be simplified.  The command ```d2c``` comes with a wide range of sub-commands to access the **D2C** system via the **DMO** API (Device Management Orchestrator), also from **DT IoT**.  

# Install or update
```bash
python3 -m pip install --upgrade dtiot_d2c
```
  
> ** INFO **  
> Pip not only installs the python packages into your local site-packages it also generates the executable ```d2c```.  
> For Windows make sure that the directory **%APPDATA%\Python\PythonXX\Scripts** (or similar) is in your search path. If not you cannot execute ```d2c``` on the command line.  
  
# Getting command line help
```bash
d2c -h
```
  
# Getting started
To get started goto [Getting Started](https://myiot-d.com/docs/device-to-cloud/command-line-interface/getting-started/) of [Device to Cloud documentation](https://myiot-d.com/docs/device-to-cloud/command-line-interface/about/) at DT IoT.  
  
# Documentation links
- [Getting started with d2c](https://myiot-d.com/docs/device-to-cloud/command-line-interface/getting-started/)</br>
  Learn how to install and test the **d2c** command.
- [d2c Basics](https://myiot-d.com/docs/device-to-cloud/command-line-interface/basics/)</br>
  Learn how to use the **d2c** command and get an overview about all the sub-commands.
- [DMO access profile management](https://myiot-d.com/docs/device-to-cloud/command-line-interface/dmo-access-profiles-management/)</br>
  Learn what DMO access profiles are and how to manage them with **d2c** command.
- [DMO commands](https://myiot-d.com/docs/device-to-cloud/command-line-interface/dmo-commands/)</br>
  Reference documentation for DMO sub-commands of **d2c**.
- [D2C client domain model](https://myiot-d.com/docs/device-to-cloud/command-line-interface/d2c-client-domain-model/)</br>
  Learn about the client sided D2C domain model and the different command domains.
- [D2C device management commands](.https://myiot-d.com/docs/device-to-cloud/command-line-interface/device-commands/)</br>
  Reference documentation for D2C device management sub-commands of **d2c**.
- [D2C application management commands](https://myiot-d.com/docs/device-to-cloud/command-line-interface/application-commands/)</br>
  Reference documentation for D2C application management sub-commands of **d2c**.
- [D2C device group management commands](https://myiot-d.com/docs/device-to-cloud/command-line-interface/device-group-commands/)</br>
  Reference documentation for D2C device group management sub-commands of **d2c**.
- [D2C administration commands](https://myiot-d.com/docs/device-to-cloud/command-line-interface/administration-commands/)</br>
  Reference documentation for D2C administration sub-commands of **d2c**.
- [d2c command environment and configuration variables](https://myiot-d.com/docs/device-to-cloud/command-line-interface/tips/)</br>
  Reference documentation for environment and configuration variables of **d2c**.



