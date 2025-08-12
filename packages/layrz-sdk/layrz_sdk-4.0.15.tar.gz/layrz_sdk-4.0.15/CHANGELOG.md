# Changelog

## 4.0.14

- Added decorators to measure function execution time.

## 4.0.13

- Added `partition_number` field to `Asset` entity to represent the partition number assigned to the asset.
- Added `pk` and `trigger_id` fields to `BroadcastResult` entity to represent the broadcast result ID and trigger ID respectively.
- Updated `BroadcastResult` entity to include an `error` field to represent any error message if the broadcast failed.
- Updated `BroadcastStatus` enum to include `BAD_REQUEST` and `INTERNAL_ERROR` as new status values.
- Added `algorithm` field to `BroadcastResult` entity to represent the algorithm used for the broadcast, if any.

## 4.0.12

- Added `search_time_delta` field to `Trigger` entity to define the search time delta of the trigger.
- Updated `TriggerKind` enum to include `NESTED` as a new trigger kind

## 4.0.11

- Added protection of worksheets in `Report` entity when exporting to Microsoft Excel to enable cell locking.

## 4.0.10

- Added support for lock cells in `ReportCol` entity and their export to Microsoft Excel.
- Added support for `list[Geofence]` on `Message` entity for presence in geofences.

## 4.0.9

- Added validation for `destination_phones` field in `Operation` entity to ensure it is a list of `DestinationPhone` objects.
- Updated `OperationPayload` entity to use `DestinationPhone` instead of a list of strings for `destinations`.


## 4.0.8

- Allowed `int | str | None` for `account_id` in `Operation` and `OperationPayload` entities.

## 4.0.7

- Added validation for `headers` field in `Operation` entity to ensure it is a list of dictionaries.
- Added validation for `reception_emails` field in `Operation` entity to ensure it is a list of strings or a single string.

## 4.0.6

- Added validation for `manual_action_fields` in `Trigger` entity to ensure it is a list of dictionaries.
- Added validation for `priority` field in `Trigger` entity to ensure it is an integer

## 4.0.5

- Missing doc

## 4.0.4

- Fixes on `is_primary` field in `Device` entity to ensure it is a boolean value.

## 4.0.3

- Added validation for `static_position` in `Asset` entity to ensure it can accept a dictionary representation of `StaticPosition`.

## 4.0.2

- Missing doc

## 4.0.1

- Missing doc

## 4.0.0

