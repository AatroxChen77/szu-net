## 1. Implementation
- [x] 1.1 Update `app/config.py`: Add `NETWORK_ZONE` field to `Settings` (choices: 'teaching', 'dorm').
- [x] 1.2 Refactor `app/client.py`: Rename `login` to `_login_teaching` (preserve all existing logic).
- [x] 1.3 Refactor `app/client.py`: Implement `_login_dorm` method.
    - [x] Use `self.ip` (dynamically detected) for `wlan_user_ip` param.
    - [x] Perform strict success validation: Check response body for `"result":1` or `"msg":"成功"`.
- [x] 1.4 Refactor `app/client.py`: Implement main `login` dispatcher.
    - [x] Add INFO log: "Executing {zone} Zone Login Strategy".
    - [x] Dispatch to appropriate method based on `settings.NETWORK_ZONE`.
- [x] 1.5 Update `.env.example` to include `NETWORK_ZONE` configuration.
