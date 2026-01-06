# network-auth Specification

## Purpose
TBD - created by archiving change add-dual-zone-support. Update Purpose after archive.
## Requirements
### Requirement: Multi-Zone Network Authentication
The system SHALL support authentication for both Teaching Zone (SRUN) and Dorm Zone (Dr.COM) networks based on configuration.

#### Scenario: Teaching Zone Login
- **WHEN** `NETWORK_ZONE` is set to `'teaching'`
- **AND** `login()` is called
- **THEN** the system SHALL log "Executing Teaching Zone Login Strategy"
- **AND** the system SHALL use the SRUN protocol (get challenge, encrypt, login)

#### Scenario: Dorm Zone Login
- **WHEN** `NETWORK_ZONE` is set to `'dorm'`
- **AND** `login()` is called
- **THEN** the system SHALL log "Executing Dorm Zone Login Strategy"
- **AND** the system SHALL use the Dr.COM protocol (HTTP GET to `172.30.255.42:801`)
- **AND** the request SHALL include `callback=dr1003` and `login_method=1`
- **AND** the `wlan_user_ip` parameter SHALL use the dynamically detected local IP
- **AND** the `user_account` SHALL be prefixed with `,0,`
- **AND** the system SHALL verify success by checking the response body for `"result":1` or `"msg":"成功"` (HTTP 200 alone is insufficient)

