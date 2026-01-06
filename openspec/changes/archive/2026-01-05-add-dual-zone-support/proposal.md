# Change: Add Dual Zone Support

## Why
Users need to access the network from two different physical locations with different authentication protocols:
1. **Teaching Zone**: Uses the existing SRUN protocol (complex JS encryption).
2. **Dorm Zone**: Uses the Dr.COM protocol (simple HTTP GET).

## What Changes
- **Configuration**: Add `NETWORK_ZONE` setting to `app/config.py` (defaults to 'teaching').
- **Architecture**: Refactor `SZUNetworkClient` to support multiple login strategies.
- **Implementation**:
  - Rename existing `login()` to `_login_teaching()`.
  - Add new `_login_dorm()` method for Dr.COM protocol with strict response validation.
  - Create a new `login()` method that dispatches based on `NETWORK_ZONE` and logs the active strategy.
- **Validation**:
  - Dorm login MUST verify response body content (`"result":1` or `"msg":"成功"`) in addition to HTTP 200.
  - Dorm login MUST use dynamically detected IP for `wlan_user_ip`.

## Impact
- **Affected Specs**: `network-auth`
- **Affected Code**: 
  - `app/config.py`
  - `app/client.py`
  - `main.py` (indirectly via config)
