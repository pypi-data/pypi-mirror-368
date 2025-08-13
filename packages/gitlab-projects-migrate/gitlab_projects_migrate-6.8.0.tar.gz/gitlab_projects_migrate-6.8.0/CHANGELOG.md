# Changelog

<a name="6.8.0"></a>
## [6.8.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/6.7.0...6.8.0) (2025-08-12)

### 🐛 Bug Fixes

- **entrypoint:** improve limitations outputs upon '--dry-run' ([e61e885](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e61e8850828887ee035178cd181c18ad2f2c2e70))
- **entrypoint:** implement GitLab Packages partial migration safeties ([a92553f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a92553fea3fd110f9bc307f1cb08531aca370900))
- **entrypoint:** implement GitLab Packages duplicates safeties ([8bc12b6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/8bc12b64bde7f58bc06fd8fddeb5b55512b6ce5b))
- **entrypoint:** validate packages count after packages migration ([93a54bb](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/93a54bbf3b06159aa191ebc61766a998bc26cdc0))

### ⚙️ Cleanups

- **pre-commit:** migrate to 'pre-commit-crocodile' 6.1.0 ([cec6bcf](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/cec6bcfa72b0042928db40ea4b3e7e49ea4067a4))

### 🚀 CI

- **gitlab-ci:** implement GitLab tags protection jobs ([7410796](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7410796512f36b7979fdf86337a20eb8ea104740))
- **gitlab-ci:** remove redundant 'before_script:' references ([a5d2257](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a5d2257d5fd6efdc898cbea7244e53974ca851f3))


<a name="6.7.0"></a>
## [6.7.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/6.6.0...6.7.0) (2025-07-27)

### ✨ Features

- **entrypoint, humanize:** show project human sizes upon export ([c9ab0cf](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c9ab0cf3f2371ac2687532578a246f5b470ca7a8))
- **gitlab:** detect group or project runners as limitations ([0f7aba3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/0f7aba340e01d86f70dd2d8a43b050bfb3fe2362))
- **gitlab:** ignore paused / inactive GitLab Runners limitations ([5fe326a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5fe326ac13a8fa92ba852a04583d84a7df6a3dd2))

### 🐛 Bug Fixes

- **entrypoint:** resolve user projects list type handlings ([b3e16e8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/b3e16e84698c0c0a7ea269cb3526d0734f108ff7))
- **entrypoint:** resolve existing project overwrite parameter ([4354921](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/43549219d85aef27e0e1cb4f82d27b07fd27d3a9))
- **entrypoint:** resolve '--dry-run' usage after latest evolutions ([794c1f7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/794c1f72c2d3509cc66b994274faf49dfefbd0aa))
- **gitlab:** resolve 'Packages count' faulty warning output ([0ea2386](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/0ea238691734b17abb83b7b417fcc5bff46b39b9))

### 📚 Documentation

- **prepare:** prepare empty HTML coverage report if missing locally ([fdc47c6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/fdc47c6f8e2424aeb20a5add49374d8d98d977f7))


<a name="6.6.0"></a>
## [6.6.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/6.5.0...6.6.0) (2025-07-06)

### ✨ Features

- **setup:** add support for Python 3.13 ([b84bdbf](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/b84bdbf5ec51eb256274ef9c5e1e9eed4a0f66a0))

### 🐛 Bug Fixes

- **entrypoint:** resolve existing subgroup detection without leading '/' ([7dbae11](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7dbae1196eb913b5f233ab2e716cbc96efe058a0))

### 📚 Documentation

- **mkdocs:** embed coverage HTML page with 'mkdocs-coverage' ([384a0fc](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/384a0fca3305eaa386d54bc441872e96250b2ccc))
- **readme:** document 'mkdocs-coverage' plugin in references ([5ecac41](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5ecac41e678ec4247bc597a88a7ad773ffe157f0))

### 🧪 Test

- **platform:** improve coverage for Windows target ([c0d8200](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c0d82000ed1383480a7ce6270d2b4bcbf2b4271e))

### ⚙️ Cleanups

- **gitlab-ci, docs, src:** resolve non breakable spacing chars ([324472f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/324472f6c397032462a3c6adfa180e28f6df6e62))
- **strings:** remove unused 'random' method and dependencies ([7dd14e5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7dd14e5605f83b0e8a3a4b931ac0328148335aba))

### 🚀 CI

- **gitlab-ci:** bind coverage reports to GitLab CI/CD artifacts ([e6d5157](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e6d515798364fed0f5eed201105b97746c1ee1ec))
- **gitlab-ci:** configure 'coverage' to parse Python coverage outputs ([d086969](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/d086969238c1aca73e6657b0d80b347a08f0f12c))
- **gitlab-ci:** always run 'coverage:*' jobs on merge requests CI/CD ([3ff59ab](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/3ff59ab6c03e8e688439e471dbab1c13b133c184))
- **gitlab-ci:** show coverage reports in 'script' outputs ([59a0510](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/59a051046f7ea8539412fd5ab2056359361148eb))
- **gitlab-ci:** restore Windows coverage scripts through templates ([aaf81cb](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/aaf81cbbb27d8964b8b2d01f03c88d27a955732a))
- **gitlab-ci:** resolve 'coverage' regex syntax for Python coverage ([82ebf3e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/82ebf3e4d3ce744f038d08bed17cea59b363b5cf))
- **gitlab-ci:** resolve 'coverage:windows' relative paths issues ([02e3502](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/02e3502d4001860c887c632294e15c3537c7242a))
- **gitlab-ci:** run normal 'script' in 'coverage:windows' with 'SUITE' ([a5ebf59](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a5ebf59b7fdc194c27bb65edae6524b880717223))
- **gitlab-ci:** use 'before_script' from 'extends' in 'coverage:*' ([59726c8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/59726c8159d9227f3a457db709af13aeb92d4bc3))
- **gitlab-ci:** run 'versions' tests on 'coverage:windows' job ([fd2355b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/fd2355b58a903cd5de1b4e1ff3556864392d356c))
- **gitlab-ci:** fix 'pragma: windows cover' in 'coverage:linux' ([38c10a4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/38c10a46e0e4ec8efc451456dd1a4b74d9dd4bab))
- **gitlab-ci:** run 'colors' tests in 'coverage:windows' ([b522c3a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/b522c3a577306ee2fb9808d280f8caae9caa8a2c))
- **gitlab-ci:** add 'pragma: ... cover file' support to exclude files ([555112d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/555112d1ed628c2750a8c7bbfbd568333031db12))
- **gitlab-ci:** isolate 'pages' and 'pdf' to 'pages.yml' template ([aa30d85](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/aa30d857957c3bf8789b4c48fc1e45752914e993))
- **gitlab-ci:** isolate 'deploy:*' jobs to 'deploy.yml' template ([46f256d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/46f256d922e7c69d87654c789b50bd9c5ddbe6c5))
- **gitlab-ci:** isolate 'sonarcloud' job to 'sonarcloud.yml' template ([0d9dec6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/0d9dec66025fbc19e6b31100c52e4412180418a1))
- **gitlab-ci:** isolate 'readme' job to 'readme.yml' template ([41f2682](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/41f268287c1c74aa639a22c430bc4c235c6de22f))
- **gitlab-ci:** isolate 'install' job to 'install.yml' template ([ef64daf](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ef64daf015258c6009b7b40232cc2948edefd443))
- **gitlab-ci:** isolate 'registry:*' jobs to 'registry.yml' template ([d0dd7a5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/d0dd7a58372bbe1f8b41cdaaa235b6de84ec1be8))
- **gitlab-ci:** isolate 'changelog' job to 'changelog.yml' template ([8c2f345](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/8c2f3456de248ba3923ca71554d326baac3ab695))
- **gitlab-ci:** isolate 'build' job to 'build.yml' template ([727e452](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/727e4521c7a472876724d74116fd7378c2944d98))
- **gitlab-ci:** isolate 'codestyle' job to 'codestyle.yml' template ([518acc1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/518acc1128d072f8979e066a62d86383ef7000c1))
- **gitlab-ci:** isolate 'lint' job to 'lint.yml' template ([627eca4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/627eca4d4c2b982a8e71064ba0cc6ebe09829f39))
- **gitlab-ci:** isolate 'typings' job to 'typings.yml' template ([1af542f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/1af542f8c9758724584cb046a8dd87c33c3c34c0))
- **gitlab-ci:** create 'quality:coverage' job to generate HTML report ([75996a5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/75996a5c80f0ec09c79e8018c6fba04fc42682a4))
- **gitlab-ci:** cache HTML coverage reports in 'pages' ([1b5eda3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/1b5eda32d045e8f45894e5cd35501104498d2ac5))
- **gitlab-ci:** migrate to 'quality:sonarcloud' job name ([783317f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/783317f79808180a975458bd2a56d1265dcc542c))
- **gitlab-ci:** isolate 'clean' job to 'clean' template ([8a52d1c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/8a52d1c70549a0a3119ed4ab83211a3380d76401))
- **gitlab-ci:** deprecate 'hooks' local job ([43e626d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/43e626d12605c78f16ec6d1af5d3ab4cbcd4dbf7))
- **gitlab-ci:** use more CI/CD inputs in 'pages.yml' template ([d343d51](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/d343d51f9750e34e6ec2ef0e5ea8514ca5e9ffa7))
- **gitlab-ci:** isolate '.test:template' to 'test.yml' template ([832ae81](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/832ae818a0de7871dca84d6f524baa0745462811))
- **gitlab-ci:** isolate '.coverage:*' to 'coverage.yml' template ([5a1a138](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5a1a1387d2d86b1aa437255db0955b04b45a8aa8))
- **gitlab-ci:** raise latest Python test images from 3.12 to 3.13 ([dc5673b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/dc5673be9e098ab7fe524a75fe6dc72ea9ebaa44))
- **gitlab-ci:** migrate to RadianDevCore components submodule ([cb9b59f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/cb9b59fc8c33be50572cb226c58c57b722c31a4d))
- **gitlab-ci:** isolate Python related templates to 'python-*.yml' ([7603b9f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7603b9f0125b9d605c899dbafa1df30c1c39d13c))
- **gitlab-ci:** migrate to 'git-cliff' 2.9.1 and use CI/CD input ([3a7cac2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/3a7cac23387794edc343fb36363c4e833790a1e5))
- **gitlab-ci:** create 'paths' CI/CD input for paths to cleanup ([13b4daf](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/13b4daf7b92a2c93421d55596a6d4d5efb76bd42))
- **gitlab-ci:** create 'paths' CI/CD input for paths to format ([4841061](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4841061a2be69cae8be7d61fea0bef5cab94dae9))
- **gitlab-ci:** create 'paths' CI/CD input for paths to check ([69ffa7f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/69ffa7f127fa7bf61cd4c8e049fe2dc6f94b2333))
- **gitlab-ci:** create 'paths' CI/CD input for paths to lint ([390ca48](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/390ca485b04f8a0d85e49deb799f3eb495ab9d46))
- **gitlab-ci:** create 'intermediates' and 'dist' CI/CD inputs ([f46ab65](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f46ab655e0156a3fb061dfed10cc681ca67c52b1))

