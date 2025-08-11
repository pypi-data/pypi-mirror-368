=======
History
=======

0.17.1 (07-08-2025)
-------------------

Changelog:

* fix: experiments no longer return data too early before measurement is complete.

Driver/firmware compatibility:

* Cluster: compatible with device firmware `v0.12.1 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.12.0>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.17.1>`__.


0.17.0 (03-06-2025)
-------------------

Changelog:

* feat: Change the type of the `debug` parameter to `types.DebugLevel` (see also below) (!339).
* refactor: remove `generic_func` for maintainability (!327).
* refactor: retrieving acquisitions is now significantly faster (up to 3 to 4 times faster) (!346).
* fix: docstring and release pipeline fixes (!361).
* fix: allow cluster firmware updates when a QDM module is present (!373).
* fix: allow single-slot module firmware updates (!377).
* refactor: remove and prevent empty docstring sections on non-generated files (!379).
* feat: rename multiple QTM QCoDeS parameters for IOChannel, Quad (!385, !387).
* fix: fix QTM-like dummy acquisition (!394).

API changes:

* **Breaking** The default value for `debug` (for non-dummy instruments),
  `DebugLevel.DEFAULT (== 0)`, no longer checks for system errors on every
  single SCPI command. It only checks on ``start_sequencer`` and ``stop_sequencer`` (!339).
* **Breaking** Rename multiple QTM `IOChannel` and `Quad` QCoDeS parameters (!385, !387).
* ``check_error_queue`` is now a public method of ``Cluster``, instead of a private method (!339).

Driver/firmware compatibility:

* Cluster: compatible with device firmware `v0.12.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.12.0>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.17.0>`__.

0.16.0 (11-03-2025)
-------------------
Changelog:

* feat: add EOM driver for QTM (!334)
* feat: make qblox-cfg give more meaningful error when it cannot connect (!322)
* feat: add support for QTM Truth Table (!340, !285)
* feat: make component classes more accessible to users (!350)
* fix: correct filter delay in simulations (!344)
* fix: SCPI parser compatibility to make ``','`` a valid delimiter (!324)
* fix: typo in the generation of input offset QCoDeS parameters (!313)
* fix: change type conversion of ``Polarity`` and ``SyncRef`` enum instances to ``int`` (!315)
* docs: update doc string of ``binned_acq_time_ref`` (!317)
* refactor: do only one error check with instrument in case of python error (!333)
* refactor: general code cleanup (!320, !336)
* chore: add a triggered job from qblox_instruments to the qblox_instruments_docs repo (!318)
* chore: updated latest assemblers based on Cluster QCM, for dummy assembly operation (!312)
* chore: [backport][v0.15.x] assemblers: update assemblers with cluster_qcm build (!314)

API changes:

* **Breaking** Drop support for Python 3.8; this version of qblox-instruments supports Python 3.9 and higher (!320)
* feat: add ``is_dummy`` property to ``Cluster`` and ``Module`` to check whether the instrument is a dummy (!326, !329)
* feat: add ``shutdown_module(s)``, ``reboot_module(s)``, and ``powerup_module(s)`` commands to ``Cluster`` (!301)
* feat: add ``get_hardware_revisions`` to ``Cluster`` to retrieve all hardware information present on the instrument (!310)
* feat: add ``--include-slots``, ``--exclude-slots`` settings for the `qblox-cfg update` command (!321, !306)

Driver/firmware compatibility:

* Cluster: compatible with device firmware `v0.11.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.11.0>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.16.0>`__.


0.15.0 (20-12-2024)
-------------------

Changelog:

