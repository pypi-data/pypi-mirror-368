# Cisco RADKit

Cisco Remote Automation Development Kit (RADKit) is a Software Development Kit (SDK) that offers a set of ready-to-use tools and Python modules, providing efficient and scalable interactions with local or remote equipment. It enables manual device access and automation, and allows users to capture data, monitor states, deploy configurations, or administer network devices.

For more information, please visit:

- [RADKit Home Page](https://radkit.cisco.com/)
- [RADKit Data Sheet](https://www.cisco.com/c/en/us/td/docs/cloud-systems-management/remote-automation-development-kit/radkit-data-sheet.html)
- [RADKit Documentation](https://radkit.cisco.com/docs/) (cisco.com login required)

## Downloading

RADKit is available in two forms: as an installer (containing a dedicated Python run-time environment + all required third-party dependencies) for the most common platforms, and as individual Python wheels for all supporrted platforms. The wheels can either be downloaded as tarballs from [the main RADKit Home Page](https://radkit.cisco.com/downloads/), or individually from [PyPI.org](https://pypi.org).

At the moment, RADKit comprises four different Python packages:

- [cisco-radkit-client](https://pypi.org/project/cisco-radkit-client/): RADKit Client REPL, Python API and Network Console;
- [cisco-radkit-service](https://pypi.org/project/cisco-radkit-service/): RADKit Service + Control CLI/API;
- [cisco-radkit-genie](https://pypi.org/project/cisco-radkit-genie/): the [Genie](https://pypi.org/project/genie/) integration layer for RADKit Client;
- [cisco-radkit-common](https://pypi.org/project/cisco-radkit-common/): a utility package that is shared between Client & Service.

## Verifying

All RADKit Python wheels are both attested and signed.

- **Attestation**: PyPI.org is configured to only accept RADKit wheels published by Cisco. For more details on attestations, see [the PyPI docs](https://docs.pypi.org/attestations/).

- **Code Signing**: Cisco provides signed SHA-256 digests for all RADKit wheels on [the main RADKit Home Page](https://radkit.cisco.com/downloads/) in the form of a `.sig256` file for every release. Those digests can be cryptographically verified using the mechanism documented at [this location](https://radkit.cisco.com/docs/security/security_codesign.html).

## Installing

Installing RADKit Service or Client is a simple matter of performing a `pip install` (or equivalent using your tool of choice) of RADKit Client and/or Service on a [supported Python version](https://radkit.cisco.com/docs/compatibility.html) (the use of a virtual environment is strongly recommended):

```
$ python3 -m pip install cisco_radkit_client
$ python3 -m pip install cisco_radkit_service
```

More detailed instructions on how to install RADKit can be found at [this location](https://radkit.cisco.com/docs/install/install_pip.html).