### 📦 Build

- **pages:** install 'coverage.txt' requirements in 'pages' image ([55a2f9c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/55a2f9cd4ee34bf3a4235a9866397ed95e837a0e))
- **requirements:** install 'mkdocs-coverage>=1.1.0' for 'pages' ([c1f2b9b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c1f2b9b861e0338941328e5221d95c7d489402c1))


<a name="6.5.0"></a>
## [6.5.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/6.4.1...6.5.0) (2025-06-09)

### 🐛 Bug Fixes

- **entrypoint:** strip spaces in '--normalize-names' usage ([01120b6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/01120b6cfd30fd76cf84a3b006b9350738e727c8))
- **entrypoint:** validate input group subgroups respect naming rules ([0049b8f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/0049b8fa57fe3295d2a6ee7915d1bb50fd3d60d9))
- **src:** resolve new Python typings issues and warnings ([d94ab96](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/d94ab96372e46ad73c82466e49ab71ddd1c1215a))
- **version:** migrate from deprecated 'pkg_resources' to 'packaging' ([f6d4150](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f6d415086fb8187b42b00a33c254976705c4c118))
- **version:** try getting version from bundle name too ([1f4ce9b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/1f4ce9b793325cb0dfc3d9451da6308a22a37a2f))

### ⚙️ Cleanups

- **entrypoint:** refactor sources and rework subgroup variables ([429c31b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/429c31b75a09a0a4bc05c790c21cf5a5dd2b66c3))
- **pre-commit:** update against 'pre-commit-crocodile' 4.2.1 ([071fd94](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/071fd949388906ee0e00f354a08a025a0591056c))
- **pre-commit:** migrate to 'pre-commit-crocodile' 5.0.0 ([d4094c5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/d4094c5ccbfc504b101931b3eff919b06e74ab43))
- **vscode:** install 'ryanluker.vscode-coverage-gutters' ([1e627ac](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/1e627acbf83d6c18759432461b5632cdef2bcde3))
- **vscode:** configure coverage file and settings ([8e277fe](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/8e277fe3cec531082db2d268db8454a632c8aa71))

### 🚀 CI

- **coveragerc, gitlab-ci:** implement coverage specific exclusions ([f7f780c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f7f780ccef037633914d18d0d6be7b7f266ced4e))
- **gitlab-ci:** remove unrequired 'stage: deploy' in 'pdf' job ([2d69be1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/2d69be13e8b711423ad9d4874cafb4af228659b3))
- **gitlab-ci:** improve combined coverage local outputs ([6bbecd3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/6bbecd3e11adbde56a382e431e6f9b309831d276))
- **gitlab-ci:** enforce 'coverage' runs tool's 'src' sources only ([b9ccd3b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/b9ccd3beadc3b8277da610cda9ab57ff3942684a))
- **gitlab-ci:** add support for '-f [VAR], --flag [VAR]' in 'readme' ([063537a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/063537abbdf43d8bc6c9f65bef620f1227606cb7))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@5.0.0' ([a40dc95](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a40dc951f84da3ddeeb582e695096d42a8b72d95))
- **gitlab-ci:** migrate to 'CI_LOCAL_*' variables with 'gcil' 12.0.0 ([9ffab18](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/9ffab1894ae02484f86ef35c23fd95641b63c07d))

### 📦 Build

- **requirements:** add 'importlib-metadata' runtime requirement ([137289b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/137289bea95809fa104662e7389ee0b16e06cce7))
- **requirements:** migrate to 'commitizen' 4.8.2+adriandc.20250608 ([b2095bb](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/b2095bbd3e6827b6bfd551e15b70145654cd96eb))


<a name="6.4.1"></a>
## [6.4.1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/6.4.0...6.4.1) (2025-05-31)

### 🐛 Bug Fixes

- **entrypoint:** use simple 'replace' instead of 're.sub' ([a98368e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a98368e385649e87bf4e6da33505b11fe4e598a2))
- **gitlab:** fixup project export status checks and failures ([410a56b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/410a56bbd552d593f18b2ea6ab6484ed652578ea))

### 📚 Documentation

- **license, mkdocs:** raise copyright year to '2025' ([012f5ab](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/012f5ab2d2752e428d53a4b8c0fafa9aa8be9eba))

### 🚀 CI

- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@4.1.0' ([d6ecc0f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/d6ecc0ff3f1fecd79f63ed18702a827dcaeb0bbe))


<a name="6.4.0"></a>
## [6.4.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/6.3.0...6.4.0) (2025-05-17)

### ✨ Features

- **cli:** implement '--normalize-names' to normalize names ([1e86d1f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/1e86d1f39dc322db63f0f679d1459718f15e43cf))
- **entrypoint:** unarchive input project directly after export ([58fb40f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/58fb40fb4023db229cbb083f2d57804549250a27))
- **entrypoint:** implement subgroups and projects progress indexes ([50ded87](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/50ded87d22b943d527c6011805aae6c8068f57ef))
- **entrypoint:** improve 'Ignored project packages: No packages found' log ([9745734](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/97457347d01526b2b57c5a3805befccc5eec7317))
- **entrypoint:** confirm project migration last after configurations ([d3a994e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/d3a994e6da29edf94fd7e34c459594f3aaef2b68))
- **gitlab:** implement GitLab export steps progress logs ([bc53c59](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/bc53c590899b848863945b5acc264146b5740aaf))
- **gitlab:** validate migrated project issues count ([56adf2f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/56adf2f1311510d1c40e82626667ed10e9419eb8))
- **gitlab:** validate migrated project badges count ([6eeee5b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/6eeee5b3cf8ef686a2963c360eff9dce269b6a12))
- **gitlab:** validate migrated project releases count ([b210112](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/b2101120853f5ec94983a2cd7da764a7aa6ee38f))
- **gitlab:** ignore migration differences of reset entities ([d6cacff](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/d6cacff0772e77eb109c33ebc92bdfc7c254b0e9))
- **gitlab:** resolve GitLab large group and subgroups import timeout ([668809b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/668809bd673924b50a80946187578c4a23da8ae7))

### 🐛 Bug Fixes

- **entrypoint:** detect confirmation without stdin user input ([bd5c239](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/bd5c2397028234dd9abb5bc7fb5c5e327997acbe))
- **entrypoint:** prevent existing output project name conflicts ([d913b0a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/d913b0a98c08d77ec87a5fb0f5551e4513c356e9))
- **entrypoint:** prevent existing group name conflicts ([e19e880](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e19e880099004e8857296e34fc31855cb76e5da6))
- **entrypoint:** normalize project path against GitLab rules ([e39577a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e39577a281af82b3a179052b57cee00829248ca6))
- **entrypoint, gitlab:** resolve existing project name recursive checks ([24f1d2f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/24f1d2fd89ab5289d432dd9aefcef3733889733d))
- **gitlab:** delay one second after changing project archive states ([dbfa2a7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/dbfa2a70eedfe204ed9170aa97ed7f22d1d948d2))
- **gitlab:** resolve project export status checks and failures ([f268c4e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f268c4e7b42d4e93f222ad278e44b2ee0125a854))
- **gitlab:** ignore unavailable input issues or merge requests differences ([f56053b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f56053b70b18d4d524ae51f873862b48b7cd1459))
- **gitlab:** check project migration lists twice to avoid rare timeouts ([7cd68b7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7cd68b76787403e5b5d57f13cac53ea7aea49044))
- **gitlab:** avoid differences detection of empty input projects ([4ea42f4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4ea42f495d9c50ec1f484e8128eac40d8f022b8e))


<a name="6.3.0"></a>
## [6.3.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/6.2.1...6.3.0) (2025-04-13)

### ✨ Features

- **entrypoint:** archive and unarchive input project during export ([a6236b6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a6236b6506c1bda8cc0c2a2bd747415b62a7c097))


<a name="6.2.1"></a>
## [6.2.1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/6.2.0...6.2.1) (2025-03-03)

### 🐛 Bug Fixes

- **gitlab:** resolve 'container_registry_enabled: null' corruptions ([0141125](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/0141125d2c53fa3608fb625874fb693a7f0fb86c))

### 🚜 Code Refactoring

- **cli:** handle 'rename_project_positional' in 'main' sources ([f192f09](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f192f092e4cd34e4f3d6bed6b26ea673f29ae0b1))


<a name="6.2.0"></a>
## [6.2.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/6.1.0...6.2.0) (2025-02-28)

### ✨ Features