* Rename QcmQrmDummyTransport to ModuleDummyTransport, since it does not apply solely to QCM and QRM modules anymore.
* qblox-cfg support for extended instruments
* Require confirmation for qblox-pnp commands that make bulk configuration changes to all devices on the network
* `SystemState`, `SystemStatusOld`, and `get_system_state` are deprecated and removed from the codebase
* `SequencerState`, `SequencerStatusOld`, `get_sequencer_state`, and `get_acquisition_state` are deprecated and removed from the codebase
* Fix the network calibration failure status flag so that it is rendered correctly
* Added a compatibility check in-cluster, disallowing the user from using modules of different software versions unless debug > 0
* Updated latest assemblers based on Cluster QCM, for dummy assembly operation

API changes:

* **Breaking:** Removed `LO:PRESent?` and its corresponding QCoDeS parameter and python wrapper.
* **Breaking:** Removed `RF` field within `*MODS?` command
* **Breaking:** Usage of `*DESC?` instead of `*MODS?` within the initialization of qblox_instruments
* **Deprecated:** Class `QcmQrmDummyTransport` is deprecated. Use `ModuleDummyTransport` instead
* Add support for time module
* Add `is_rf` field within `*DESC?` command
* Removed QTM `in_counter_mode`, `in_counter_rising`, and `in_counter_falling` experimental/testing parameters
* Added QTM `binned_acq_count_source`, `binned_acq_on_invalid_count`, and `binned_acq_on_invalid_threshold` parameters

Driver/firmware compatibility:

* Cluster: compatible with device firmware `v0.10.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.10.0>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.15.0>`__.


0.14.1 (05-09-2024)
-------------------

Changelog:

* Added support for Automatic Mixer Calibration (AMC)

API changes:

* `module.out{x}_lo_freq` can be set with an optional keyword argument `cal_type` which can be one of "off", "lo only" and "lo and sidebands".
* New parameter `module.out{x}_lo_freq_cal_type_default` can set the default `cal_type`.
* `sequencer.nco_freq` can be set with an optional keyword argument `cal_type` which can be one of "off", "sideband".
* New parameter `sequencer.nco_freq_cal_type_default` can set the default `cal_type`.

Driver/firmware compatibility:

* Cluster: compatible with device firmware `v0.9.1 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.9.1>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.14.1>`__.


0.14.0 (09-08-2024)
-------------------

Changelog:

* Added support for Real-Time Pre-Distortion (RTP)
* Added support for Automatic Mixer Calibration (AMC)

API changes:

* RTP-related QCoDeS parameters

Driver/firmware compatibility:

* Cluster: compatible with device firmware `v0.9.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.9.0>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.14.0>`__.

0.13.0 (25-04-2024)
-------------------

Changelog:

* Added support for new, preliminary QTM (Quantum Timetaging Module)
* Fixed mixed usage of integer/string keys in QcmQrmDummyTransport._sequencer_status. The keys are now strings always.
* Made the dummy cluster and dummy module correctly propagate commands to its modules and sequencers, if the module and sequencer numbers are not specified as arguments.
* Fix bug on qblox-pnp device list parsing
* Support for QDM prototype

API changes:

* Upper limit of `nco_prop_delay_comp` increased from 50ns to 109ns
* Added QTM related parameters
* Added `class IOChannel`, comparable to `class Sequencer` but more specific to io channels

Driver/firmware compatibility:

* Cluster: compatible with device firmware `v0.8.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.8.0>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.13.0>`__.

0.12.0 (06-02-2024)
-------------------

Changelog:

* Added support for new cluster firmware release.
* Added a check on `Cluster()`, to verify that application versions are all the same in all the modules, if not an exception is thrown.
* Added URLs to deprecation warnings, that link to `deprecated section of the docs <https://qblox-qblox-instruments.readthedocs-hosted.com/en/main/getting_started/deprecated.html>`__.

API changes:

* Deprecated entire Pulsar Device and its types and interfaces. This device is no longer in the field and is considered legacy.
* Fix SCPI command 'TNN:CALIB:EXEC:' -> 'TNN:CALIB:EXEC'
* Substituted CRITICAL flag with RESOLVED
* Added critical temperature error flag
* Changed avg_count to 0 instead of NaN when no TTL event is detected.
* Added new method 'Cluster.get_connected_modules()', which returns slot index and QcmQrm object for all occupied slots.
* Change 'SEQuencer#:STATE?' SCPI return.
* Added interface to clear sequencer flags.
* Deprecated get_sequencer_state interface.
* Added get_sequencer_status interface.
* Added preliminary support for QTM.

