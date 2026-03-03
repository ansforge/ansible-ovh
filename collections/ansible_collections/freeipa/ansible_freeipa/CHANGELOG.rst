Changes for 1.16.0 since 1.15.1
-------------------------------

  - Fix Ansible warnings in Firewall zone testing tasks (#1407)
  - upstream ci: Use version_name for CheckPR labels (#1406)
  - Cert tests: Do not fail on new dogtag profile not found error message (#1405)
  - upstream ci: Fix Azure pipelines invalid names (#1404)
  - upstream CI: Fix CheckPR ansible-core version definition (#1403)
  - upstream CI: Fix nightly and azure-pipelines to use version map (#1402)
  - Sysaccount management (#1398)
  - pre-commit: Update pre-commit repo versions (#1394)
  - ipacert: Fix tests for inexistent certificate (#1392)
  - Add capability sys admin to fix dbus broker in systemd 258 (#1387)
  - ipadnsrecord: Allow setting any IP address if create_reverse is false (#1382)
  - Fixes several linter issues for recent tool versions. (#1380)
  - test_backup.yml: Fix evaluation of 'list = False' and 'list = True' v2 (#1379)
  - Update Ansible version in Upstream CI (#1377)
  - test_backup.yml: Fix evaluation of 'list = False' and 'list = True' (#1376)
  - Add support for passkey (#1372)
  - Prepare playbooks for ansible core 2.19 (#1369)

Detailed changelog for 1.16.0 since 1.15.1 by author
----------------------------------------------------
  2 authors, 36 commits

Rafael Guterres Jeffman (28)

  - Fix Ansible warnings in Firewalld zone testing tasks
  - ipadnsrecord: Allow setting any IP address if create_reverse is false
  - New passkeyconfig management module
  - ipauser: Add support for 'passkey' in 'user_auth_type'
  - ipaservice: Add support for 'passkey' in 'auth_ind'
  - ipahost: Add support for 'passkey' in 'auth_ind'
  - ipaconfig: Add support for 'passkey' in 'user_auth_type'
  - tests: Add fact for passkey support
  - upstream ci: Use version_name for CheckPR labels
  - upstream ci: Fix Azure pipelines invalid names
  - upstream CI: Fix CheckPR ansible-core version definition
  - upstream CI: Fix Azure nightly pipelines to use version map
  - pre-commit: Update pre-commit repo versions
  - upstream CI: Update Ansible version for c9s
  - pytest: update to work with recent Python
  - pylint: Add list of upper case constants to setup.cfg
  - ansible-lint: Fix Jinja error
  - ansible-lint: Fix deprecation warning with bool and omit
  - pylint: Fix pylint 3.3.8 issues
  - requirements.txt: Add setuptools
  - ansible-docs: Update versions for ansible-doc-test checks
  - linter: Pin Python version for ansible-lint
  - ipacert: Fix tests for inexistent certificate
  - ci: Update ansible-core to 2.18 in CI
  - tests service: Fixes evaluation of 'Keytab = True'
  - ansible-core 2.19: 'upper' and 'lower' make lists into strings
  - ansible-core 2.19: Templates and expressions must use trusted sources
  - ansible-core 2.19: when clause don't automatically convert to bool

Thomas Woerner (8)

  - README-role.md: Fix typo in action description
  - iparole: Add sysaccount member support
  - Cert tests: Do not fail on new dogtag profile not found error message
  - New sysaccount management module
  - Dockerfiles c8s,c9s,fedora-latest and fedora-rawhide: Install hostname
  - infra/image/shdefaults: Add capability SYS_ADMIN for systemd 258
  - test_backup.yml: Fix evaluation of 'list = False' and 'list = True' v2
  - test_backup.yml: Fix evaluation of 'list = False' and 'list = True'