- **entrypoint:** minor outputs codestyle improvements ([e4c7938](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e4c79384cc805a273310753d53c1298288c17a1c))
- **entrypoint:** archive migrated project if source is archived ([d416ee5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/d416ee5f265b720fa8b1ea11263129c141d4cea7))
- **entrypoint:** improve migration progress output logs ([2eada02](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/2eada021b4c6199569b479503dd4f4429e6a130b))
- **entrypoint:** add existing subgroup update header log ([5ca1f9f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5ca1f9f9dc9584c24a77060c27d5585f71d1966c))
- **entrypoint, gitlab:** validate migrated project items counts ([71bf9f4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/71bf9f4eba18cd9e12b976fef13ce353c0e537b1))
- **gitlab:** ignore unavailable input pipelines differences ([a1678b6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a1678b638954c99991eb76b7b41bbbfa2eb628aa))
- **gitlab:** ignore unavailable input packages differences ([aadabff](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/aadabff0e15ccab9082f40b3f922bfcc5cd03820))
- **gitlab:** ignore unavailable input snippets differences ([731185b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/731185b33594e3a51014eea98e4bbea5efe39f84))

### 🐛 Bug Fixes

- **entrypoint:** avoid group as user runtime error issue ([ecf25f0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ecf25f047f7a6d15dd3636646c774420140d53d6))
- **gitlab:** enforce support for old webhooks GitLab API ([2cd1042](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/2cd1042170d94682b1ea16a066828a658a665451))


<a name="6.1.0"></a>
## [6.1.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/6.0.0...6.1.0) (2025-02-10)

### ✨ Features

- **cli:** implement '--flatten-group' parameter to flatten projects ([4d395f3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4d395f3676bbc51c2a386e9b68879c7138310765))
- **cli:** implement '--migrate-packages' to migrate GitLab Packages ([8e5343f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/8e5343f43eb49621fd8cab936c671255237bffdd))
- **entrypoint:** show GitLab username upon authentication ([29cecda](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/29cecda5f2339bc2ab159f9805a8dee7c6894105))
- **entrypoint:** exit project migration normally if already existing ([b132727](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/b132727c60c3be737a37af3e3a13bbe06aa3ef45))
- **entrypoint, gitlab:** show already valid settings in green ([c694447](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c694447b8a6c54e8ef3bae71fcb25b9e6ef096a3))
- **entrypoint, gitlab:** implement GitLab limitations warning level ([5bb3054](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5bb30549b2885647eccbcf92c9731633e397a482))
- **gitlab:** ignore 'key not found: nil' from old GitLab exports ([ce43c6d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ce43c6d0f26e1e4eea30511a30432bd1da7ca501))

### 🐛 Bug Fixes

- **entrypoint:** prevent acces to projects shared with groups ([b4f82ce](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/b4f82ce68842506d19f4e3395faae281247463c3))
- **entrypoint:** resolve support for group input to user output ([e2ed784](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e2ed7841480b394b629c3aacf7e7abc123c90a36))
- **entrypoint:** prevent repeated '.', '-' or '_' in project names ([b6dad94](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/b6dad9442d7fcb80b9b1df90274571c7cf77f813))
- **entrypoint:** resolve personal projects migration with sudo permissions ([f4b5054](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f4b5054297a678e0d4ae7d1532e9b4cfb5b8d8d9))

### 📚 Documentation

- **docs:** use '<span class=page-break>' instead of '<div>' ([6619a4c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/6619a4cfa817d5164d3ef44696e20d959cfad488))
- **prepare:** avoid 'TOC' injection if 'hide:  - toc' is used ([491f649](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/491f6498ddc59bd910cd4e36034cce912488af41))

### 🎨 Styling

- **colors:** ignore 'Colored' import 'Incompatible import' warning ([d83c875](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/d83c875fafa5d630ff808329bf57d8349c0490da))

### ⚙️ Cleanups

- **entrypoint, gitlab:** minor Python codestyle improvements ([66e8953](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/66e8953b3984f0c48230b959f06a54397cbd8efe))
- **sonar-project:** configure coverage checks in SonarCloud ([8cfad86](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/8cfad8659c5b825042065a8076521c5b4deb53aa))

### 🚀 CI

- **gitlab-ci:** run coverage jobs if 'sonar-project.properties' changes ([cf87482](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/cf874827edb1c29cca83cfb60e3865a525be4df0))
- **gitlab-ci:** watch for 'docs/.*' changes in 'pages' jobs ([50e2874](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/50e287445f5001e0b213669895bbe5b5686da9dc))


<a name="6.0.0"></a>
## [6.0.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/5.3.1...6.0.0) (2025-01-01)

### ✨ Features

- **cli:** implement input project archive exports only mode ([cc02639](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/cc0263927b3c596c296b9f5caf05af4dd6096225))
- **entrypoint:** show projects description after '# ...' ([1fa46ca](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/1fa46ca2965dcd1ac8435d21d9389dd87c110543))
- **entrypoint:** allow empty description and custom indent in 'confirm' ([c852df3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c852df3f2b471d04b90854b75950b608ef8c35be))
- **entrypoint:** use '...' quotes in 'confirm' function ([123132b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/123132b9cf030b861cb73a1fdd47ac192a6b08b9))
- **entrypoint:** list limited features per line, then confirm ([bf06d06](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/bf06d0651fbdc73a6ff6d28ea93b44a37187b948))
- **entrypoint, gitlab:** show limited features items for analysis ([f9ac6ef](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f9ac6efb3ed0af1619735e98329785a97a8e7cd5))
- **main:** support '--update-description[s]' parameter ([98be116](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/98be11607d1819cc77f42e847bc3a619512e8c8c))

### 🐛 Bug Fixes

- **cli:** use package name for 'Updates' checks ([ef7dc06](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ef7dc06edb47dd03dfa00fac3893230f1939e53b))
- **cli, gitlab:** synchronize repository default branch after migration ([fcc204a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/fcc204a5cfbc12f5dffa6e7e15998c06c7ce7929))
- **cli, gitlab:** indent configurations under input / output items ([c307c3b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c307c3ba328acef1f53c17cc872c1040db5c77e5))
- **entrypoint:** prevent name conflicts upon same namespaces migration ([16ffc28](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/16ffc28e4f360b11211a2a2d8f3dba1a99b7a5a7))
- **entrypoint:** add missing '--archive-sources' handlings for groups ([6ce6af0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/6ce6af032e948d7f822c08678310446d61fafd0b))
- **gitlab:** wait 1 second before group or project deletion checks ([204b654](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/204b654e1bcc43cdc14056f78070187c3a9683c2))
- **gitlab:** wait 60 seconds for large groups creation ([a496990](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a496990463dcc90aa6b9c3876deb94cc9d2e358d))
- **gitlab:** wait 300 seconds for a successful export download ([4033c37](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4033c37b3fef268f98ed4d7cfe31aeb7d7048b5f))
- **gitlab:** support GitLab Premium delayed project/group deletions ([7af95fe](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7af95fe3689da7ccb1ffa5c8f9bf6343f2c40695))
- **main:** ensure 'FORCE_COLOR=0' if using '--no-color' flag ([29eaa67](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/29eaa6767894804b31887628d10421a1c396c0a8))

### 📚 Documentation