Driver/firmware compatibility:

* Cluster: compatible with device firmware `v0.7.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.7.0>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.12.0>`__.

0.11.2 (27-10-2023)
-------------------

Changelog:

* Added support for new cluster firmware release.

API changes:

* Add a method to get the maximum allowed attenuation for that specific board, use it to populate the respective range of the QCoDeS parameter.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.11.1 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.11.1>`__.
* Pulsar QRM: compatible with device firmware `v0.11.1 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.11.1>`__.
* Cluster: compatible with device firmware `v0.6.2 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.6.2>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.11.2>`__.

0.11.1 (15-09-2023)
-------------------

Changelog:

* Fixed compatibility with Python 3.7
* Fixed `qblox-pnp` under MacOS
* Added support for new cluster firmware release.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.11.1 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.11.1>`__.
* Pulsar QRM: compatible with device firmware `v0.11.1 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.11.1>`__.
* Cluster: compatible with device firmware `v0.6.1 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.6.1>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.11.1>`__.

0.11.0 (27-07-2023)
-------------------

Changelog:

* Added marker inversion functionality, for changing marker default voltage level. Previously it defaulted to LOW but now
  user can use the marker inv parameters to select default value of HIGH.
* Made all the SystemStatusFlags more concise.
* Added ability for ADC's inputs to be offset.
* Changed channel map to support real-mode waveform playback and make the parameters usage more intuitive.
* Fixed missing set/get parameters on dummy instrument.
* Fixed global divide-by-zero settings in numpy, moving it for local scope when is potentially possible.

API changes:

* SystemStatusFlags regrouped PLL flags {CARRIER_PLL_UNLOCKED, FPGA_PLL_UNLOCKED, LO_PLL_UNLOCKED} -> {PLL_UNLOCKED}
* SystemStatusFlags regrouped Temp flags {FPGA_TEMPERATURE_OUT_OF_RANGE, CARRIER_TEMPERATURE_OUT_OF_RANGE,
  AFE_TEMPERATURE_OUT_OF_RANGE, LO_TEMPERATURE_OUT_OF_RANGE, BACKPLANE_TEMPERATURE_OUT_OF_RANGE} -> {TEMPERATURE_OUT_OF_RANGE}
* SystemStatusFlags added flag {HARDWARE_COMPONENT_FAILED}
* QCoDeS parameter added for input offset : {in0_offset_path0, in0_offset_path1, in0_offset, in1_offset}
* QCoDeS parameter added for marker inversion: {marker0_inv_en, marker1_inv_en, marker2_inv_en, marker3_inv_en}
* QCoDeS parameters changed for channel map: channel_map_pathX_outY_en -> connect_outX
* QCoDeS parameters added for real-mode acquisition: {connect_acq_I, connect_acq_Q}
* Added utility methods for configuring the channel map: {disconnect_outputs, disconnect_inputs, connect_sequencer}
* Added `qblox-cfg describe -j/--json`` to more explicitly expose the functionality currently only shown when verbosity is increased

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.11.0 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.11.0>`__.
* Pulsar QRM: compatible with device firmware `v0.11.0 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.11.0>`__.
* Cluster: compatible with device firmware `v0.6.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.6.0>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.11.0>`__.

0.10.1 (17-07-2023)
-------------------

Changelog:

* Added support for new cluster firmware release.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.10.0 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.10.0>`__.
* Pulsar QRM: compatible with device firmware `v0.10.0 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.10.0>`__.
* Cluster: compatible with device firmware `v0.5.1 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.5.1>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.10.1>`__.

0.10.0 (01-05-2023)
-------------------

Changelog:

* Changed resolution of the sequencer's real-time timegrid from 4 ns to 1 ns for all real-time instructions, except
  for the instructions that operate on the NCOs (e.g. set_freq, reset_ph, set_ph, set_ph_delta). For now, the NCO
  instructions still operate on the 4 ns timegrid.
* Added the option to control the brightness of the front-panel LEDs. The brightness can be set to four settings:
  high, medium, low, off.
* Added a sequencer flag to indicate that input was out-of-range during an acquisition's integration window.
  Previously, the input out-of-range could only be detected by scope acquisitions. Now all acquisitions are able to
  detect this.
* Changed the format with which sequencer and scope configurations are communicated between the instrument and
  driver to JSON objects as a first step towards improving driver backwards compatibility.
* Improved handling of acquisitions in the dummy drivers.
* Added more detail to the HISTORY file.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.10.0 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.10.0>`__.
* Pulsar QRM: compatible with device firmware `v0.10.0 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.10.0>`__.
* Cluster: compatible with device firmware `v0.5.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.5.0>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.10.0>`__.

0.9.0 (28-02-2023)
------------------

Changelog:

* Added new feedback functionality to allow sequencer-to-sequencer, module-to-module and Cluster-to-Cluster feedback.
  To support this, new Q1ASM instructions are added to the instruction set. The wait_trigger instruction is also
  changed accordingly with a new address argument.
* The external trigger input is now also connected to the new trigger network for feedback purposes and must be mapped
  to this network using the associated parameters.
* QCoDeS parameter name change: discretization_threshold_acq -> thresholded_acq_threshold
* QCoDeS parameter name change: phase_rotation_acq -> thresholded_acq_rotation
* Improved performance of the get_acquisitions method.
* Fixed ability to exclude sequencer.sequence readout when creating a snapshot through QCoDeS.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.9.0 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.9.0>`__.
* Pulsar QRM: compatible with device firmware `v0.9.0 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.9.0>`__.
* Cluster: compatible with device firmware `v0.4.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.4.0>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.9.0>`__.

0.8.2 (27-01-2023)
------------------

Changelog:

* Add compatibility for Cluster release v0.3.1
* Improved scope mode data handling.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.8.0 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.8.0>`__.
* Pulsar QRM: compatible with device firmware `v0.8.0 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.8.0>`__.
* Cluster: compatible with device firmware `v0.3.1 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.3.1>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.8.2>`__.

0.8.1 (19-12-2022)
------------------

Changelog:

* Removed Read the Docs files from repository and moved it to https://gitlab.com/qblox/packages/software/qblox_instruments_docs.
* Improved performance of the get_acquisitions method.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.8.0 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.8.0>`__.
* Pulsar QRM: compatible with device firmware `v0.8.0 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.8.0>`__.
* Cluster: compatible with device firmware `v0.3.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.3.0>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.8.1>`__.

0.8.0 (09-12-2022)
------------------

Changelog:

* Added support for the redesigned NCO.
* Added support for the NCO phase compensation for propagation delays from output to input path.
* Increased NCO range from +/-300 MHz to +/-500 MHz.
* Added support for TTL trigger acquisitions.
* Improved error handling for sequence retrieval.
* Added support for attenuation control to dummy modules.
* Added support to set acquisition data in dummy modules.
* Updated the assemblers used by the dummy modules.
* Added and updated test cases for new features.
* Added NCO control tutorial notebook.
* Added TTL trigger acquisition tutorial notebook.
* Improved doc-strings.
* Updated documentation and tutorials.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.8.0 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.8.0>`__.
* Pulsar QRM: compatible with device firmware `v0.8.0 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.8.0>`__.
* Cluster: compatible with device firmware `v0.3.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.3.0>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.8.0>`__.

0.7.1 (23-01-2023)
------------------

Changelog:

* Added support for new firmware release.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.7.3 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.7.3>`__.
* Pulsar QRM: compatible with device firmware `v0.7.3 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.7.3>`__.
* Cluster: compatible with device firmware `v0.2.3 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.2.3>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.7.1>`__.

0.7.0 (04-08-2022)
------------------

Changelog:

* Added command clear acquisition data
* SPI Rack driver was updated to always unlock it at startup, not initialize the span by default, change the code for
  changing the span of the S4g and D5a and ensure no mismatch between the host computer and SPI rack on the span
  value before doing a current/voltage set operation.
* Changed assembler character limit, and add code to strip the sequencer program from comments and unused information.
* Updated tutorials to make them independent of the device type (ie QRM or QCM) and to divide them in a Pulsar and a
  Cluster section.
* Changed QRM output offset range to 1Vpp.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.7.2 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.7.2>`__.
* Pulsar QRM: compatible with device firmware `v0.7.2 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.7.2>`__.
* Cluster: compatible with device firmware `v0.2.2 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.2.2>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.7.0>`__.

0.6.1 (20-05-2022)
------------------

Changelog:

* Added input and output attenuation control for RF-modules.
* Added the ability to disable LOs in RF-modules.
* Added a method to manually restart ADC calibration in QRM and QRM-RF modules. Be aware that this is a preliminary
  method that might change in the near future.
* Changed the SPI Rack driver to eliminate unwanted voltage/current jumps by disabling the reset of
  voltages/currents on initialization and adding checks to prevent the user to set a value outside of the currently
  set span.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.7.1 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.7.1>`__.
* Pulsar QRM: compatible with device firmware `v0.7.1 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.7.1>`__.
* Cluster: compatible with device firmware `v0.2.1 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.2.1>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.6.1>`__.

0.6.0 (29-03-2022)
------------------
This release introduces a significant refactor to Qblox Instruments as both a general restructure is introduced
and the preliminary Cluster driver is replaced by the definitive driver. Unfortunately, this means that this
release also introduces a few breaking changes. In exchange, we believe that this release prepares Qblox Instruments
for the future.

Changelog:

* Renamed all classes to be compliant with PEP8's capswords format.
* Restructured imports; all drivers are now imported directly from `qblox_instruments` as follows:
    * from qblox_instruments import Cluster, Pulsar, SpiRack
    * from qblox_instruments.qcodes_drivers.spi_rack_modules import D5aModule, S4gModule
* With the new Cluster firmware release, the user now interacts with the Cluster as a single instrument instead
  of a rack of instruments. The new Cluster driver reflects this. It detects where and which modules are in the rack
  and automatically makes them accessible as an InstrumentChannel submodule accessible as `Cluster.module<x>`, where
  `x` is the slot index of the rack.
* The Pulsar QCM and Pulsar QRM drivers have been combined into a single Pulsar driver that covers the functionality
  of both.
* The SPI Rack driver driver has been split into a native and QCoDeS layer to improve separation of functionality.
* Each sequencer's parameters are now accessible through it's own InstrumentChannel submodule. This means
  that parameters are now accessible as `module.sequencer<x>.parameter`, where `x` is the sequencer index.
* Renamed `get_system_status` to `get_system_state` to be inline with other state method names.
* The methods `get_system_state` and `get_sequencer_state` now return namedtuples of type `SystemState` and
  `SequencerState` respectively to ease handling of the returned statuses and accompanying flags.
* Renamed the sequencer's `waveform_and_programs` parameter to `sequence`.
* The way to configure the driver as a dummy has been changed to use enums for module type selection.
* Added keep alive pinging to the socket interface to keep the instrument connection from closing after
  a platform dependant idle period.
* Fixed general code duplication problem between instruments.
* Introduced `qblox-cfg` as the new configuration management tool with which to update the Cluster and Pulsar
  instruments. As of Pulsar firmware release v0.7.0 and Cluster firmware release v0.2.0, the configuration
  management tool is no longer shipped with the release, but instead `qblox-cfg` must be used. This new tool provides
  far more functionality and exposes the improved network configurability of the latest firmware releases.
* On top of the new configuration management tool, `qblox-pnp` is also instroduced as the new network debug tool.
  This tool, in combination with the latest firmware releases, allows to easily find instruments in the network and
  to potentially recover them in case of network/IP configuration problems.
* Improved unit test coverage.
* Updated the documentation on Read the Docs to reflect the changes.
* Added various improvements and fixes to the tutorials.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.7.0 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.7.0>`__.
* Pulsar QRM: compatible with device firmware `v0.7.0 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.7.0>`__.
* Cluster: compatible with device firmware `v0.2.0 <https://gitlab.com/qblox/releases/cluster_releases/-/releases/v0.2.0>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.6.0>`__.

