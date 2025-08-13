# Changelog

<a name="3.0.0"></a>
## [3.0.0](https://gitlab.com/RadianDevCore/tools/git-dct/compare/2.2.0...3.0.0) (2025-08-12)

### ✨ Features

- **git_pu:** implement single tag reference push support ([23d7f7a](https://gitlab.com/RadianDevCore/tools/git-dct/commit/23d7f7ab212c35dc987ff652a286e95afc5a6c65))
- **git_pu:** implement '-y/--yes' and '-n/--no' confirmation flags ([e4a21d1](https://gitlab.com/RadianDevCore/tools/git-dct/commit/e4a21d1bcda7b25be68d806e6837602b2c426d88))
- **git_pu, puall:** implement 'git pu --all' and 'git puall' ([6765387](https://gitlab.com/RadianDevCore/tools/git-dct/commit/6765387c1180dea1f919b53b047ff9a92dbd89bf))
- **profiles/lo:** improve 'git lo' outputs closer to 'tig --all' ([95da4d4](https://gitlab.com/RadianDevCore/tools/git-dct/commit/95da4d4e3db2df2a4f181208807b951e9756104f))
- **profiles/loall:** create 'loall' alias for 'lo' with '--all --graph' ([6ce8b6e](https://gitlab.com/RadianDevCore/tools/git-dct/commit/6ce8b6e55f77c688a7b89a8269096b54a7a333dd))
- **setup:** add support for Python 3.13 ([784339f](https://gitlab.com/RadianDevCore/tools/git-dct/commit/784339f2051567d30df09ebdf4055cd147fe65db))
- **tools:** rework 'branch' into 'reference' in sources ([fe53cc8](https://gitlab.com/RadianDevCore/tools/git-dct/commit/fe53cc8d42c82ea1c3c801cd3228f5dbead3576d))

### 🐛 Bug Fixes

- **git_pu:** force user non-default confirmation if risk push ([536d9a2](https://gitlab.com/RadianDevCore/tools/git-dct/commit/536d9a2ba7e4b5de2dd428940e5af8eb3c97e87c))
- **git_stat:** resolve reversed Git statistics upon push ([fd85463](https://gitlab.com/RadianDevCore/tools/git-dct/commit/fd8546351d70797d12325d07417cba1aba40e93d))
- **tools:** avoid catching remotes and branches error logs ([0a09dc5](https://gitlab.com/RadianDevCore/tools/git-dct/commit/0a09dc5cd00cc2a2da3e5d35a775c99f2ffcfebb))

### 🚜 Code Refactoring

- **tools:** isolate remotes and branches list to functions ([2b88496](https://gitlab.com/RadianDevCore/tools/git-dct/commit/2b88496bc816bf10b56b6e3a7314400f06a5eb8d))

### 📚 Documentation

- **mkdocs:** embed coverage HTML page with 'mkdocs-coverage' ([0be2466](https://gitlab.com/RadianDevCore/tools/git-dct/commit/0be2466be3d04619f402db3af1ea38a72bb410e0))
- **prepare:** prepare empty HTML coverage report if missing locally ([3203b9f](https://gitlab.com/RadianDevCore/tools/git-dct/commit/3203b9f7b7003dcb677b3c708848e0759f03d9d9))
- **readme:** document 'mkdocs-coverage' plugin in references ([605c076](https://gitlab.com/RadianDevCore/tools/git-dct/commit/605c076fe700cfe4b076eb065de1ac724cfb4859))

### 🧪 Test

- **platform:** improve coverage for Windows target ([3d2c7a9](https://gitlab.com/RadianDevCore/tools/git-dct/commit/3d2c7a9f46adfe588634b418abb24ab21900e569))
- **versions:** ignore '--enable' attempts on Windows environments ([14c9cdf](https://gitlab.com/RadianDevCore/tools/git-dct/commit/14c9cdf0bb1599d1e45d7b2907410a26693edccf))

### ⚙️ Cleanups

- **gitlab-ci, src:** resolve non breakable spacing chars ([40a2f53](https://gitlab.com/RadianDevCore/tools/git-dct/commit/40a2f5322a7ee82186dd7337d7748c05587a7cf0))
- **pre-commit:** migrate to 'pre-commit-crocodile' 6.1.0 ([bb22e03](https://gitlab.com/RadianDevCore/tools/git-dct/commit/bb22e03015396983678e8cdcb28fd088255b5b65))
- **strings:** remove unused 'random' method and dependencies ([3da4a31](https://gitlab.com/RadianDevCore/tools/git-dct/commit/3da4a31467d9366f729662bf21b281f61918ea16))

### 🚀 CI

- **gitlab-ci:** bind coverage reports to GitLab CI/CD artifacts ([1aaac5c](https://gitlab.com/RadianDevCore/tools/git-dct/commit/1aaac5c6a6d8ce82eb874f374a6330c24f7b9bad))
- **gitlab-ci:** configure 'coverage' to parse Python coverage outputs ([f8a75ab](https://gitlab.com/RadianDevCore/tools/git-dct/commit/f8a75ab63ea204d9f96f6026c2f70775ad2496dd))
- **gitlab-ci:** always run 'coverage:*' jobs on merge requests CI/CD ([81babbf](https://gitlab.com/RadianDevCore/tools/git-dct/commit/81babbf14c01e56f07832c93a91300bb3b70078e))
- **gitlab-ci:** show coverage reports in 'script' outputs ([6342925](https://gitlab.com/RadianDevCore/tools/git-dct/commit/634292576f3d82205fa2b6683f5ef535e04cb6f2))
- **gitlab-ci:** restore Windows coverage scripts through templates ([41da713](https://gitlab.com/RadianDevCore/tools/git-dct/commit/41da7133651eb3b5baf81c688d2fe729d48f913d))
- **gitlab-ci:** resolve 'coverage' regex syntax for Python coverage ([6335cfa](https://gitlab.com/RadianDevCore/tools/git-dct/commit/6335cfa5b7bbfb623512b0dca90e213ac0d3e897))
- **gitlab-ci:** resolve 'coverage:windows' relative paths issues ([cdbcf5a](https://gitlab.com/RadianDevCore/tools/git-dct/commit/cdbcf5a5d14cceb450b1d45442e18ce21126285c))
- **gitlab-ci:** run normal 'script' in 'coverage:windows' with 'SUITE' ([d5d7c25](https://gitlab.com/RadianDevCore/tools/git-dct/commit/d5d7c25b0cb439649ee2553e397a763abb28f47a))
- **gitlab-ci:** use 'before_script' from 'extends' in 'coverage:*' ([bb1e7e3](https://gitlab.com/RadianDevCore/tools/git-dct/commit/bb1e7e3edc11c4ed5db9848c52a4879ddab55ed9))
- **gitlab-ci:** run 'versions' tests on 'coverage:windows' job ([926db53](https://gitlab.com/RadianDevCore/tools/git-dct/commit/926db53fb4a00fe518e39f7093fdb1142b850de9))
- **gitlab-ci:** fix 'pragma: windows cover' in 'coverage:linux' ([113ddcf](https://gitlab.com/RadianDevCore/tools/git-dct/commit/113ddcf76ae736c34cd9dd7e310a8ca62b895508))
- **gitlab-ci:** run 'colors' tests in 'coverage:windows' ([66ffb67](https://gitlab.com/RadianDevCore/tools/git-dct/commit/66ffb67831ca9615f0726559625220b22c18f6a1))
- **gitlab-ci:** run 'modes' tests in 'coverage:windows' ([f7eae6b](https://gitlab.com/RadianDevCore/tools/git-dct/commit/f7eae6b55941521ffb85b559ea46714b62894a83))
- **gitlab-ci:** add 'pragma: ... cover file' support to exclude files ([f4aa089](https://gitlab.com/RadianDevCore/tools/git-dct/commit/f4aa08953141d59fed0eb0df11ac32ce39dd9d2b))
- **gitlab-ci:** isolate 'pages' and 'pdf' to 'pages.yml' template ([19866da](https://gitlab.com/RadianDevCore/tools/git-dct/commit/19866da6506e0e611ea7d3fe62d95dbe735b421a))
- **gitlab-ci:** isolate 'deploy:*' jobs to 'deploy.yml' template ([8ce5d90](https://gitlab.com/RadianDevCore/tools/git-dct/commit/8ce5d9056e8d09bbb9f944a57dd06fc898b7e583))
- **gitlab-ci:** isolate 'sonarcloud' job to 'sonarcloud.yml' template ([d7e6c48](https://gitlab.com/RadianDevCore/tools/git-dct/commit/d7e6c4865bb8d0175d72a309388adddc1e37aa79))
- **gitlab-ci:** isolate 'readme' job to 'readme.yml' template ([ab960c0](https://gitlab.com/RadianDevCore/tools/git-dct/commit/ab960c0ee1f0993febb053ba3b0005cca1392ec5))
- **gitlab-ci:** isolate 'install' job to 'install.yml' template ([131662e](https://gitlab.com/RadianDevCore/tools/git-dct/commit/131662ebbc3e4c896cf5e6dfb179aab525b8abf1))
- **gitlab-ci:** isolate 'registry:*' jobs to 'registry.yml' template ([f40e834](https://gitlab.com/RadianDevCore/tools/git-dct/commit/f40e834cfd9bcf68ba2116c347f6467b1308c3d4))
- **gitlab-ci:** isolate 'changelog' job to 'changelog.yml' template ([d0107d6](https://gitlab.com/RadianDevCore/tools/git-dct/commit/d0107d67cec3573d929ffdfd296661b3123a1d39))
- **gitlab-ci:** isolate 'build' job to 'build.yml' template ([be15b8c](https://gitlab.com/RadianDevCore/tools/git-dct/commit/be15b8cb93efa78237aff28a95ff9e21317f5c32))
- **gitlab-ci:** isolate 'codestyle' job to 'codestyle.yml' template ([7bc0b04](https://gitlab.com/RadianDevCore/tools/git-dct/commit/7bc0b046e04d934849690d675b4a3f3ba29211e7))
- **gitlab-ci:** isolate 'lint' job to 'lint.yml' template ([8cc821a](https://gitlab.com/RadianDevCore/tools/git-dct/commit/8cc821ac5553e8abd7de25fdf598be7ea1e2e58d))
- **gitlab-ci:** isolate 'typings' job to 'typings.yml' template ([15bd6ad](https://gitlab.com/RadianDevCore/tools/git-dct/commit/15bd6ad7bc65adf48dff092e388a00bebe092f14))
- **gitlab-ci:** create 'quality:coverage' job to generate HTML report ([a3ba98e](https://gitlab.com/RadianDevCore/tools/git-dct/commit/a3ba98ef8796ebcb98c1643d8ee59cd007bee696))
- **gitlab-ci:** cache HTML coverage reports in 'pages' ([7906d44](https://gitlab.com/RadianDevCore/tools/git-dct/commit/7906d440f3af53eb65c770a251207cded230c588))
- **gitlab-ci:** migrate to 'quality:sonarcloud' job name ([629bcb7](https://gitlab.com/RadianDevCore/tools/git-dct/commit/629bcb7f0f3ce703df37423bb82e3169d7d2b3f4))
- **gitlab-ci:** isolate 'clean' job to 'clean' template ([017e669](https://gitlab.com/RadianDevCore/tools/git-dct/commit/017e66904e1904d7757673caa1afd2f1f34d947f))
- **gitlab-ci:** deprecate 'hooks' local job ([c06aa7e](https://gitlab.com/RadianDevCore/tools/git-dct/commit/c06aa7e359d63b3b82fd43ceacfc4be61ef6ace1))
- **gitlab-ci:** use more CI/CD inputs in 'pages.yml' template ([b1c1263](https://gitlab.com/RadianDevCore/tools/git-dct/commit/b1c1263d5172144b1b653da7e40a4c354e32bfdf))
- **gitlab-ci:** isolate '.test:template' to 'test.yml' template ([b73abca](https://gitlab.com/RadianDevCore/tools/git-dct/commit/b73abca1ebb687175331d46022940c9b1a33a70d))
- **gitlab-ci:** isolate '.coverage:*' to 'coverage.yml' template ([761b9d5](https://gitlab.com/RadianDevCore/tools/git-dct/commit/761b9d55dc11b08be796ab3e2d5dfc9c8819f044))
- **gitlab-ci:** raise latest Python test images from 3.12 to 3.13 ([e466e4f](https://gitlab.com/RadianDevCore/tools/git-dct/commit/e466e4f6dbad5c1ddc03d9dd6eb4a1c2ec3348b3))
- **gitlab-ci:** migrate to RadianDevCore components submodule ([a04f8ff](https://gitlab.com/RadianDevCore/tools/git-dct/commit/a04f8ff9a068da8571cb867eeb8cfe1901e0d12f))
- **gitlab-ci:** isolate Python related templates to 'python-*.yml' ([f735404](https://gitlab.com/RadianDevCore/tools/git-dct/commit/f73540455778cf6a69b604394853437b2d340710))
- **gitlab-ci:** migrate to 'git-cliff' 2.9.1 and use CI/CD input ([4ced0cb](https://gitlab.com/RadianDevCore/tools/git-dct/commit/4ced0cb31990f77956853a303aae50250ca03174))
- **gitlab-ci:** create 'paths' CI/CD input for paths to cleanup ([8cb2875](https://gitlab.com/RadianDevCore/tools/git-dct/commit/8cb28753f8465dbad8df528f103d0fac4f3b5cc0))
- **gitlab-ci:** create 'paths' CI/CD input for paths to format ([07bac79](https://gitlab.com/RadianDevCore/tools/git-dct/commit/07bac79da322d96e6a4f68c23534854d4d88c368))
- **gitlab-ci:** create 'paths' CI/CD input for paths to check ([f9f5495](https://gitlab.com/RadianDevCore/tools/git-dct/commit/f9f5495dc88cc6e6e96daf02374eb5eeeca6d33e))
- **gitlab-ci:** create 'paths' CI/CD input for paths to lint ([755bf80](https://gitlab.com/RadianDevCore/tools/git-dct/commit/755bf8029698616f30e16d186ab59333213fba23))
- **gitlab-ci:** create 'intermediates' and 'dist' CI/CD inputs ([c1c9ce1](https://gitlab.com/RadianDevCore/tools/git-dct/commit/c1c9ce1ce587e720efa008fc6b38d7a70bf625d7))
- **gitlab-ci:** implement GitLab tags protection jobs ([80e9732](https://gitlab.com/RadianDevCore/tools/git-dct/commit/80e9732001b63f70abf776afb8e653c8dde86c96))
- **gitlab-ci:** remove redundant 'before_script:' references ([1776a7c](https://gitlab.com/RadianDevCore/tools/git-dct/commit/1776a7ce38c40c979ba92dceb078b314e505f407))

### 📦 Build

- **pages:** install 'coverage.txt' requirements in 'pages' image ([d9a2ba4](https://gitlab.com/RadianDevCore/tools/git-dct/commit/d9a2ba43986baaa8b4110e4027df27f27a807a6e))
- **requirements:** install 'mkdocs-coverage>=1.1.0' for 'pages' ([01ae52a](https://gitlab.com/RadianDevCore/tools/git-dct/commit/01ae52a2af9832af7a66f477390c8c21aa9227ba))


<a name="2.2.0"></a>
## [2.2.0](https://gitlab.com/RadianDevCore/tools/git-dct/compare/2.1.1...2.2.0) (2025-06-16)

### ✨ Features

- **commit:** create 'wip' alias to create 'Work in Progress' commits ([4f34e6d](https://gitlab.com/RadianDevCore/tools/git-dct/commit/4f34e6d22eb7754dd389817cf61037506290d1f7))

### 🐛 Bug Fixes

- **tools:** avoid 'select_branch' detecting remotes in branches names ([31b614c](https://gitlab.com/RadianDevCore/tools/git-dct/commit/31b614c20c53371e1eb21593b549a91f416915ef))
- **version:** migrate from deprecated 'pkg_resources' to 'packaging' ([3656d7f](https://gitlab.com/RadianDevCore/tools/git-dct/commit/3656d7f38fd8a7d691489bb283dec590036dfae1))
- **version:** try getting version from bundle name too ([f4f92b3](https://gitlab.com/RadianDevCore/tools/git-dct/commit/f4f92b32e2b589b5d0c7ac7e534a5508e2bb5063))

### 📚 Documentation

- **mkdocs:** raise copyright year to '2025' ([85bd624](https://gitlab.com/RadianDevCore/tools/git-dct/commit/85bd624d34772d03173712580923aa0b1cfd6183))

### ⚙️ Cleanups

- **pre-commit:** update against 'pre-commit-crocodile' 4.2.1 ([2d35ce9](https://gitlab.com/RadianDevCore/tools/git-dct/commit/2d35ce9be6c13929390891b408870f17ecfc22c7))
- **pre-commit:** migrate to 'pre-commit-crocodile' 5.0.0 ([1a96cac](https://gitlab.com/RadianDevCore/tools/git-dct/commit/1a96cac0072ecc098bce0c193c458b585d934daa))
- **vscode:** install 'ryanluker.vscode-coverage-gutters' ([b62a943](https://gitlab.com/RadianDevCore/tools/git-dct/commit/b62a94343eb987251af43680f02689df3e0060d1))
- **vscode:** configure coverage file and settings ([9f48ef4](https://gitlab.com/RadianDevCore/tools/git-dct/commit/9f48ef4478ef915709687da11bdf0e316624395f))

### 🚀 CI

- **coveragerc, gitlab-ci:** implement coverage specific exclusions ([93d8fcc](https://gitlab.com/RadianDevCore/tools/git-dct/commit/93d8fcce093b293c399f7e36003a8df09b3648ad))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@4.1.0' ([5504965](https://gitlab.com/RadianDevCore/tools/git-dct/commit/5504965eb93ecb07d8568c05ecb594e82e8ed833))
- **gitlab-ci:** remove unrequired 'stage: deploy' in 'pdf' job ([36a1199](https://gitlab.com/RadianDevCore/tools/git-dct/commit/36a11994d9a1c4a5eb1c8aa2a7139ea722efaa64))
- **gitlab-ci:** improve combined coverage local outputs ([13fb300](https://gitlab.com/RadianDevCore/tools/git-dct/commit/13fb3009d00b06463821d8e0bd210350fba10177))
- **gitlab-ci:** enforce 'coverage' runs tool's 'src' sources only ([11c5f3e](https://gitlab.com/RadianDevCore/tools/git-dct/commit/11c5f3e8cb8eb55176cf70c4291767f0b546ff06))
- **gitlab-ci:** add support for '-f [VAR], --flag [VAR]' in 'readme' ([30f70e9](https://gitlab.com/RadianDevCore/tools/git-dct/commit/30f70e9b8a704c5522b836a7d0791eea9c7d4471))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@5.0.0' ([5e62f7c](https://gitlab.com/RadianDevCore/tools/git-dct/commit/5e62f7c273e30543ba8550e6457e625ea7658aad))
- **gitlab-ci:** migrate to 'CI_LOCAL_*' variables with 'gcil' 12.0.0 ([21408cf](https://gitlab.com/RadianDevCore/tools/git-dct/commit/21408cfe0b0f6b8e1b3882df394ebc8492861b3a))

### 📦 Build

- **requirements:** add 'importlib-metadata' runtime requirement ([0de1469](https://gitlab.com/RadianDevCore/tools/git-dct/commit/0de146990f1cc22ac58a9a366c8cc5e984eebe69))
- **requirements:** migrate to 'commitizen' 4.8.2+adriandc.20250608 ([adea2a4](https://gitlab.com/RadianDevCore/tools/git-dct/commit/adea2a4ee60fce203045bc71b6b97698b18890ae))


<a name="2.1.1"></a>
## [2.1.1](https://gitlab.com/RadianDevCore/tools/git-dct/compare/2.1.0...2.1.1) (2025-02-09)

### 🐛 Bug Fixes

- **git_pu:** avoid commits lost warning upon missing branch ([552c6f8](https://gitlab.com/RadianDevCore/tools/git-dct/commit/552c6f8352240dc94e315399baa3bca50568c0d9))
- **tools:** improve user input to integer conversions security ([af8f6a6](https://gitlab.com/RadianDevCore/tools/git-dct/commit/af8f6a633c80ff395ea0d8fa6698aa24c8da2e50))
- **tools:** resolve manual input without remote branches in 'select_branch' ([2e82f82](https://gitlab.com/RadianDevCore/tools/git-dct/commit/2e82f82d329107818bf09e7841d02756fd04e75a))


<a name="2.1.0"></a>
## [2.1.0](https://gitlab.com/RadianDevCore/tools/git-dct/compare/2.0.0...2.1.0) (2025-02-03)

### ✨ Features

- **git_pu:** add user confirmation if remote commits will be lost ([270ebc9](https://gitlab.com/RadianDevCore/tools/git-dct/commit/270ebc9b53e9f804b9de91fe573df5aa8e62a5f8))
- **tools:** implement '--ref' support to override 'HEAD' reference ([06ea0f7](https://gitlab.com/RadianDevCore/tools/git-dct/commit/06ea0f75d7c94248b07b54d6839e28ab01c21d08))
- **tools:** implement '--validate' flag to confirm manually by user ([70ea3c0](https://gitlab.com/RadianDevCore/tools/git-dct/commit/70ea3c0a1c58a4291a70053240664b4baa304003))

### 🐛 Bug Fixes

- **git_fe:** fix main tool name to 'git fe' ([de092d6](https://gitlab.com/RadianDevCore/tools/git-dct/commit/de092d6c81a6474dba6d11424d22bedeafa724b4))
- **git_pu:** resolve faulty '{branch}' header text output ([fd81070](https://gitlab.com/RadianDevCore/tools/git-dct/commit/fd81070497951588b92c37cd157a80e4776438e2))
- **git_pu:** resolve 'SyntaxError: f-string' for Python 3.9 ([573f3e6](https://gitlab.com/RadianDevCore/tools/git-dct/commit/573f3e6e26c15cff780faed94b2a35134aeb09d8))
- **tools:** use 'questionary' for user inputs and confirmation ([73abe99](https://gitlab.com/RadianDevCore/tools/git-dct/commit/73abe9968e11e1ef1cc36aac0df873710ad04fe1))
- **tools:** refactor branch manual input with 'questionary' ([e63b38b](https://gitlab.com/RadianDevCore/tools/git-dct/commit/e63b38bddd0689e7e763478766da09cf28734386))

### 📚 Documentation

- **docs:** use '<span class=page-break>' instead of '<div>' ([73d0eeb](https://gitlab.com/RadianDevCore/tools/git-dct/commit/73d0eebc50f480e33b7d1351ba4eacdd3cea0af5))
- **pages:** rename 'Tools' section to 'Features' ([b181fab](https://gitlab.com/RadianDevCore/tools/git-dct/commit/b181fab053e621e73d3b02c037ffae3d6d9a2de1))

### 🎨 Styling

- **colors:** ignore 'Colored' import 'Incompatible import' warning ([6d3f5e3](https://gitlab.com/RadianDevCore/tools/git-dct/commit/6d3f5e306c9737589e4b1f770e1dcfd689245c3c))

### 🧪 Test

- **tools:** create 'git-dct-tools-... --help' coverage tests ([5182dcc](https://gitlab.com/RadianDevCore/tools/git-dct/commit/5182dcc0f2ec01510d3809ac5149dd6b05e58b4d))

### 🚀 CI

- **gitlab-ci:** bind 'git-dct-tools-*' for coverage tests ([5ea9338](https://gitlab.com/RadianDevCore/tools/git-dct/commit/5ea93383610d2bbb94dd9e1fb09ae386c015ec84))


<a name="2.0.0"></a>
## [2.0.0](https://gitlab.com/RadianDevCore/tools/git-dct/compare/1.0.0...2.0.0) (2025-01-19)

### ✨ Features

- **add:** create 'acae' function alias ([0535267](https://gitlab.com/RadianDevCore/tools/git-dct/commit/0535267ec758f716349dd9545974d9c4227baa6a))
- **branch:** create 'bd' Git alias ([d80dceb](https://gitlab.com/RadianDevCore/tools/git-dct/commit/d80dcebe86a57de854658f37aca4dd0ee96cc739))
- **cherry-pick:** create 'cpa', 'cpc' and 'cps' Git aliases ([a6db11c](https://gitlab.com/RadianDevCore/tools/git-dct/commit/a6db11cd861e0729c268d7caa833d451ed5a1029))
- **commit:** create 'cad', 'cauthor' and 'sl' function aliases ([d625d04](https://gitlab.com/RadianDevCore/tools/git-dct/commit/d625d04cbb24d985980eb0557964aec32835d606))
- **commit:** create 'ce' Git alias ([f968f14](https://gitlab.com/RadianDevCore/tools/git-dct/commit/f968f14862ef24ab0e6e7962570ae8d1e98d8044))
- **describe:** create 'tagdescribe' Git alias ([35c009e](https://gitlab.com/RadianDevCore/tools/git-dct/commit/35c009e818921609baf72b86cc6a7271d2f3839e))
- **diff:** create 'di' function alias ([b9f0ec9](https://gitlab.com/RadianDevCore/tools/git-dct/commit/b9f0ec90e06e2b8fd853f8834afd6fd25ee9608c))
- **diff:** create 'st' Git alias ([70b3856](https://gitlab.com/RadianDevCore/tools/git-dct/commit/70b38568448ce632d7a88cbcc2ca6835f29d3a14))
- **diff:** bind 'st' Git alias to 'stat' Git alias ([5e31cfe](https://gitlab.com/RadianDevCore/tools/git-dct/commit/5e31cfef62c8b5c35595b75b05604cd248985e41))
- **fetch:** create 'f' Git alias ([9349d15](https://gitlab.com/RadianDevCore/tools/git-dct/commit/9349d1527e097e0dd9b3c5b547d5d782ddf6888a))
- **interfaces:** create 'k' and 'tig' function aliases ([ebc2f1e](https://gitlab.com/RadianDevCore/tools/git-dct/commit/ebc2f1e99a95b162d3f3cfba8614995e7b904257))
- **log:** create 'l' for 'lo' without decorations ([0d1b8e9](https://gitlab.com/RadianDevCore/tools/git-dct/commit/0d1b8e93e7c42da4132705a2e35acf0f5b92dc92))
- **push:** create 'p' and 'pf' Git aliases ([535c2dd](https://gitlab.com/RadianDevCore/tools/git-dct/commit/535c2ddb45ef100b88f0c7795f59b094214e0740))
- **rebase:** create 'r', 'redit', 'rf, 'rfedit' function aliases ([1b99ed8](https://gitlab.com/RadianDevCore/tools/git-dct/commit/1b99ed8377319424a25deaba72c36cb275362cca))
- **reset:** create 'ri' Git alias ([27fcde1](https://gitlab.com/RadianDevCore/tools/git-dct/commit/27fcde130569bb454eaa9105ed58f0f744fca2b8))
- **revert:** create 'rl' function alias ([db2253a](https://gitlab.com/RadianDevCore/tools/git-dct/commit/db2253a0ea1c56dc63237eea1c1f507ed66038e6))
- **revert:** create 'revertf' function alias ([1532c57](https://gitlab.com/RadianDevCore/tools/git-dct/commit/1532c57db0587ebf2e0f39840732ddcbe6e6d117))
- **setup:** implement support for '*.function' profiles as aliases ([e56fb00](https://gitlab.com/RadianDevCore/tools/git-dct/commit/e56fb000656a7a2d5f55b03b2508852b7c1d49ee))
- **setup:** add double quotes on alias definitions ([72ccdcf](https://gitlab.com/RadianDevCore/tools/git-dct/commit/72ccdcfbadd9349d98774b5a05ed6fde504294e5))
- **setup:** improve function aliases syntax ([df8bb1e](https://gitlab.com/RadianDevCore/tools/git-dct/commit/df8bb1e17fbd535f87d03a88de40883b1cd7e8c0))
- **setup:** isolate aliases and functions in '.gitconfig' sections ([7acda69](https://gitlab.com/RadianDevCore/tools/git-dct/commit/7acda69eff7070e9e09420d4bd86af50b7558f88))
- **show:** create 'shall' Git alias ([85e4def](https://gitlab.com/RadianDevCore/tools/git-dct/commit/85e4def26312ee50bd39dc7347c91192baa36429))
- **stash:** create 'cl', 'cla' and 'su' function aliases ([8d70198](https://gitlab.com/RadianDevCore/tools/git-dct/commit/8d70198eb209918ac87d192ed2a32e62400710ed))
- **submodule:** create 'smu' function alias ([e79e5de](https://gitlab.com/RadianDevCore/tools/git-dct/commit/e79e5dea1a39b793926abaa8ee53bfb0eaf7001c))
- **tag:** create 'clean-tags' function alias ([23b5bde](https://gitlab.com/RadianDevCore/tools/git-dct/commit/23b5bde10b54e07facf9cef452ff9d0156f271e3))
- **tools:** create 'git stat' Python tool and alias ([14c1ed0](https://gitlab.com/RadianDevCore/tools/git-dct/commit/14c1ed00b8d2bea15aff641f223f24d8058f43c4))
- **tools:** improve 'git stat' error code result handlings ([552c1be](https://gitlab.com/RadianDevCore/tools/git-dct/commit/552c1be5f1f2222dce4a84006d0dc6a3cfa29716))
- **tools:** create 'git pu' Python tool, 'pu' and 'put' aliases ([2129268](https://gitlab.com/RadianDevCore/tools/git-dct/commit/2129268772ad8bed164cbe18664caf8590f2be73))
- **tools:** create 'git rb' Python tool and 'rb' alias ([b9c879a](https://gitlab.com/RadianDevCore/tools/git-dct/commit/b9c879a1aa91cc9c8a0a75fcf6b18d919db06b79))
- **tools:** create 'git rbl' Python tool and 'rbl' alias ([55ec379](https://gitlab.com/RadianDevCore/tools/git-dct/commit/55ec3797b030fcf69568c1c4dfc6b6861873fe00))
- **tools:** create 'git fe' Python tool and 'fe', 'fr' and 'ftr' aliases ([a3fdd07](https://gitlab.com/RadianDevCore/tools/git-dct/commit/a3fdd077b8708e3d5bd5cf9af7998072185e6368))
- **tools:** create 'git fcp' Python tool and 'fcp' alias ([0bd8447](https://gitlab.com/RadianDevCore/tools/git-dct/commit/0bd8447300f3e23e7c2ce1501e199b767c13a1cc))
- **tools:** create 'git cauthor' Python tool and use in 'cauthor' alias ([ba10ee6](https://gitlab.com/RadianDevCore/tools/git-dct/commit/ba10ee6994d156c4d79771c14bc9b702d4114e94))

### 🐛 Bug Fixes

- **git_cauthor:** prevent faulty author issues outside git directory ([cba8bfc](https://gitlab.com/RadianDevCore/tools/git-dct/commit/cba8bfc4d4bc8b46901a3160fafc668b614f6f49))
- **git_cauthor:** add commit separator if git hooks are found ([967625b](https://gitlab.com/RadianDevCore/tools/git-dct/commit/967625b129fbdb9f9650129011f616d345240c6a))
- **git_stat:** isolate 'git diff' if upstream commits exist ([d2cd705](https://gitlab.com/RadianDevCore/tools/git-dct/commit/d2cd7054d21264dcea74676e5888a9e6d52e97fd))
- **git_stat:** add missing line separator ir local commits only ([cc01321](https://gitlab.com/RadianDevCore/tools/git-dct/commit/cc01321f39424ba790e620c1d0fd521ad7e5b4e0))
- **git_stat:** resolve 'git diff' output separator ([d63ccd2](https://gitlab.com/RadianDevCore/tools/git-dct/commit/d63ccd27fe8d832f90dd492152213b6988381deb))
- **setup:** resolve Git functions to alias syntax ([19b2aca](https://gitlab.com/RadianDevCore/tools/git-dct/commit/19b2aca3df5fcb8a46e7222d30ac57ea9d375156))
- **tools:** resolve support for branches with '.../...' formats ([3074636](https://gitlab.com/RadianDevCore/tools/git-dct/commit/30746364a90e26ba1be0040d59f1eb6b98c1fbc9))

### 🚜 Code Refactoring

- **git_rb:** rework 'rbl' tool into 'rb --local' tool ([79394fa](https://gitlab.com/RadianDevCore/tools/git-dct/commit/79394fa3b0427c0778edd58ed17c9833a2eb6bb9))

### 📚 Documentation

- **alias:** disable table of contents injection ([d3722b6](https://gitlab.com/RadianDevCore/tools/git-dct/commit/d3722b687f9f38c52f5c27887aa3e5ab8f6410a8))
- **alias:** add '.title' title files for all aliases sections ([71415bd](https://gitlab.com/RadianDevCore/tools/git-dct/commit/71415bdabb535e8fc56e2f8fb77a8a0a3a493560))
- **alias:** refactor 'alias' documentation syntax and styles ([c979fb3](https://gitlab.com/RadianDevCore/tools/git-dct/commit/c979fb36f764ee7c4b15bdb505d554aeec7b5275))
- **alias.gitconfig:** create 'alias.gitconfig' raw file viewer ([80b4e89](https://gitlab.com/RadianDevCore/tools/git-dct/commit/80b4e89038d371290446f8c1669577f102a19418))
- **prepare:** avoid 'TOC' injection if 'hide:  - toc' is used ([9727ea0](https://gitlab.com/RadianDevCore/tools/git-dct/commit/9727ea09a39c1d2d0c6d5dce4ef595c7e4a88acb))
- **prepare:** prepare assets with 'setup.py' inside 'prepare.sh' ([614dc38](https://gitlab.com/RadianDevCore/tools/git-dct/commit/614dc3886f3dd50faf430a5bd287cd14d65d69f7))
- **prepare:** hide 'setup.py assets' warning outputs ([b0ed967](https://gitlab.com/RadianDevCore/tools/git-dct/commit/b0ed967ee73aeee98a2e326e54cab40cf6501720))
- **tools:** create 'git-dct' Python tools documentation page ([780e0af](https://gitlab.com/RadianDevCore/tools/git-dct/commit/780e0af2577dcb580d903c6330870091e5affe47))

### 🎨 Styling

- **docs, setup, src:** minor comments codestyle improvements ([a3dbf5d](https://gitlab.com/RadianDevCore/tools/git-dct/commit/a3dbf5d5a81aeecb7e7f4c5c54d3ae951e3d9419))

### ⚙️ Cleanups

- **profiles:** minor aliases comments codestyle improvements ([0bf7a47](https://gitlab.com/RadianDevCore/tools/git-dct/commit/0bf7a47ce7c71f69d90d18c4948202fa6d37dfc6))
- **setup:** resolve 'user_options' typings issues ([28a236a](https://gitlab.com/RadianDevCore/tools/git-dct/commit/28a236a5e949101f91361ae1c0dc097f712fce96))
- **sonar-project:** exclude tools duplication checks in SonarCloud ([cfa870a](https://gitlab.com/RadianDevCore/tools/git-dct/commit/cfa870affa0bbe9eccf684d140066572f78b0c64))
- **sonar-project:** exclude tools coverage checks in SonarCloud ([87ea4b7](https://gitlab.com/RadianDevCore/tools/git-dct/commit/87ea4b75b33cf44c3d4a3511d7e1761ecdaf5b72))

### 🚀 CI

- **gitlab-ci:** run 'pages' job upon 'profiles/*' changes ([5721cf7](https://gitlab.com/RadianDevCore/tools/git-dct/commit/5721cf7e87b8e17e759a17fd33774f26fadfb0db))
- **gitlab-ci:** run 'pages' job upon 'setup.py' changes ([f50ef42](https://gitlab.com/RadianDevCore/tools/git-dct/commit/f50ef427aa5521760095f063f79966a1cf13425e))
- **gitlab-ci:** detect 'setup.py' for 'pages' local changes detection ([efb0946](https://gitlab.com/RadianDevCore/tools/git-dct/commit/efb09462ef9fdf9d178c120d410e68df5b446bf7))
- **gitlab-ci:** run coverage jobs if 'sonar-project.properties' changes ([011d275](https://gitlab.com/RadianDevCore/tools/git-dct/commit/011d27565d7419a0ec7485f5def2731e5a8b8391))
- **gitlab-ci:** watch for 'docs/.*' changes in 'pages' jobs ([380dc5f](https://gitlab.com/RadianDevCore/tools/git-dct/commit/380dc5fe1d4da2b74c58cddb1118ead6a91ed098))


<a name="1.0.0"></a>
## [1.0.0](https://gitlab.com/RadianDevCore/tools/git-dct/compare/0.1.0...1.0.0) (2025-01-05)

### ✨ Features

- **branchs:** create 'br', 'brl', 'ch' and 'sw' Git aliases ([690a3dd](https://gitlab.com/RadianDevCore/tools/git-dct/commit/690a3ddd013f11b454a612de2cb4bdd69c01ace1))
- **cli, readme, tests:** refactor into '--enable' and '--disable' ([d4a1f08](https://gitlab.com/RadianDevCore/tools/git-dct/commit/d4a1f08ff96b07d860108d8f3fe32bcdfd0e8dc6))
- **commit:** create 'c', 'ca', 'cae', 'cp' and 'cs' Git aliases ([2004b4a](https://gitlab.com/RadianDevCore/tools/git-dct/commit/2004b4a11fb6e3006592cc8dbc045e0d9e4f8446))
- **diff:** create 'diffall', 'diffc' and 'diffw' Git aliases ([3f5e472](https://gitlab.com/RadianDevCore/tools/git-dct/commit/3f5e47259876e8086878090f64ba55bc1e2e0c3a))
- **diff:** add '--submodule=diff' to 'diffall' ([bfe0726](https://gitlab.com/RadianDevCore/tools/git-dct/commit/bfe07265484ffbe98fa790640e162786642fd6f1))
- **git-dct:** migrate project name to 'git-dct' ([e31a0d6](https://gitlab.com/RadianDevCore/tools/git-dct/commit/e31a0d67c0bdb02bbf1c4251bdb4148a6245cb3f))
- **log:** create 'lo' Git alias ([e3947ce](https://gitlab.com/RadianDevCore/tools/git-dct/commit/e3947ce71cde8e7643b301ed3082f61cf05d422e))
- **merge:** create 'mt' Git alias ([dec2b8d](https://gitlab.com/RadianDevCore/tools/git-dct/commit/dec2b8ddfc64098539730fecedf725b3862e7dab))
- **profiles, cli, setup:** initial 'aa', 'an' and 'ap' Git aliases ([e875b65](https://gitlab.com/RadianDevCore/tools/git-dct/commit/e875b65134ce5d4f2c54f7e981b3429a2a2094eb))
- **rebase:** create 'ra', 'rc', 're', 're' and 'rs' Git aliases ([646ee2c](https://gitlab.com/RadianDevCore/tools/git-dct/commit/646ee2c551911c6c33d520a87903efac4b21dc9c))
- **remote:** create 'rv' Git alias ([9a8e3be](https://gitlab.com/RadianDevCore/tools/git-dct/commit/9a8e3be7d48baa93dce744ffa7dc3c462362092e))
- **reset:** create 'rhf', 'rhh', 'ro' and 'rt' Git aliases ([c2770bb](https://gitlab.com/RadianDevCore/tools/git-dct/commit/c2770bb5f9e50c3b3efb633fd3da46032f185064))
- **show:** create 'shf' and 'shm' Git aliases ([9f82c42](https://gitlab.com/RadianDevCore/tools/git-dct/commit/9f82c42df22c22e55ff343af0bace038223d8adb))
- **stash:** create 's', 'sc', 'sp' and 'spop' Git aliases ([d069b34](https://gitlab.com/RadianDevCore/tools/git-dct/commit/d069b341ca0ede0d206b89bde4718f9b0b3ca315))
- **submodule:** create 'sm' and 'smi' Git aliases ([5941350](https://gitlab.com/RadianDevCore/tools/git-dct/commit/5941350554a21cbe45d8ecd40ddb9d70f06bf3cb))

### 🐛 Bug Fixes

- **entrypoint:** resolve Windows tests without 'Traversable' type ([652982f](https://gitlab.com/RadianDevCore/tools/git-dct/commit/652982fdae63859164e4e88971d3a1d0f059e4ca))
- **entrypoint:** inject 'include.path' without duplicating it ([1af1426](https://gitlab.com/RadianDevCore/tools/git-dct/commit/1af1426897961977ef97223f193b9058785e571e))

### 📚 Documentation

- **alias:** prepare initial Git aliases configuration simple dump ([d406f96](https://gitlab.com/RadianDevCore/tools/git-dct/commit/d406f962bcfd43e6efae7c7e61e159de7fc12c97))
- **prepare:** use 'mkdocs.yml' to get project name value ([0ae8420](https://gitlab.com/RadianDevCore/tools/git-dct/commit/0ae8420decdf829517dd0d0f2079b625508b480b))
- **readme:** refresh usage documentation for '--install' mode ([d8fc817](https://gitlab.com/RadianDevCore/tools/git-dct/commit/d8fc8175e93c7f49ec5531e7ed58fd3ad388a09f))

### 🧪 Test

- **arguments:** test 'git-development-cli-tools' without arguments ([3aa1d5f](https://gitlab.com/RadianDevCore/tools/git-dct/commit/3aa1d5f69640361862903004cc8a4bf3f4424a54))
- **entrypoint:** ignore built asset access coverage ([3812eb8](https://gitlab.com/RadianDevCore/tools/git-dct/commit/3812eb8a865d3c0611f38d943c1142438f9b3654))

### ⚙️ Cleanups

- **setup:** sort 'profiles/*/*' files before parsing them ([677fb6a](https://gitlab.com/RadianDevCore/tools/git-dct/commit/677fb6a75934eda9f99ae374c301505b40f31662))
- **setup:** add section headers and comments in 'alias.gitconfig' ([987f339](https://gitlab.com/RadianDevCore/tools/git-dct/commit/987f3390bb26c73e9e6c94a77372bee46ca6c117))
- **setup:** add tool header on autogenerated 'alias.gitconfig' ([204f4e3](https://gitlab.com/RadianDevCore/tools/git-dct/commit/204f4e3ea2c6c73e63347ef171b199fbfeb34ec2))
- **setup:** ensure assets are generated before packages with 'sdist' ([d9ecee0](https://gitlab.com/RadianDevCore/tools/git-dct/commit/d9ecee00070f147df2d6e1252565eb0ceefad17d))
- **setup:** refactor assets generation for both 'sdist' and 'build' ([758d327](https://gitlab.com/RadianDevCore/tools/git-dct/commit/758d32702efa8d627d9cd20de0fee6694b4ef23d))
- **setup:** add author, email, license and sources assets header ([27dca01](https://gitlab.com/RadianDevCore/tools/git-dct/commit/27dca01067cb70a74ec546f68776cbb5624642c9))
- **vscode:** add 'sidneys1.gitconfig' extension for '.gitconfig' ([5a0b202](https://gitlab.com/RadianDevCore/tools/git-dct/commit/5a0b202062f3353d17ac9349115e778ae728a136))

### 🚀 CI

- **gitlab-ci:** raise oldest Python test images from 3.8 to 3.9 ([077c273](https://gitlab.com/RadianDevCore/tools/git-dct/commit/077c2738664fd3e35e500976dd6db055e14893cd))
- **gitlab-ci:** prepare and cleanup assets in 'pages' job ([1731ae9](https://gitlab.com/RadianDevCore/tools/git-dct/commit/1731ae958ef9e353d6be94c27028ef85ba4d0c8e))
- **gitlab-ci:** bind 'wine python' to 'python3' for 'coverage:windows' ([81aa952](https://gitlab.com/RadianDevCore/tools/git-dct/commit/81aa9528685a43cbb42307376ce8e62174e2c27d))
- **gitlab-ci, setup:** generate assets for coverage tests too ([cebf180](https://gitlab.com/RadianDevCore/tools/git-dct/commit/cebf180a1626ca512c386101d939d7c4e1425c96))
- **gitlab-ci, setup:** refactor with 'assets {--prepare,--clean}' ([7a39511](https://gitlab.com/RadianDevCore/tools/git-dct/commit/7a3951182b308ce84ecccfb04921a9058c00af00))

### 📦 Build

- **containers:** install 'runtime' requirements in 'pages' image ([2192421](https://gitlab.com/RadianDevCore/tools/git-dct/commit/2192421177fb3e1a645fa0f01ec02482e7147733))


<a name="0.1.0"></a>
## [0.1.0](https://gitlab.com/RadianDevCore/tools/git-dct/commits/0.1.0) (2025-01-01)

### ✨ Features

- **git-development-cli-tools:** initial commit based on 'gcil' ([688d8da](https://gitlab.com/RadianDevCore/tools/git-dct/commit/688d8daded71c03292375a1600c44df4c35f139a))

### 📚 Documentation

- **git-development-cli-tools:** describe with 'for daily usage' ([6c72d21](https://gitlab.com/RadianDevCore/tools/git-dct/commit/6c72d21e6ed2cda9d71c22cc58511dd72f5691bb))

### 🚀 CI

- **gitlab-ci:** ensure 'pages' job does not block pipeline if manual ([ad84737](https://gitlab.com/RadianDevCore/tools/git-dct/commit/ad847374c582fee3d84a13609a4ae9f04e3a2845))
- **gitlab-ci:** change release title to include tag version ([adc64a8](https://gitlab.com/RadianDevCore/tools/git-dct/commit/adc64a87f412f579cc510c751e4fbf6b53e124f6))