- **assets:** prepare mkdocs to generate mermaid diagrams ([084f652](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/084f652f90eb4264b8ab7e1bff9e5159b6796a2c))
- **cliff:** improve 'Unreleased' and refactor to 'Development' ([61970f0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/61970f0c31cfbbc90ac37d316a56a8a76e0ba8ea))
- **covers:** resolve broken page header / footer titles ([18c659a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/18c659a05be0718fb78826a0a1ed14e4e5dcd478))
- **custom:** change to custom header darker blue header bar ([829af84](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/829af84c72df742c7d42cb847f6f40842013bf77))
- **docs:** improve documentation PDF outputs with page breaks ([994bbdf](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/994bbdfe3e81803b14ff9c8729821c7978170358))
- **mkdocs:** enable 'git-revision-date-localized' plugin ([bbacff0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/bbacff0de2c5395b07246a6dcc0129eb08d50ecb))
- **mkdocs:** change web pages themes colors to 'blue' ([5a681da](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5a681da5babbf7a70415fed6a4e864dbc9cc6a9e))
- **mkdocs:** fix 'git-revision-date-localized' syntax ([40c6434](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/40c6434596230cfe2ffd073a95fa6400268e8e5b))
- **mkdocs:** migrate to 'awesome-pages' pages navigation ([30a4593](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/30a4593592efd1e3c6fc42341e2412e4a60e90bc))
- **mkdocs:** change 'auto / light / dark' themes toggle icons ([e22175d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e22175d256839bd048c15f86d0240648a84d2108))
- **mkdocs:** enable and configure 'minify' plugin ([4edff1d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4edff1d830e1f10c2c3bb9ffaf3988370df3d383))
- **mkdocs:** install 'mkdocs-macros-plugin' for Jinja2 templates ([0c9106b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/0c9106bb30394067529c8ff776c2bf330e45e257))
- **mkdocs:** enable 'pymdownx.emoji' extension for Markdown ([123eec2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/123eec2fe61ce2105846e992009a03a688da6f52))
- **mkdocs:** implement 'mkdocs-exporter' and customize PDF style ([e743ce1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e743ce11e9a27facec8bfef8fc553ee8e6672b7d))
- **mkdocs:** set documentation pages logo to 'solid/code' ('</>') ([e88b4d3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e88b4d3d0e31ca60bfececa4be901e1112ef973b))
- **mkdocs:** enable 'permalink' headers anchors for table of contents ([57c540c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/57c540ce1f637cf46ddac5e21c110f3c1219aef4))
- **mkdocs:** prepare 'privacy' and 'offline' plugins for future usage ([e2ce00a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e2ce00a1fb5bc07d2b6185f42dcd47c448e84786))
- **mkdocs:** disable Google fonts to comply with GDPR data privacy ([942ded7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/942ded7250ca6772e08c2704017c611cc7ea645c))
- **mkdocs:** implement 'Table of contents' injection for PDF results ([68a8138](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/68a8138ebe0fd28ce57f5d3ee06912fd8b405ad7))
- **mkdocs:** enable 'Created' date feature for pages footer ([fef4993](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/fef4993572b45a6d64e9efbf6f4402512a03cf1e))
- **mkdocs:** add website favicon image and configuration ([38660e3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/38660e3b4abb287505a96bbee1c0c7812f34e3b9))
- **mkdocs:** implement 'book' covers to have 'limits' + 'fronts' ([bda76e2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/bda76e24a4132fdbb92c50e828c7212c13e19956))
- **mkdocs:** isolate assets to 'docs/assets/' subfolder ([dd8553a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/dd8553aac3d6eda6e3abc05b8469c4d86839c14e))
- **mkdocs:** exclude '.git' from watched documentation sources ([b1c3420](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/b1c34200b572bf55f56335eadb73045abdfef332))
- **mkdocs:** minor '(prefers-color-scheme...)' syntax improvements ([483cfff](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/483cfffc642d6c45b91fab468180cd3bfd8260af))
- **mkdocs:** remove 'preview.py' and 'template.svg' files exclusions ([711dac4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/711dac43fd539119ebdbd5d0fa00d2e7ebf1fab7))
- **mkdocs, pages:** use 'MKDOCS_EXPORTER_PDF_OUTPUT' for PDF file ([23c4165](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/23c41651c0d33157a7b7c215f724e6afd4b9e7a4))
- **mkdocs, prepare:** resolve Markdown support in hidden '<details>' ([3e666b9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/3e666b91a410ebc4238e6240a67f4894e1b6c3dc))
- **pages:** rename index page title to '‣ Usage' ([defa9fb](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/defa9fbded7ae7fa1946e0d9106a29408b17034a))
- **pages:** rename PDF link title to 'Export as PDF' ([752e41d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/752e41d692cdddc628e2b9e32cf8acd3fd04b797))
- **pdf:** simplify PDF pages copyright footer ([1bc1589](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/1bc158912e657f45e5e5e9d128bfe144a4d10de5))
- **pdf:** migrate to custom state pseudo class 'state(...)' ([7be21f7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7be21f742ec5920aaf1f635e6efb08155a8417e1))
- **pdf:** avoid header / footer lines on front / back pages ([b075999](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/b0759999ffea8bc5d872ccd866d85dc679d14b2d))
- **pdf:** minor stylesheets codestyle improvements ([20c0466](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/20c04667721f6e2707030c916c09707f06010e7f))
- **pdf:** reverse PDF front / back cover pages colors for printers ([6ec5a93](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/6ec5a93b34a645e12f387eee559a5e1b4ac3939e))
- **prepare:** regenerate development 'CHANGELOG' with 'git-cliff' ([dae8d4c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/dae8d4c7a9a6c7b949307196b618c39444ff84a4))
- **prepare:** avoid 'md_in_html' changes to 'changelog' and 'license' ([ef17a50](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ef17a5088893f5c7167bcbcac93916f40bd762df))
- **prepare:** fix '<' and '>' changelog handlings and files list ([6d8ca34](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/6d8ca34e4604ec19d4fa2fc6a99cd069ac510da5))
- **prepare:** implement 'About / Quality' badges page ([bc0b823](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/bc0b823a2e8d646ab0261d7cdb993d33417c5ac1))
- **prepare:** improve 'Quality' project badges to GitLab ([8fface0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/8fface0f1f2b92ef360b518b638c69dddd71b6ef))
- **prepare:** use 'docs' sources rather than '.cache' duplicates ([63bb28f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/63bb28fcb13b302178961e706e68aca390a24d0c))
- **prepare:** resolve 'docs/about' intermediates cleanup ([a4a9e9e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a4a9e9ebb111f6a2e984885964be256d262bfc65))
- **prepare:** add PyPI badges and license badge to 'quality' page ([35820d6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/35820d6979a1f9f7cec99d7ed35dcd644fdae5cf))
- **prepare:** avoid adding TOC to generated and 'no-toc' files ([5b80769](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5b80769eb85ba915e8a8a5a86f037ded846b4955))
- **prepare:** use 'mkdocs.yml' to get project name value ([144e542](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/144e5428451b5e96ed8fb5a5f6fef994cc180ffa))
- **readme:** add 'gcil:enabled' documentation badge ([5abc43d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5abc43d8aa824b59c00b3fc819542ffbf0a74330))
- **readme:** add pypi, python versions, downloads and license badges ([3726476](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/3726476a9d094d218661d03a638f68311b6bed35))
- **readme:** add '~/.python-gitlab.cfg' section title ([411f8b7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/411f8b71f1be31b0936b57844d71f2652ea12485))
- **robots:** configure 'robots.txt' for pages robots exploration ([9bb91ed](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/9bb91ed8d2b67739c47b97d82fe32063fabc0978))
- **stylesheets:** resolve lines and arrows visibility in dark mode ([ac19dde](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ac19dde3a28380ee53f08bfe85b831875a765db3))
- **templates:** add 'Author' and 'Description' to PDF front page ([26c49d1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/26c49d156d8e1fffca334fbb7aa09a1a02bdca93))
- **templates:** add 'Date' detail on PDF front page ([1545a26](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/1545a262aafc1d9d41b19f493203ad1954a2d9c9))
- **templates:** use Git commit SHA1 as version if no Git tag found ([2174692](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/21746922aefa6cb076ebd88e426569c29b452451))

### 🧪 Test

- **test:** fix daily updates coverage test syntax ([7e305e8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7e305e87984bf2bdd503a860aba23efd33a3ac55))

### ⚙️ Cleanups

- **gitignore:** exclude only 'build' folder from sources root ([f90614c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f90614cc3cfab83550c2d710e0d89688d0f8ebef))
- **gitignore:** exclude '/build' folder or symlink too ([b507a47](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/b507a4752fe7becef03900aacd4b3b41658288ce))
- **sonar:** wait for SonarCloud Quality Gate status ([d1e2f56](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/d1e2f56518d339434932c94d3d10d353705d20d9))
- **src:** resolve 'too-many-positional-arguments' new lint warnings ([6544a3d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/6544a3de6ace96b7753be70220c93db1837eefbc))
- **vscode:** use 'yzhang.markdown-all-in-one' for Markdown formatter ([eebd0fe](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/eebd0fee6dcddf00a0ff792f51d6e46e7a237896))

### 🚀 CI

- **gitlab-ci:** prevent 'sonarcloud' job launch upon 'gcil' local use ([0ae3920](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/0ae3920447a4065f284430d764f6db688ca251a6))
- **gitlab-ci:** run SonarCloud analysis on merge request pipelines ([1d8596f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/1d8596fd1ed7c5d2801d83beb9d4820ddad66000))
- **gitlab-ci:** watch for 'config/*' changes in 'serve' job ([92c604a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/92c604a52f6994448a9980b4ed9b0b2de63168d8))
- **gitlab-ci:** fetch Git tags history in 'pages' job execution ([77a53c2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/77a53c2a69f39d8d705c1f3437d4b9122f045e66))
- **gitlab-ci:** fetch with '--unshallow' for full history in 'pages' ([48849e4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/48849e4b55e65a515adcb2ca32165f0404fe91b4))
- **gitlab-ci:** enforce 'requirements/pages.txt' in 'serve' job ([9f5279b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/9f5279bf34ce011c64e50ab3faf8f6f7cb4dcf04))
- **gitlab-ci:** add 'python:3.12-slim' image mirror ([42baf94](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/42baf94ea6ee20807792a98bec646c4152fa531b))
- **gitlab-ci:** inject only 'mkdocs-*' packages in 'serve' job ([e921142](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e9211423dfa86f6beac6a1b011f8d55fc0c1c3fc))
- **gitlab-ci:** install 'playwright' with chromium in 'serve' job ([ce2f709](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ce2f709165b24151bbfdf0aa98f4cc43c1e19f73))
- **gitlab-ci:** find files only for 'entr' in 'serve' ([a43e0c9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a43e0c9209fbd0595a4d5fb02a00ffa54d2383ba))
- **gitlab-ci:** improve GitLab CI job outputs for readability ([58115a1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/58115a1495f85f0ea82227a6460a5d8464ad5062))
- **gitlab-ci:** deploy GitLab Pages on 'CI_DEFAULT_BRANCH' branch ([97205a9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/97205a9834c34b6c6f433e9e73d32fe82377ef87))
- **gitlab-ci:** ignore 'variables.scss' in 'serve' watcher ([5434b1b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5434b1b4f27e63c0fd7c09627f05fb4392ee2f69))
- **gitlab-ci:** preserve only existing Docker images after 'images' ([7dafbce](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7dafbcecb49abe1ed2e2d3561b927adfab30ad61))
- **gitlab-ci:** use 'MKDOCS_EXPORTER_PDF_ENABLED' to disable PDF exports ([d0679b6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/d0679b622550621d1fb2219fe2a967ed0cbbe2c5))
- **gitlab-ci:** run 'pages' job on GitLab CI tags pipelines ([0f3eecc](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/0f3eecc3577d8c7273682008e54a03a68ad6c2e5))
- **gitlab-ci:** isolate 'pages: rules: changes' for reuse ([300d463](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/300d46337ecfa340546f5a347a841fe2282df8fa))
- **gitlab-ci:** allow manual launch of 'pages' on protected branches ([249a187](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/249a187ac2181647c14133afe5fc48d54b40ea3c))
- **gitlab-ci:** create 'pdf' job to export PDF on tags and branches ([d45f4e3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/d45f4e3dadff2d9a8328567b06515bd9458e80f5))
- **gitlab-ci:** implement local pages serve in 'pages' job ([1b6c9ad](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/1b6c9ad545aefc1813806fe6dfd68243d8a64a1b))
- **gitlab-ci:** raise minimal 'gcil' version to '11.0' ([8067971](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/80679711f1381d759bfc81304b60f4ae18ad1ccc))
- **gitlab-ci:** enable local host network on 'pages' job ([353fade](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/353fade903ad599e299d038d655e81cf51452672))
- **gitlab-ci:** detect failures from 'mkdocs serve' executions ([c81b44a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c81b44a8671cf39f9de08f96c6c2bab3297d80e6))
- **gitlab-ci:** refactor images containers into 'registry:*' jobs ([4a52c3a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4a52c3a226b923333a8216c25387b63dd16e10d1))
- **gitlab-ci:** bind 'registry:*' dependencies to 'requirements/*.txt' ([4238a86](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4238a86fda0806c59254232e0b8883c115a1b311))
- **gitlab-ci:** avoid PDF slow generation locally outside 'pdf' job ([37ecf85](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/37ecf857f9cf0dc2d7ab44a51e4fc077ff0426df))
- **gitlab-ci:** validate host network interfaces support ([af12837](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/af128377be709b3abe03a910db2ed731726af835))
- **gitlab-ci:** enable '.local: no_regex' feature ([89f7cd8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/89f7cd8042a20e745eb354c60c56c5790e23ab67))
- **gitlab-ci:** append Git version to PDF output file name ([fd446f9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/fd446f975a8b3ef56cbfbb544c9c299f2f7323a1))
- **gitlab-ci:** rename PDF to 'gitlab-projects-migrate' ([3f82c91](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/3f82c91a9ce4be917b552ec5565addb83f519eba))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@4.0.0' ([bb6ae39](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/bb6ae39afb02d9f9f177841d2a75fce964f73454))
- **gitlab-ci:** ensure 'pages' job does not block pipeline if manual ([963f703](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/963f70363408ae174cd8d56a483a10ecf574ccfb))
- **gitlab-ci:** change release title to include tag version ([e174cf2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e174cf2ac8c1416d52ef276e67a27cf51da15d2f))