0.5.4 (22-12-2021)
------------------

Changelog:

* Cleaned code to improve unit test code coverage.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.6.3 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.6.3>`__.
* Pulsar QRM: compatible with device firmware `v0.6.3 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.6.3>`__.
* Cluster CMM: compatible with device firmware v0.1.1.
* Cluster CMM: compatible with device firmware v0.1.5.
* Cluster CMM: compatible with device firmware v0.1.5.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.5.4>`__.

0.5.3 (26-11-2021)
------------------

Changelog:

* Improved __repr__ response from the QCoDeS drivers.
* Added tutorials for multiplexed sequencing, mixer correction, RF-control and Rabi experiments.
* Fixed empty acquisition list readout from dummy modules.
* Added RF-module support to dummy modules.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.6.2 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.6.2>`__.
* Pulsar QRM: compatible with device firmware `v0.6.2 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.6.2>`__.
* Cluster CMM: compatible with device firmware v0.1.0.
* Cluster CMM: compatible with device firmware v0.1.3.
* Cluster CMM: compatible with device firmware v0.1.3.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.5.3>`__.

0.5.2 (11-10-2021)
------------------

Changelog:

* Device compatibility update.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.6.2 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.6.2>`__.
* Pulsar QRM: compatible with device firmware `v0.6.2 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.6.2>`__.
* Cluster CMM: compatible with device firmware v0.1.0.
* Cluster CMM: compatible with device firmware v0.1.3.
* Cluster CMM: compatible with device firmware v0.1.3.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.5.2>`__.

0.5.1 (07-10-2021)
------------------

Changelog:

* Device compatibility update.
* Added channel map functionality to dummy layer.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.6.1 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.6.1>`__.
* Pulsar QRM: compatible with device firmware `v0.6.1 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.6.1>`__.
* Cluster CMM: compatible with device firmware v0.1.0.
* Cluster CMM: compatible with device firmware v0.1.2.
* Cluster CMM: compatible with device firmware v0.1.2.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.5.1>`__.

0.5.0 (05-10-2021)
------------------

Changelog:

* Increased sequencer support to 6 sequencers per instrument.
* Added support for real-time mixer correction.
* Renamed Pulsar QRM input gain parameters to be inline with output offset parameter names.
* Updated the assemblers for the Pulsar QCM and QRM dummy drivers to support the phase reset instruction.
* Added preliminary driver for the Cluster.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.6.0 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.6.0>`__.
* Pulsar QRM: compatible with device firmware `v0.6.0 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.6.0>`__.
* Cluster CMM: compatible with device firmware v0.1.0.
* Cluster CMM: compatible with device firmware v0.1.1.
* Cluster CMM: compatible with device firmware v0.1.1.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.5.0>`__.

0.4.0 (21-07-2021)
------------------

Changelog:

* Changed initial Pulsar QCM and QRM device instantiation timeout from 60 seconds to 3 seconds.
* Added support for the new Pulsar QRM acquisition path functionalities (i.e. real-time demodulation, integration, discretization, averaging, binning).
* Updated the assemblers for the Pulsar QCM and QRM dummy drivers.
* Switched from using a custom function to using functools in the QCoDeS parameters.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.5.2 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.5.2>`__.
* Pulsar QRM: compatible with device firmware `v0.5.0 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.5.0>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.4.0>`__.

0.3.2 (21-04-2021)
------------------

Changelog:

* Added QCoDeS driver for D5A SPI-rack module.
* Updated documentation on ReadTheDocs.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.5.1 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.5.1>`__.
* Pulsar QRM: compatible with device firmware `v0.4.1 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.4.1>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.3.2>`__.