- Removed all aliases to be more accurate and similar to the Dart equivalent on [`layrz_models`](https://pub.dev/packages/layrz_models).

## 3.1.50

- Added `is_fixed` field to `CustomField` entity to indicate if the custom field is fixed or not.
- Updated `CustomField` entity to include `pk` field as an alias for `id`.

## 3.1.49

- New models `AtsExitExecutionHistory` and  `AtsPossibleExit` for Ats exits add formula field to `Sensor`.
## 3.1.48

- Moved `DestinationPhone` entity to its own file, and renamed from `TwilioHostPhone` to `DestinationPhone`.
- Updated `Operation` entity to use `DestinationPhone` instead of a `list[str]` for `destination_phones`.

## 3.1.47

- Changed datatype of `destinations` field in `OperationPayload` entity from `list[str]` to `list[TwilioHostPhone]`.

## 3.1.46

- Added `AssetContact` entity to represent contacts of an asset.
- Updated `Asset` entity to use `AssetContact` instead of a list of strings for contacts.
- Added `contacts` field to `Asset` entity to represent the list of contacts associated with the asset.

## 3.1.45

- Updates over `Checkpoint` and `Waypoint` models

## 3.1.44

- Removed `asset_id` from `Checkpoint` entity, now using `name` field to represent the checkpoint name.

## 3.1.43

- Fixes

## 3.1.42

- New models `CheckpointRef` and `WaypointRef` to represent checkpoints with waypoints.

## 3.1.41

- Added `owner_id` field to `Preset` entity to represent the owner of the preset.

## 3.1.40

- Added `Preset` entity to represent presets with a name, valid before date, and comment.

## 3.1.39

- Added `ExchangeService` entity to represent outbound services with credentials.
- New `CommandSeriesTicket` model
- Added more information on `OutboundService` model

## 3.1.38

- Added `owner_id` field to `Asset`, `Action`, and `Trigger` models to represent the owner of the entity.

## 3.1.37

- Fixes on `Timezone` model, added `offset` field to represent the timezone offset in seconds from UTC.
- Added some fields on `Operation` model

## 3.1.36

- Updated enum of `OperationType`

## 3.1.35

- Added models for operations handling

## 3.1.34

- Fixes on data types onf `Action` model

## 3.1.33

- New `Action` model
- New `ActionKind`, `ActionSubKind`, `GeofenceCategory` and `ActionGeofenceOwnership` enums

## 3.1.32

- New `AtsREception` model

## 3.1.31

- Expanded `Trigger` model with new fields (Almost closed to the Dart equivalent on [`layrz_models`](https://pub.dev/packages/layrz_models))
- Added `Weekday` enum to represent days of the week
- Added `TriggerKind`, `TriggerGeofenceKind`, `TriggerCaseKind`, and `TriggerCommentPattern` enums to represent different trigger types and patterns
- Almost removed all aliases from the models

## 3.1.30

- New `Function` model

## 3.1.29

- Serialization changes

## 3.1.28

- Added `BroadcastPayload` and `BroadcastService` models

## 3.1.27

- Fixes on `ChartDataSerieType` that can have a `None` value, removed str inheritance to avoid issues

## 3.1.26

- Reverted StrEnum in favor to str + Enum due to compatibility issues

## 3.1.25

- Added `AssetConstants` class to hold constants related to assets on sensors, triggers and functions.

## 3.1.24
## 3.1.23
## 3.1.22

- Backwards compatibility for `StrEnum` in Python 3.11 and below, now using `layrz_sdk.backwards.StrEnum` for versions below 3.11.

## 3.1.21

- Moved all enums to `StrEnum` and added compatibility for Python 3.11 and below.

## 3.1.20

- Fixed condition of `StrEnum` on Python 3.11, for versions below 3.11 it will use `strenum.StrEnum` instead of `enum.StrEnum`

## 3.1.19

- Added serializers for messages

## 3.1.18

- Fixes

## 3.1.17

- Fixes

## 3.1.16

- Added `primary_id` into `Asset`

## 3.1.15

- Added some parameters on `Asset` and `Device` classes
- Added `AssetMessage` and `DeviceMessage` classes to handle messages related to assets and devices 

## 3.1.14

- Some changes related to the `Case` entity

## 3.1.12

- Adjustment of all typings

## 3.1.11

- Fixes on data casting in `Message` class

## 3.1.10

- Updated docstrings to provide more information about types and usage

## 3.1.9

- Changed `json` to `parsed` on `BroadcastResponse` and `BroadcastRequest` to avoid confusion with the `json` property from `pydantic.BaseModel`

## 3.1.8

- Replaced `str` in favor of using `Path` object to manage paths on `Report` export methods

## 3.1.7

- Removed validation of asset type `SINGLE`

## 3.1.6

- Fixes on model validate on `Asset` class

## 3.1.5

- Changed `width` on `ReportHeader` from `int` to `float` due to backwards compatibility

## 3.1.4

- Fixed iteration searching for the primary device on `Asset` class

## 3.1.3

- Fixes on `Asset` entity validation, found by @simonjrojas!

## 3.1.2

- Set as optional the `asset_type` argument in `Asset` class

## 3.1.1

- Small fixes on some models to backwards compatibility

## 3.1.0

- Migrated all models to Pydantic
- Removed models `Transaction`.
- Added `mypy` to the project to enforce type checking
- Migrated from `uniitest` to `pytest` to the project to enforce unit testing

## 3.0.14

- Fixes on `GET_CUSTOM_FIELD` LCL function, now accepts a default value as the second argument (Fallback as '')

## 3.0.13

- Added `LastMessage` entity to be used in `Trigger`s

## 3.0.12

- Moved `Geofence` model from `checkpoints` to `general`
- Added `PresenceType` enum to be used in `Event` model

## 3.0.11

- Added way to standarize the `int` and `float` arguments to `float`. Allowing comparison between `int` and `float` values in LCL formulas

## 3.0.10

- Removed Self type annotation from all classes

## 3.0.9

- Added different return data of Report when password is set

## 3.0.8

- New linter and formatter using ruff
- Added typings on all classes and functions available
- New Report export format PDF (Not implemented yet)
- Added new way to encrypt .xslx files directly using the `Report` class

## 3.0.7

- Added the value of `AssetOperationMode.ZONE`
- Added a check for `Asset.operation_mode == ASSETMULTIPLE` while savind the list of child's
- Clarified the deprecation of `ReportRow.height`

## 3.0.6

- Changed print in `LineChart` to a `log.warning` and `log.fatal` in case of error

## 3.0.3

- Implemented new chart rendering library `syncfusion_flutter_charts` for Flutter.
- Changed rendering method for `LineChart`, now you should provide the `technology` to select the rendering library.

## 3.0.2

- Fixed issue with `IF()` LCL function, now only validates the nullability of the first argument.
- Added new `VERSION()` LCL Function to get the current version of the package

## 3.0.1

- Added None validation on every LCL function, when any of the arguments is None, the function will return None
- Added unit tests for all LCL functions

## 3.0.0

- Removed shared namespace to improve compatibility with other packages

## 2.2.4

- Defined new class `ReportConfiguration` to handle the configuration of the report in Python scripts

## 2.2.3

- Property `text_color` deprectated in `ReportCol`, replaced by a luminance-based color using the background color
- Property `text_color` deprectated in `ReportHeader`, replaced by a luminance-based color using the background color
- Property `width` deprectated in `ReportHeader`, replaced by the function `autofit()` to automatically fit the header width
- New entity `CustomReportPage` that receives a custom builder function to build the page
- Property `export_format` deprecated in `Report`, replaced to an argument of the function `export()`

## 2.2.2

- Updated `AssetOperationMode` to support `STATIC` and removal of `FAILOVER` mode

## 2.2.1

- Bug fixes related to removing __ from all classes

## 2.2.0

- Removed support to Python 3.12 due to a shared namespace issue.
- Reorganized classes to better support.
- Added typings to all classes and functions.

## 2.1.5

- Added declarative typing on all LCL functions
- Added support for timezone in `UNIX_TO_STR` LCL function

## 2.1.3

- Changed build mode to pyproject.toml
- Updated `LcLCore.perform()` function to receive additional globals and locals in their arguments

## v2.1.2

- Add UNIX_TO_STR LCL function

## v2.1.1

- Added `compact` in the json return format in reports

## v2.1.0

- Add bold format option to Col class
- Add freeze header option to Page class

## v2.0.1

- Fixes on package namespace

## v2.0.0

- Deprecated `lcl.core` module
- Changed `layrzsdk` to `layrz.sdk` package (With unified Layrz namespace)

## v1.4.5

- Added CaseIgnoredStatus to init file

## v1.4.4

- Added CaseIgnoredStatus to Case entity

## v1.4.3

- Added new ChartType: TableChart and NumberChart
- Starting to replace documentation format from unstructured to a structured format

## v1.4.2

- Fix, added SUBSTRING LCL to global functions

## v1.4.1

- Fixed LineChart xAxis Datetime conversion for CanvasJS, now will multiply the timestamp by 1000 to use milliseconds

## v1.4.0

- Added support for Flutter `graphic` library
  - LineChart
  - AreaChart (Replaced previous AreaChart to a temporal extend of LineChart)
  - BarChart
  - ColumnChart
  - PieChart
  - MapChart
  - ScatterChart
  - RadialBarChart

- Future deprecations:
  - HTMLChart
  - TimelineChart
  - RadarChart

## v1.3.9

- Internal changes related to GitLab CI automation

## v1.3.8

- Added SUBSTRING LCL function

## v.1.3.7

- Added sequence in cases

## v1.3.6

- Added new Map Chart
  - Added required entity MapPoint
  - Added required enum MapCenterType
- Added new HTML Chart

## v1.3.5

- Bug fix related to formula perform, added PRIMARY_DEVICE to simulation environment

## v1.3.4

- Added Transaction entity for REPCOM reports

## v1.3.3

- Added PRIMARY_DEVICE() function to Layrz Compute Language

## v1.3.2

- Updated styles of charts return object to ApexCharts or CanvasJS
- Replaced all .rst files to .md files

## v1.3.1

- Removed markerSize (in CanvasJS) for dashed series

## v1.3.0

- Added support for CanvasJS Javascript Library
- Deprecated to_apexcharts property in charts.
- New method render() in charts with support for multiple Javascript rendering library
- Added color helpers in layrzsdk.helpers

## v1.2.6

- Removed dataLabels in almost all charts (Except Pie and RadialBar)

## v1.2.5

- Optimizations for Javascript renderer

## v1.2.4

- Added dashed attribute to ChartDataSerie
- Added the Possibility to mix charts, only available for:
  - LineChart
  - AreaChart
  - ColumnChart
  - ScatterChart (Only as serie, not as main chart)

## v1.2.3

- Added new value in BroadcastStatus

## v1.2.2

- Updated ReportCol entity to set new default values
- New entity ReportDataType
- Possibility to export directly to the Report class
- Re-organized entities/ folder
- Added Broadcasts entities

## v1.2.1

- Added Report Col entity

## v1.2.0

- Added reports entities

## v1.1.4

- Bug fixes

## v1.1.3

- Bug fixes

## v1.1.2

- Bug fixes

## v1.1.1

- Bug fixes

## v1.1.0

- Reorganized files
- Added new Charts entities

## v1.0.14

- Added CONTAINS, STARTS_WITH, ENDS_WITH functions to the Layrz Computed Language

## v1.0.13

- Fixed missing import into `layrzsdk.entities.__init__.py`

## v1.0.12

- Added Geofence, Comment, Waypoint and Checkpoint entities

## v1.0.11

- Added User, Comment and Case entities

## v1.0.10

- Fixes

## v1.0.9

- Added Event and Trigger entities
- Renamed file `mesage.py` to `message.py`

## v1.0.8

- Added title getter of all charts entities

## v1.0.7

- Added PieChart, BarChart, and RadialBarChart entities

## v1.0.6

- Fixed STING to STRING bug in ChartDataType enum

## v1.0.5

- Bug fixes

## v1.0.4

- Added data_type argument of ChartDataSerie

## v1.0.3

- Added Chart configuration entity

## v1.0.2

- Added entities for Range Charts:
  - Line Charts
  - Area Charts
  - Column Charts

## v1.0.1

- Added entities for Sensors and Triggers

## v1.0.0

- Initial release