### 📦 Build

- **build:** import missing 'build' container sources ([2c0051e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/2c0051e89e182c283d43978971a4363cc3234290))
- **containers:** use 'apk add --no-cache' for lighter images ([9caf832](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/9caf8324e8f0efc67da59af60ff4452185d822d9))
- **pages:** add 'git-cliff' to the ':pages' image ([d4b495b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/d4b495b91a4d71a0c97df2d5341fb72ca6dc56a9))
- **pages:** migrate to 'python:3.12-slim' Ubuntu base image ([a050260](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a05026076e816c88579957c91030e94e93a2c798))
- **pages:** install 'playwright' dependencies for 'mkdocs-exporter' ([60216a7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/60216a70203ebb08ebaad7feedc9e62bbdfe826a))
- **pages:** install 'entr' in the image ([dc49e78](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/dc49e782952686561d01d67d4ece1eade3ca18f9))
- **requirements:** install 'mkdocs-git-revision-date-localized-plugin' ([cd1245a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/cd1245aba59ba9cd266df9bf7d898dfad7851a0a))
- **requirements:** install 'mkdocs-awesome-pages-plugin' plugin ([8e0a6d8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/8e0a6d88a8e75252e0e2a78b059b1ab9e729f5b5))
- **requirements:** install 'mkdocs-minify-plugin' for ':pages' ([ecb9486](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ecb94863baa84d01e74410fe78f8d50424c6c032))
- **requirements:** install 'mkdocs-exporter' in ':pages' ([2c04dc2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/2c04dc25a60d1d32684e4616e91eddc02a85415e))
- **requirements:** migrate to 'mkdocs-exporter' with PR#35 ([d98f294](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/d98f294ce5a472fdde5929a33e37fc22b6d302cd))
- **requirements:** upgrade to 'playwright' 1.48.0 ([eca8f8c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/eca8f8c642ce689e8b84d822e139a92f99025f4e))
- **requirements:** migrate to 'mkdocs-exporter' with PR#42/PR#41 ([fb0f873](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/fb0f87376d0ee3333392be89eea86e17048570c7))


<a name="5.3.1"></a>
## [5.3.1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/5.3.0...5.3.1) (2024-08-25)

### ✨ Features

- **updates:** migrate from deprecated 'pkg_resources' to 'packaging' ([a04cd3f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a04cd3fb6432db028b74730453a6de3bf1fe5cc2))

### 📚 Documentation

- **mkdocs:** implement GitLab Pages initial documentation and jobs ([4077cf2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4077cf2279a6b41f73b529027503be6137db34b7))
- **readme:** link against 'gcil' documentation pages ([4d192ae](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4d192ae2396c0f27c76304becb6331fd1ac7eaac))

### ⚙️ Cleanups