0.3.1 (09-04-2021)
------------------

Changelog:

* Device compatibility update.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.5.1 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.5.1>`__.
* Pulsar QRM: compatible with device firmware `v0.4.1 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.4.1>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.3.1>`__.

0.3.0 (25-03-2021)
------------------

Changelog:

* Added preliminary internal LO support for development purposes.
* Added support for Pulsar QCM's output offset DACs.
* Made IDN fields IEEE488.2 compliant.
* Added SPI-rack QCoDeS drivers.
* Fixed sequencer offset instruction in dummy assemblers.
* Changed acquisition out-of-range result implementation from per sample basis to per acquisition basis.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.5.0 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.5.0>`__.
* Pulsar QRM: compatible with device firmware `v0.4.0 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.4.0>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.3.0>`__.

0.2.3 (03-03-2021)
------------------

Changelog:

* Small improvements to tutorials.
* Small improvements to doc strings.
* Socket timeout is now set to 60s to fix timeout issues.
* The get_sequencer_state and get_acquisition_state functions now express their timeout in minutes iso seconds.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.4.0 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.4.0>`__.
* Pulsar QRM: compatible with device firmware `v0.3.0 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.3.0>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.2.3>`__.

0.2.2 (25-01-2021)
------------------

Changelog:

* Improved documentation on ReadTheDocs.
* Added tutorials to ReadTheDocs.
* Fixed bugs in Pulsar dummy classes.
* Fixed missing arguments on some function calls.
* Cleaned code after static analysis.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.4.0 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.4.0>`__.
* Pulsar QRM: compatible with device firmware `v0.3.0 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.3.0>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.2.2>`__.

0.2.1 (01-12-2020)
------------------

Changelog:

* Fixed get_awg_waveforms for Pulsar QCM.
* Renamed get_acquisition_status to get_acquisition_state.
* Added optional blocking behaviour and timeout to get_sequencer_state.
* Corrected documentation on Read The Docs.
* Added value mapping for reference_source and trigger mode parameters.
* Improved readability of version mismatch.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.4.0 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.4.0>`__.
* Pulsar QRM: compatible with device firmware `v0.3.0 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.3.0>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.2.1>`__.

0.2.0 (21-11-2020)
------------------

Changelog:

* Added support for floating point temperature readout.
* Renamed QCoDeS parameter sequencer#_nco_phase to sequencer#_nco_phase_offs.
* Added support for Pulsar QCM input gain control.
* Significantly improved documentation on Read The Docs.

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.4.0 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.4.0>`__.
* Pulsar QRM: compatible with device firmware `v0.3.0 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.3.0>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.2.0>`__.

0.1.2 (22-10-2020)
------------------

Changelog:

* Fixed Windows assembler for dummy Pulsar
* Fixed MacOS assembler for dummy Pulsar

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.3.0 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.3.0>`__.
* Pulsar QRM: compatible with device firmware `v0.2.0 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.2.0>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.1.2>`__.

0.1.1 (05-10-2020)
------------------

Changelog:

* First release on PyPI

Driver/firmware compatibility:

* Pulsar QCM: compatible with device firmware `v0.3.0 <https://gitlab.com/qblox/releases/pulsar_qcm_releases/-/releases/v0.3.0>`__.
* Pulsar QRM: compatible with device firmware `v0.2.0 <https://gitlab.com/qblox/releases/pulsar_qrm_releases/-/releases/v0.2.0>`__.

**Note:** You can also find this release on Gitlab `here <https://gitlab.com/qblox/packages/software/qblox_instruments/-/releases/v0.1.1>`__.