- **commitizen:** migrate to new 'filter' syntax (commitizen#1207) ([f09adcc](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f09adccef149a31f219a7373b2b4ddb6550d7fbf))
- **pre-commit:** add 'python-check-blanket-type-ignore' and 'python-no-eval' ([db8336b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/db8336b2ba83b0db38e74aa043c2c0a3320f25e5))
- **pre-commit:** fail 'gcil' jobs if 'PRE_COMMIT' is defined ([658d2cd](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/658d2cd2123b1b5d9272b2130c191469540e420d))
- **pre-commit:** simplify and unify 'local-gcil' hooks syntax ([2fc9cdb](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/2fc9cdb663e0762452f82cd906c0e8c0404e5ec3))
- **pre-commit:** improve syntax for 'args' arguments ([75cdc0b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/75cdc0b2e5af2947295f288f3705a32d0b3c2a02))
- **pre-commit:** migrate to 'run-gcil-*' template 'gcil' hooks ([f81d11c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f81d11c9af1c293d0b8f9b04cb39fe82036ac013))
- **pre-commit:** update against 'run-gcil-push' hook template ([505b5b5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/505b5b513a6f6853dcdd07585149bdaee9594c33))
- **pre-commit:** migrate to 'pre-commit-crocodile' 3.0.0 ([a7a93ac](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a7a93ac11aaf452f97e5af720236533858a36864))

### 🚀 CI

- **containers:** implement ':pages' image with 'mkdocs-material' ([623c9bb](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/623c9bb14ea63a6904d86411e4654e8fb238ecbd))
- **gitlab-ci:** avoid failures of 'codestyle' upon local launches ([9872de6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/9872de62b036b9d58ea71128b164b62d55b93d91))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@2.1.0' component ([88d8ab1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/88d8ab14caf43f3535723ad279946cfd95ec350d))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@3.0.0' component ([cd1e3be](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/cd1e3bedbdd3506e2dd562d63fd8682f17145988))


<a name="5.3.0"></a>
## [5.3.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/5.2.0...5.3.0) (2024-08-21)

### 🐛 Bug Fixes

- **package:** fix package name for 'importlib' version detection ([4310eeb](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4310eebe61df590558817480db0307da8db68c1e))
- **platform:** always flush on Windows hosts without stdout TTY ([336fd2d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/336fd2d751e81be383d7442eaabf98be9e189133))

### 📚 Documentation

- **readme:** add 'pre-commit enabled' badges ([3ae46f3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/3ae46f30c50888138d0ff19339e9786eb97ba85e))
- **readme:** add SonarCloud analysis project badges ([79f0c09](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/79f0c09a047968d89291855af7df27f11e6f827c))
- **readme:** link 'gcil' back to 'gitlabci-local' PyPI package ([84f65e2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/84f65e2271a164a6132edda33be30c2a47d6a521))

### ⚙️ Cleanups

- **commitizen:** migrate to 'pre-commit-crocodile' 2.0.1 ([1ed854f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/1ed854ff78ad46b90d142a78dce1534a644e09d3))
- **gitattributes:** always checkout Shell scripts with '\n' EOL ([d48e1ac](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/d48e1aca3ad2b025fe00c603f9cf1200617a0c82))
- **gitignore:** ignore '.*.swp' intermediates 'nano' files ([e87a978](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e87a978998f4b23d002adbac8cd01b2a674dd630))
- **hooks:** implement evaluators and matchers priority parser ([7e48cc8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7e48cc8f7992e3e94fbc18ce33d10c413e4a5b9d))
- **pre-commit:** run 'codestyle', 'lint' and 'typings' jobs ([f8796e8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f8796e86f655151340fc5fe1a0d584eb0ba06a0a))
- **pre-commit:** migrate to 'pre-commit-crocodile' 2.0.0 ([f425805](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f4258050b866ac2cb5f057a1381bf35e5d671f86))

### 🚀 CI

- **gitlab-ci:** show fetched merge request branches in 'commits' ([7af39e4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7af39e444f545a128cbe9ef23673cd674caac14e))
- **gitlab-ci:** fix 'image' of 'commits' job ([2af9e4f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/2af9e4f1129ee02fda6105167132d446cb99062b))
- **gitlab-ci:** always run 'commits' job on merge request pipelines ([c36657f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c36657f883ae74312fbeb8638a07d16005383fd8))
- **gitlab-ci:** make 'needs' jobs for 'build' optional ([ed18d14](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ed18d1488d969edfb4c68ebee8cf5c98ed16c3cb))
- **gitlab-ci:** validate 'pre-commit' checks in 'commits' job ([ce816ea](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ce816eadfe6f53e15862bb4d64d678184de20d41))
- **gitlab-ci:** refactor images into 'containers/*/Dockerfile' ([f0cb573](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f0cb57386c5e96190fafdb99ca966a14f879c687))
- **gitlab-ci:** use 'HEAD~1' instead of 'HEAD^' for Windows compatibility ([2c7cb24](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/2c7cb24e0a3680ea1cea4750a4605540f76dcfbd))
- **gitlab-ci:** check only Python files in 'typings' job ([a7434b9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a7434b959d536212bea6394ad921aa04b4d95d49))
- **gitlab-ci:** implement SonarCloud quality analysis ([1ec376a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/1ec376a73765403b8d768cf57d031baa390221f5))
- **gitlab-ci:** detect and refuse '^wip|^WIP' commits ([3cd6108](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/3cd61087d7891e086541d27cafb67fb8811ec7b8))
- **gitlab-ci:** isolate 'commits' job to 'templates/commit.yml' ([08e9717](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/08e971789719b5863d0bbd3faee63b9d82730d43))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@2.0.0' component ([9bbe33e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/9bbe33e05a5657154e2f01faff4e6038a536d0e2))
- **gitlab-ci:** create 'hooks' local job for maintenance ([ab13810](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ab13810460c194dc0e4f8375dfb8e9528a83c909))
- **gitlab-ci, tests:** implement coverage initial jobs and tests ([81c5bad](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/81c5badb7f35a9325ba23b3e1874fffc6502f0bf))

### 📦 Build

- **pre-commit:** migrate to 'pre-commit-crocodile' 1.1.0 ([91138ae](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/91138ae288221a810db0cf1d3ccc2d55aecad6c0))


<a name="5.2.0"></a>
## [5.2.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/5.1.0...5.2.0) (2024-08-15)

### 🐛 Bug Fixes

- **setup:** refactor 'python_requires' versions syntax ([1313d2e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/1313d2e83633fec3142d3f5d07f460ae48b420dc))
- **🚨 BREAKING CHANGE 🚨 |** **setup:** drop support for Python 3.7 due to 'questionary>=2.0.0' ([c35db2f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c35db2f0a9ca741132579aee0a50830ebb5b50db))
- **setup:** resolve project package and name usage ([e247e21](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e247e218ae95f518e26b315e3bcac2b216ad061c))
- **updates:** ensure 'DEBUG_UPDATES_DISABLE' has non-empty value ([721c199](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/721c199898a6fde1fcc1c3aee35644063350229b))
- **updates:** fix offline mode and SemVer versions comparisons ([947dfbc](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/947dfbc3dc2d30c33957d719145aaa8bf0e55481))

### 📚 Documentation

- **cliff:** use '|' to separate breaking changes in 'CHANGELOG' ([f4b9a7e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f4b9a7eb7c786cbed38979921c457d6012d7866f))
- **license:** update copyright details for 2024 ([87d3a30](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/87d3a3056cc218d032c5d8978d7dbe385d3e5bf3))
- **readme:** add 'Commitizen friendly' badge ([6cfd434](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/6cfd43495e0bb63a9acd97d5adb30aeae50ccf8f))

### 🎨 Styling

- **cli:** improve Python arguments codestyle syntax ([4aedfed](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4aedfed4bfbb649a304e237bf31d13e169c2ac7e))
- **commitizen, pre-commit:** implement 'commitizen' custom configurations ([12c4300](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/12c4300a199f2074a47ae06835980b2ac83fe80d))
- **pre-commit:** implement 'pre-commit' configurations ([7300bde](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7300bde8691f4d1ae15a031f033f1352aa6561df))

### ⚙️ Cleanups

- **cli, package:** minor Python codestyle improvements ([50f3a98](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/50f3a98e14654d0627c60c9330dc7467342e2a14))
- **pre-commit:** disable 'check-xml' unused hook ([be305d3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/be305d376f3348996a82d6da149c85133867d5f0))
- **pre-commit:** fix 'commitizen-branch' for same commits ranges ([456a108](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/456a108cda41e3b9e250eeed5077970b9cacedaa))
- **setup:** refactor with more project configurations ([197125e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/197125e522d70e2db789ede73600ce2222310c67))
- **updates:** ignore coverage of online updates message ([9f273d9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/9f273d9fe49dddbe95746bb0af46550e766d2ab9))
- **vscode:** remove illegal comments in 'extensions.json' ([a691dbc](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a691dbc81ccddfbeb88252d4d8b7f36ef296e7a0))

### 🚀 CI

- **gitlab-ci:** watch for 'codestyle', 'lint' and 'typings' jobs success ([a9425db](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a9425db27bb16f12aa66906154680c266407164d))
- **gitlab-ci:** create 'commits' job to validate with 'commitizen' ([b2c8d00](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/b2c8d007872f14e3ff3c21c1f2adf204baf43941))
- **gitlab-ci:** fix 'commits' job for non-default branches pipelines ([4e3402e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4e3402ecd5a9a4fa2069e4bcfc75a58b98fa5a33))

### 📦 Build

- **hooks:** create './.hooks/manage' hooks manager for developers ([048b9f6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/048b9f6f12a900eb3064a04ef59cad1401fdaf37))
- **hooks:** implement 'prepare-commit-msg' template generator ([a16f1ce](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a16f1ceb465ef1959aed39126c1582cbbac327c3))
- **pre-commit:** enable 'check-hooks-apply' and 'check-useless-excludes' ([5fd439c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5fd439c73dde86aecadf1609e071c5dbf6f84b5d))


<a name="5.1.0"></a>
## [5.1.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/5.0.3...5.1.0) (2024-08-11)

### ✨ Features

- **cli:** implement '--no-color' to disable colors ([294fd18](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/294fd1885e302208d97ec3cd5cf9666aba996253))

### 🐛 Bug Fixes

- **package:** check empty 'environ' values before usage ([42b25d4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/42b25d43b69ab374104d01c07f8b7902f695a72f))
- **updates:** remove unused 'recommended' feature ([201ca49](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/201ca49df3888fda1ed9bfb46332c00648199a2b))

### 📚 Documentation

- **readme:** migrate from 'gitlabci-local' to 'gcil' package ([9c81cd8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/9c81cd82b6a538b2e11af76eee1e00dc9d9aafbc))

### ⚙️ Cleanups

- **cli:** resolve unused variable value initialization ([c6f99cd](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c6f99cde80c7aef1d2538e4a55601314b61ac7cd))
- **colors:** resolve 'pragma: no cover' detection ([64c028e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/64c028ea18079737fb26a8b9ab6cbb50f811e240))
- **platform:** disable coverage of 'SUDO' without write access ([6c1d314](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/6c1d3144acf88bfe36a30102b69cefcc2e75fc24))
- **setup:** remove faulty '# pragma: exclude file' flag ([03bb970](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/03bb970ac21e6385e86d33f5dec7e544ac94c6c2))


<a name="5.0.3"></a>
## [5.0.3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/5.0.2...5.0.3) (2024-08-10)

### ✨ Features

- **setup:** add support for Python 3.12 ([b72e9a1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/b72e9a178aefdc961e0fe87ece704b9bb5d3d4b2))

### 🎨 Styling

- **main:** declare 'subgroup' variable as '_MutuallyExclusiveGroup' ([3e1842c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/3e1842c5be3a189960b05a23a94b93c15dc23e93))

### 🧪 Test

- **setup:** disable sources coverage of the build script ([8e7ce06](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/8e7ce0695410df8ebce8a8fd432f38d4e4959062))

### 🚀 CI

- **gitlab-ci:** raise latest Python test images from 3.11 to 3.12 ([47da8d5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/47da8d5369331a2a033f62460428a07e4090c84c))
- **gitlab-ci:** deprecate outdated and unsafe 'unify' tool ([2a890ac](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/2a890ac178af80ed080ed5a41b20a40fc5e10b68))


<a name="5.0.2"></a>
## [5.0.2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/5.0.1...5.0.2) (2024-08-10)

### ✨ Features

- **gitlab-projects-migrate:** migrate under 'RadianDevCore/tools' group ([50ed087](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/50ed087e57116b044692ca2220e6c4ce21018a60))

### 🐛 Bug Fixes

- **settings:** ensure 'Settings' class initializes settings file ([beb96ff](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/beb96ff7336b23e248c1a83abb7ce2c2d4c89233))
- **src:** use relative module paths in '__init__' and '__main__' ([79e567e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/79e567e1c2d97d0f7bd48af84cf923fe40bc43eb))


<a name="5.0.1"></a>
## [5.0.1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/5.0.0...5.0.1) (2024-08-08)

### 🐛 Bug Fixes

- **cli:** fix syntax of '--reset-entities' argument variable ([5bb61f0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5bb61f02646871647dfa78fb22cb565c22e9146c))


<a name="5.0.0"></a>
## [5.0.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/4.1.2...5.0.0) (2024-08-08)

### 🛡️ Security

- **🚨 BREAKING CHANGE 🚨 |** **cli:** acquire tokens only from environment variables ([1cca6b8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/1cca6b8231e7a1bb8860a3033d086f2e38d0d035))

### ✨ Features

- **🚨 BREAKING CHANGE 🚨 |** **cli:** refactor CLI into simpler GitLab URL bound parameters ([495ccf3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/495ccf3b26c2934ffc36c02369547613d9bfd8e8))
- **cli:** implement '--confirm' to bypass interactive user confirmations ([640109c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/640109c63502e57de2c5fa86a5c43ae7b6e9006c))
- **cli:** support 3rd positional argument for '--rename-project' ([23a4e94](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/23a4e94245449f3b05b544d0b48ef8dde3524c0b))
- **cli:** add tool identifier header with name and version ([8dfd23f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/8dfd23f276f540d3f2bb27d99806e35d0496ca24))
- **cli:** implement '.python-gitlab.cfg' GitLab configurations files ([0782032](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/0782032dfa92ebbc29401ca79aa89377df888c2b))
- **cli, argparse:** implement environment variables helpers ([f660b3f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f660b3f3b5308c4b8b2de96a7856274228b5063f))
- **cli, gitlab:** implement '--available-entities' for migration ([c52056a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c52056acae4a24e2cbc26e0a71a71cd0a672d169))
- **🚨 BREAKING CHANGE 🚨 |** **cli, gitlab:** migrate from '--keep-members' to '--exclude-entities' ([fff8a55](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/fff8a552ad5dccbf885ded6ebcd6ee2b9246bf38))
- **cli, gitlab:** implement CI job token and public authentications ([c9a78f8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c9a78f88e359cb740afd80855f253b7533acd083))
- **cli, gitlab:** migrate to '--reset-entities' parameter name ([c8d3b19](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c8d3b19dab249a3b4c4ad34b3198db97944e3ab6))
- **entrypoint, gitlab:** implement 'Remove:' and 'Template:' entities ([6d90592](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/6d90592a92f928cb6f8a86bbd2a81d35e2d81d63))
- **gitlab:** migrate entities to 'Remove/' and 'Template/' ([91e1942](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/91e1942cb72d61e0a12e3fc606b09e383a22f708))

### 🐛 Bug Fixes

- **environments:** add missing ':' to the README help description ([3ae5b5d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/3ae5b5d2cb5355fe39eefedd2fb7d9c7339fe207))

### 📚 Documentation

- **cliff:** document 'security(...)' first in changelog ([e8499a9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e8499a949fa5a74ac6231e43c82e345d0923284f))
- **readme:** document '~/.python-gitlab.cfg' configuration file ([07c1d6b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/07c1d6be890c3134da2a074d638aa62c811acad5))
- **readme:** document projects copy and project renaming ([32107fd](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/32107fda7276ca59cd402b4c32837fafa91f667d))
- **readme:** document projects as templates copy and entities cleanups ([e525ca3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e525ca323fdbf5d4d9b468381f707d996f8d8d84))

### ⚙️ Cleanups

- **cli/main:** minor codestyle improvement of 'import argparse' ([fcd1716](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/fcd171612e83bc5f27419a3b8c7647d8b6bd5528))
- **gitlab:** remove unused 'type: ignore' and resolved TODO 'fixme' ([2905f9f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/2905f9f74c2c8e3db8bdd2348d3a730c82d3572d))
- **types:** cleanup inconsistent '()' over base classes ([c0150d6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c0150d66910f5899594e4c04156a94e7b6bb2339))

### 🚀 CI

- **gitlab-ci:** migrate from 'git-chglog' to 'git-cliff' ([77bc35b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/77bc35b96566c8dbe71afa455a77bf2d50840325))


<a name="4.1.2"></a>
## [4.1.2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/4.1.0...4.1.2) (2024-08-06)

### 🐛 Bug Fixes

- **entrypoint:** fix already existing checks if renaming project ([20c8268](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/20c8268bdf986cd2ae5a2efacedb74f2d60c98e7))
- **entrypoint:** fix already existing removal if renaming project ([303a798](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/303a798d59c85e09366501e5ca5a25b8330ccbf5))
- **gitlab:** wait 3 seconds after group and project deletions ([9957021](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/9957021bea497469c2f30fe723e472b0059dcde2))


<a name="4.1.0"></a>
## [4.1.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/4.0.3...4.1.0) (2024-08-04)

### ✨ Features

- **gitlab:** warn about 'Pipeline triggers', 'Webhooks', 'Project Access Tokens' ([760884f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/760884fe3ca1cef38ad1599ddff99ba7e967225d))

### 🐛 Bug Fixes

- **entrypoint:** fix project checks by path rather than by name ([98f4577](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/98f45779beb93a8f1e48e2bc16c0c944922443e6))


<a name="4.0.3"></a>
## [4.0.3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/4.0.2...4.0.3) (2024-06-11)

### 🐛 Bug Fixes

- **gitlab:** fix namespace detections upon '--dry-run' executions ([a331fb8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a331fb87e6732695935290c7979b30a23ddb0f8f))


<a name="4.0.2"></a>
## [4.0.2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/4.0.1...4.0.2) (2024-06-10)

### 📚 Documentation

- **chglog:** add 'ci' as 'CI' configuration for 'CHANGELOG.md' ([f2231d3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f2231d3015b366cb6815716f0c331777cef58013))

### 🚀 CI

- **gitlab-ci:** support docker pull and push without remote ([9118e38](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/9118e3809cc77ac5953a633b6bbec4094c786ee4))
- **gitlab-ci:** use 'CI_DEFAULT_BRANCH' to access 'develop' branch ([ffca219](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ffca2196436b01ebb9b55b94f5cc469e16f3faa9))
- **gitlab-ci:** change commit messages to tag name ([35b9df0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/35b9df0efa834817ef63be0704cdb6fda644f963))
- **setup:** update Python package keywords hints ([5f36462](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5f364625a50056b7ccd12031a73ece0b9503cdd5))


<a name="4.0.1"></a>
## [4.0.1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/4.0.0...4.0.1) (2024-05-27)

### 🐛 Bug Fixes

- **entrypoint:** resolve already existing nested subgroups check ([bf656d0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/bf656d0722fdf306e21458c93b17433640033a56))
- **gitlab:** resolve '.variables.list' on old GitLab instances ([483823e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/483823edcd9667bee6d7c732b224b5bb3fe8cbee))


<a name="4.0.0"></a>
## [4.0.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/3.1.0...4.0.0) (2024-05-26)

### ✨ Features

- **entrypoint:** improve outputs logs upon delections ([8da3ae1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/8da3ae126918b512e5b8b8d1245f3b56bccb6c18))
- **entrypoint:** identify already existing project, group, subgroup ([7baf7b3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7baf7b339958d8a72517654915ab42dbd11ebfd6))
- **entrypoint, gitlab:** detect and confirm export limitations ([797e469](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/797e469505d4b685c54701ca7553bb629290c3a8))
- **entrypoint, main:** implement '--rename-project' to rename project ([fdf447f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/fdf447f4bce3bff49f6a05df9375b25b9434b892))
- **main:** show newer updates message upon incompatible arguments ([5561849](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5561849746623a127ad4ad5e182619ad4d02221e))
- **main, entrypoint:** implement '--archive-sources' mode ([64dc73a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/64dc73aa16305666d8799f9d7b413a64e6ecabb5))

### 🐛 Bug Fixes

- **gitlab:** fix project import 'path_with_namespace' in dry run ([e4bf8e2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e4bf8e28f992d7d0e2ef4876c86623bcd31a61b2))
- **main:** exclusive '--archive-sources' and '--delete-sources' ([f29389e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f29389e59f1faabb61bb573cbe3e63a20dcb94d6))

### 📚 Documentation

- **readme:** add '--archive-sources' and '--delete-sources' examples ([59779ca](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/59779ca61361efe303c2be4712cb9bdfc68c921b))

### ⚙️ Cleanups

- **entrypoint:** turn 'confirm' function into generic handler ([5151afa](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5151afaa67a217da46bef4f1ad9745c4569198a7))


<a name="3.1.0"></a>
## [3.1.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/3.0.1...3.1.0) (2024-05-17)

### ✨ Features

- **entrypoint:** implement '--archive-exports FOLDER' to keep exports ([2c47fb7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/2c47fb7850a796c03f5cb07ec17833186f0af2ce))
- **entrypoint:** implement prompt confirmation upon deletions ([3430da0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/3430da052200cda1630cfd7a101fe9033c45a678))
- **requirements:** prepare 'questionary' library integration ([1a2877c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/1a2877c970adf054f9842be298bab8a3fe439194))

### 🐛 Bug Fixes

- **gitlab:** raise runtime error upon failed project imports ([38ffbb6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/38ffbb6947a0a79e7f38fe3abc116ffe0b0de5a2))
- **gitlab:** restore 'import_project' file argument as BufferedReader ([d2a6eaa](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/d2a6eaa7dbca713cbccabfb8e28d7290e2c4f9a2))

### ⚙️ Cleanups

- **gitlab:** ignore 'import_project' file argument typing ([edd0867](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/edd08673819429493a7ca3a6ad1f11fb9dbfd038))


<a name="3.0.1"></a>
## [3.0.1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/3.0.0...3.0.1) (2024-05-15)

### 🐛 Bug Fixes

- **entrypoint:** resolve 'output_namespace' assertion tests ([a7e48c9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a7e48c9887ab1691f9ffe70bef5626b969da555b))


<a name="3.0.0"></a>
## [3.0.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/2.1.0...3.0.0) (2024-05-15)

### ✨ Features

- **entrypoint:** always flush progress output logs ([e8067f2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e8067f21fd1b41f27d7f654235da5384f35c9b29))
- **entrypoint, gitlab:** adapt name for '--update-description' ([f3fe725](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f3fe72586753b096cbe00e33ffab02f2dbe75388))
- **entrypoint, gitlab:** add support for user namespace projects ([e5118a4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e5118a42e41355596da7c209265e47e39d8d01e7))
- **gitlab:** automatically wait for group and project deletions ([c998605](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c99860531de2495ebadca65943a4b52eae1caeb4))
- **main:** document optional '--' positional arguments separator ([aff6a17](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/aff6a171b1cedcc30bc4e6e916a094f5a7ec2609))
- **main, entrypoint:** implement '--delete-sources' final actions ([140ff3a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/140ff3aa69a16c57edff3e657e36ae65057ab7f2))
- **main, settings:** implement 'Settings' from 'gitlabci-local' ([dc36932](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/dc3693298446c2d64955b3617d13011b62418a85))
- **main, upgrades:** implement 'Upgrades' from 'gitlabci-local' ([3a1ae89](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/3a1ae8977feea33b9afb9a33b4ccf2b62b9fec63))
- **namespaces:** migrate 'Helper' class to 'Namespaces' class ([5a82589](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5a82589ff29fff3344f2297d98fe3eba7b7974f6))

### 🐛 Bug Fixes

- **entrypoint:** enforce against missing '.description' values ([9db9037](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/9db90379c38df0a25fd763863c13ad60faa9c23b))
- **entrypoint:** detect if GitLab actions can continue ([c1a8d2c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c1a8d2c074f65f23565ab66f5202a353af5303d4))
- **entrypoint:** minor Python codestyle improvement ([2e138e3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/2e138e39127afd6a7bd204d460e70f3d45d12987))
- **entrypoint:** use full paths instead of 'id' integer fields ([524eb14](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/524eb145846da12f5292024125b84617de6646e9))
- **entrypoint:** refactor to return no error upon final actions ([6367e89](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/6367e8988236b978197d9f8fefefe6be44665dbe))
- **entrypoint, gitlab:** resolve Python typings new warnings ([393e239](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/393e239134a1bd88d19ce50b92f64cc5f1432c3a))
- **entrypoint, namespaces:** add 'text' to handle empty descriptions ([005b50c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/005b50c12a169dad6aa69a884a8e1e69708c85bb))
- **gitlab:** get all members in 'project_reset_members' ([f2834a2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f2834a241fb07a1415436088b6c52ccc48515be7))
- **gitlab:** fix 'Any' and 'Optional' typings imports ([4af24ba](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4af24baed4772b37137d84d69aefde933222dc83))
- **gitlab:** try to get real group before faking in '--dry-run' ([70ea00d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/70ea00d3119f9619161b7c8d2329319bd4d21a23))
- **gitlab:** add 'description' field to fake project in '--dry-run' ([9b7bca1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/9b7bca16cccd2772dd4e4cd7bc6d7d6dc51f5adc))
- **gitlab:** accept deletion denials in 'project_reset_members' ([be12ff0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/be12ff0b9c3fd3bfe5380e99d04da37e0d204c61))

### 🧪 Test

- **version:** add 'DEBUG_VERSION_FAKE' for debugging purposes ([ae75971](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ae75971a49ceb55e46760316ab898f5b6a5037ec))

### 🚀 CI

- **gitlab-ci:** move 'readme' job after 'build' and local 'install' ([97d3ed0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/97d3ed02ab08e8db94ebde60ff4d32388c2a3438))
- **gitlab-ci:** handle optional parameters and multiline in 'readme' ([a720e9c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a720e9c9086bfdd92ed8f8dcff03ac3b81818e64))
- **gitlab-ci:** detect 'README.md' issues in 'readme' job ([f817eef](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/f817eef04fba14e2a6b97780876f186227d25e71))
- **gitlab-ci:** implement 'images' and use project specific images ([5475393](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5475393610cf67897736f9720da6e4faf10c779b))
- **gitlab-ci:** deprecate requirements install in 'lint' job ([4e03a36](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4e03a365d9c2e7efdb702d8e978bae76f7a8b6b2))
- **gitlab-ci:** support multiple 'METAVAR' words in 'readme' job ([2c571f6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/2c571f66d104faac58c5a8d63eeb99ec09d78b8e))


<a name="2.1.0"></a>
## [2.1.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/2.0.0...2.1.0) (2024-04-28)

### ✨ Features

- **entrypoint:** keep description if already contains group ([4c50766](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/4c50766886b6af5c76e1758016640bc00a183646))
- **entrypoint:** sort groups and projects recursively ([90e59a4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/90e59a49992aef0809b0d0aaaa3de23a6c89b06e))

### 🐛 Bug Fixes

- **entrypoint:** resolve input group for single project migration ([ce5c66e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ce5c66e4722914df467f3a8d6ceada5214a021c9))
- **entrypoint:** resolve input group detection for projects ([96ccad9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/96ccad9be44ab1a1592fd57f65aac9e6da8b05f9))


<a name="2.0.0"></a>
## [2.0.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/1.1.0...2.0.0) (2024-04-28)

### ✨ Features

- **cli:** isolate 'features/migration.py' to 'cli/entrypoint.py' ([b54de48](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/b54de488db64bd48447e50631047498de3f27aff))
- **entrypoint:** isolate 'group' function to 'subgroup' ([5436398](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/54363985d3e70493d62eb64073d6a75a7df3e008))
- **entrypoint, gitlab:** isolate 'GitLabFeature.Helper.subpath' ([a3d9f28](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a3d9f28c4f7872d237eda9c932658d09b503f605))
- **entrypoint, gitlab:** isolate 'GitLabFeature.Helper.capitalize' ([7a745e4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7a745e4cce19af66a1b6333007d368f5a67e3ffb))
- **entrypoint, gitlab:** implement output parent group creation ([c9218c3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c9218c383884ea1f9084e8bcc80e6466bde55768))
- **entrypoint, gitlab:** implement groups export/import handlings ([a2e6989](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a2e69896d693013dd127e87311fb5cc73bf0e263))
- **gitlab:** prepare group settings functions for future usage ([167962a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/167962a02f2167ee5c03e702b3c8ad51448182c6))
- **gitlab, migration:** refactor into GitLabFeature functions ([41436ec](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/41436ec1f327c3a5d907d5b8fbbc9603cf10a34c))
- **main:** isolate CLI argument into specific sections ([95ec817](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/95ec817167bef8bf09443909ea2fbfd66c6847ab))
- **main:** enforce 'output_group' value is always passed by CLI ([701c335](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/701c335e3feaefd89aea81d7244fd90c7a2e68fe))
- **main:** align 'RawTextHelpFormatter' to 30 chars columns ([c15bf79](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/c15bf79da3523d21747b101acc01a1796015712e))
- **main:** limit '--help' width to terminal width or 120 chars ([3fcaac0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/3fcaac09274dadc907b121207424b727a9180f15))
- **main:** add support for 'GITLAB_TOKEN' environment variable ([a8cae39](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/a8cae39731cf10df1b227e895cf31a90916c0d80))
- **main, entrypoint:** implement '--exclude-subgroups' filter ([377bff5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/377bff5f8f9479529f1f64a3f3d17a9d526eb482))
- **main, entrypoint:** implement '--exclude-projects' filter ([7c09032](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7c0903269ce3f31a287589e153c5cc582f159651))
- **main, entrypoint:** implement '--exclude-group' filter ([21a513c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/21a513c14941bdc088ef1a0b59bd5a61a19e8b15))
- **main, gitlab, migration:** refactor and add '--dry-run' ([afe7a8d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/afe7a8d60c3781fb6c781a324899ace9dc50e56f))
- **migration:** sort group projects in ascending 'path' order ([23232de](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/23232de186c041ff6692ea6124e545578369d153))
- **migration:** implement support for input project along group ([cd51b98](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/cd51b982c954ee81fd0afef5ccc014b276ceaa53))
- **migration:** implement nested projects migration support ([5639fca](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5639fca40b9744f3444fec3aa11fee104eafca67))
- **migration:** implement GitLab subgroups creation ([549f600](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/549f600f77c7e047217da0807f0096246f78a8f7))
- **settings:** change project/group descriptions color ([fb41f6c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/fb41f6c3761788ce03f90eca36a0fb44a1be9921))

### 🐛 Bug Fixes

- **entrypoint:** safeguard group handlings for '--dry-run' ([8202026](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/82020262e1f927db57b3b9479ea4d19e70a6a11c))
- **entrypoint, gitlab:** implement description to name fallbacks ([5524af7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5524af7b8b9d902436e908ab31e14bc68dd38134))
- **gitlab:** resolve '--dry-run' usage upon projects migration ([65c0cdb](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/65c0cdb6307e36992e2b04d18cd88dedf14d58d5))
- **main:** ensure GitLab token has been defined ([5f9cd0a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/5f9cd0a4534556a4046ae36fe0c626c032e2f39b))

### 🚜 Code Refactoring

- **entrypoint, gitlab:** isolate 'GitLabFeature.Helper.split_namespace' ([ffd519b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ffd519b4b51938c4f2cb122caa516e91c19c9ea4))
- **migration:** refactor into 'entrypoint' main function ([ac9990f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ac9990f2054ca853266433b0fed4c63bbbeb2139))
- **migration:** isolate project migration feature sources ([330fbe4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/330fbe4eaeca1f5d950ab7c9bbd6ec71709cf133))
- **src:** isolate all sources under 'src/' ([7f97146](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/7f97146a90627f66d3db435f90e566cc91fa6cfb))

### 📚 Documentation

- **readme:** regenerate '--help' details in 'README.md' ([0209976](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/02099760a523c8d1962c194801fd853f357c725d))
- **readme, cli:** minor project description improvements ([fbbb80a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/fbbb80a41c45a5d76dbddf08fa9fcbfcf9af5e16))

### 🎨 Styling

- **main,migration:** minor Python codestyle improvements ([8f4ece8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/8f4ece8a00391037f03914a68f6447a33e7e8913))

### ⚙️ Cleanups

- **src:** ignore 'import-error' over '__init__' and '__main__' ([fce4b15](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/fce4b152df1368a33a6625a3e22e8b4f412da8dc))

### 🚀 CI

- **gitlab-ci:** implement 'readme' local job to update README details ([02c6fad](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/02c6fad7db2b1acf03bdaeeec5486f32c37a7efe))
- **gitlab-ci:** disable 'typing' mypy caching with 'MYPY_CACHE_DIR' ([e9ce388](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/e9ce3887d682ef53c5f028134ded214b26d6b464))
- **gitlab-ci, setup:** migrate to 'src' sources management ([65dac94](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/65dac94835db84ac6eb4cc2163d0779a8f8a5761))


<a name="1.1.0"></a>
## [1.1.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/compare/1.0.0...1.1.0) (2024-04-22)

### ✨ Features

- **features, prints:** implement 'colored' outputs colors ([dfdb3bf](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/dfdb3bf7608e95fa7465ed8950d4f4a930fb3f11))
- **migration:** implement '--overwrite' to delete and reimport ([34a2af5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/34a2af5ad8077564f0a714422ab0782869cc92a5))

### 🐛 Bug Fixes

- **migration:** prevent '--set-avatar' already closed input file ([ef2583f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ef2583f9cc37e13d2f5ee03a9091a8f4694f441c))

### ⚙️ Cleanups

- **migration:** minor output flush improvements ([ece017a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/ece017a21d7fe2735dcaede1b9468a51b404055d))


<a name="1.0.0"></a>
## [1.0.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commits/1.0.0) (2024-04-21)

### ✨ Features

- **gitlab-projects-migrate:** initial sources implementation ([89ed62b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-migrate/commit/89ed62b74c076a9c49145be0ae366a1aac626933))


