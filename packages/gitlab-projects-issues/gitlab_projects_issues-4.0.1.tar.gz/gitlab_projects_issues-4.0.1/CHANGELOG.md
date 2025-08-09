# Changelog

<a name="4.0.1"></a>
## [4.0.1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/compare/4.0.0...4.0.1) (2025-08-08)

### 🐛 Bug Fixes

- **entrypoint:** raise issues without milestone errors properly ([0ea9f51](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/0ea9f51b02a6c63a59f78046766aa3de414fac66))
- **entrypoint:** improve issue without milestone error logs ([f5b37b6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/f5b37b6c4ed8fa094d7f3012fffae4008f6e36d1))


<a name="4.0.0"></a>
## [4.0.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/compare/3.2.0...4.0.0) (2025-08-08)

### ✨ Features

- **cli:** raise error if issue without milestone found ([05d9d89](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/05d9d8958b3aa36cdbf847184086e1442b46d8d6))
- **setup:** add support for Python 3.13 ([2d14ba2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/2d14ba2c615175de3bede1b147a7026c21f35b61))

### 🐛 Bug Fixes

- **version:** migrate from deprecated 'pkg_resources' to 'packaging' ([5fe5836](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/5fe583670899cc3de07124ed54b981846b6ed6e5))
- **version:** try getting version from bundle name too ([8cf7eac](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/8cf7eac907c7d77064b873905ee7cf71386ef99f))

### 📚 Documentation

- **docs:** use '<span class=page-break>' instead of '<div>' ([da31616](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/da31616fa5eb5b7f193cb3ae8c82ce1bad9afb8a))
- **license, mkdocs:** raise copyright year to '2025' ([3f41b96](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/3f41b9633f06f8303b3e25ac926cf8360b599979))
- **mkdocs:** embed coverage HTML page with 'mkdocs-coverage' ([3275b07](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/3275b07edb38967345da4bb8a382a758571759b5))
- **prepare:** avoid 'TOC' injection if 'hide:  - toc' is used ([02a4585](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/02a45858efc58bbf114be922511f511b28caa3fd))
- **prepare:** prepare empty HTML coverage report if missing locally ([1504c96](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/1504c965433893d4341669732548e52c62a71944))
- **readme:** document 'mkdocs-coverage' plugin in references ([b250e29](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/b250e292fbf86c0b5bae54051fa00bd4bf2d8f9c))

### 🎨 Styling

- **colors:** ignore 'Colored' import 'Incompatible import' warning ([dd6f537](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/dd6f5377cc7d77db92f1e6a78199a8006496623b))

### 🧪 Test

- **platform:** improve coverage for Windows target ([4578e40](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/4578e40398f33442fb4e11653d7ca747d81ef5e5))

### ⚙️ Cleanups

- **gitlab-ci, docs, src:** resolve non breakable spacing chars ([ba0bd2c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/ba0bd2cb340f306037386c1b6bfedaa581198d03))
- **pre-commit:** update against 'pre-commit-crocodile' 4.2.1 ([1a47aba](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/1a47aba0d58f8b1e462059e2dfa7628c5d8969f9))
- **pre-commit:** migrate to 'pre-commit-crocodile' 5.0.0 ([239b1ed](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/239b1ed82e461dd05fc506e11318a411ae1c1bcf))
- **sonar-project:** configure coverage checks in SonarCloud ([f9dc018](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/f9dc01861f8b25c66870ef2b6ec5a5de222a2c3c))
- **strings:** remove unused 'random' method and dependencies ([b9aebf8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/b9aebf8757455e619b2eb122ff249997a7058b18))
- **vscode:** install 'ryanluker.vscode-coverage-gutters' ([39a7bb4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/39a7bb4e576905651f07c6fb8fc73860999380ab))
- **vscode:** configure coverage file and settings ([fa11152](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/fa111522b33004cda8ac0609462101778ca06669))

### 🚀 CI

- **coveragerc, gitlab-ci:** implement coverage specific exclusions ([64e5308](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/64e530892e6e502019626f0d612cc217c23bb543))
- **gitlab-ci:** run coverage jobs if 'sonar-project.properties' changes ([f6b0152](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/f6b01521329908598846886fc8f376afaaefacfe))
- **gitlab-ci:** watch for 'docs/.*' changes in 'pages' jobs ([ec054fe](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/ec054fe6d531f12a8101663d8cc4965cde51c588))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@4.1.0' ([cef0196](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/cef019601adfcc5aced6ded439fc24b74a4684e5))
- **gitlab-ci:** remove unrequired 'stage: deploy' in 'pdf' job ([32bb698](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/32bb698a8ec8ab50874bec96043b4e61626cf669))
- **gitlab-ci:** improve combined coverage local outputs ([c53129a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/c53129a27182a1d0288c79ff0b16cd2399dc7795))
- **gitlab-ci:** enforce 'coverage' runs tool's 'src' sources only ([43ff886](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/43ff886f20e1f816fce3812847bc03fce396bb54))
- **gitlab-ci:** add support for '-f [VAR], --flag [VAR]' in 'readme' ([5037c68](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/5037c689b5e884861248d47c427dae8e71118ae7))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@5.0.0' ([0839991](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/08399910eec16726d73fcea83af0d11495d031e0))
- **gitlab-ci:** migrate to 'CI_LOCAL_*' variables with 'gcil' 12.0.0 ([7130991](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/7130991db5adffb32e3aa59f07ae60bef072e788))
- **gitlab-ci:** bind coverage reports to GitLab CI/CD artifacts ([cff8a36](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/cff8a3634bee30ab891abf074af685410199a835))
- **gitlab-ci:** configure 'coverage' to parse Python coverage outputs ([d33e391](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/d33e391250f68c41600cead6186fe6e0f0247c9c))
- **gitlab-ci:** always run 'coverage:*' jobs on merge requests CI/CD ([3a67078](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/3a670781b11185a50bfc6e239f48fdd690a4b403))
- **gitlab-ci:** show coverage reports in 'script' outputs ([0586c37](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/0586c370b28865619fb5ad84444ae1d97540de05))
- **gitlab-ci:** restore Windows coverage scripts through templates ([e7a372c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/e7a372cec783ef2c97e363f147a73afc54296abe))
- **gitlab-ci:** resolve 'coverage' regex syntax for Python coverage ([124d62d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/124d62d1398b6c4bd6edc27a045eb5f801071cb4))
- **gitlab-ci:** resolve 'coverage:windows' relative paths issues ([a8d2b93](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/a8d2b9363012d4b6b50b91d31813d2a9d4c51f40))
- **gitlab-ci:** run normal 'script' in 'coverage:windows' with 'SUITE' ([894aecd](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/894aecd50c5cef3aa9e44b1bba7a79e7c336acdb))
- **gitlab-ci:** use 'before_script' from 'extends' in 'coverage:*' ([fa9864b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/fa9864b9b554a6ae5bf4ed307c4c0fe4d07f572d))
- **gitlab-ci:** run 'versions' tests on 'coverage:windows' job ([3b22d6e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/3b22d6ef61a493fed1bb9411b3300ddd30c4d7a4))
- **gitlab-ci:** fix 'pragma: windows cover' in 'coverage:linux' ([e5e5c8e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/e5e5c8e44474c6c697c3affc6594d67a9b16a970))
- **gitlab-ci:** run 'colors' tests in 'coverage:windows' ([29b6926](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/29b69260570771ade55ecc20330d57310980a051))
- **gitlab-ci:** add 'pragma: ... cover file' support to exclude files ([6c2e088](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/6c2e0889b9124c3383cdc595d62181d29a180374))
- **gitlab-ci:** isolate 'pages' and 'pdf' to 'pages.yml' template ([5fe172e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/5fe172e0cd9b6713edf69dba63a3ecc51f6af497))
- **gitlab-ci:** isolate 'deploy:*' jobs to 'deploy.yml' template ([1ca9660](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/1ca9660fcb9936c54405a8d2e53e7ca9c9a54060))
- **gitlab-ci:** isolate 'sonarcloud' job to 'sonarcloud.yml' template ([2831678](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/2831678181b6a2e2804b3da0fc57d16d8f83b87f))
- **gitlab-ci:** isolate 'readme' job to 'readme.yml' template ([d033862](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/d033862c0c61d745be1acb47ae691c36112b1915))
- **gitlab-ci:** isolate 'install' job to 'install.yml' template ([bf3a7d8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/bf3a7d8b1d93947e7e21f7960e5ff8177c16e865))
- **gitlab-ci:** isolate 'registry:*' jobs to 'registry.yml' template ([f9ae3a5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/f9ae3a5dbb52e6b0838952f6d7bc0dec7af55731))
- **gitlab-ci:** isolate 'changelog' job to 'changelog.yml' template ([b40017e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/b40017eecdc0af7579acab1a67a7c79cef249425))
- **gitlab-ci:** isolate 'build' job to 'build.yml' template ([0ab0cca](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/0ab0ccad2250d230f2a595b2ef474daf52d783e6))
- **gitlab-ci:** isolate 'codestyle' job to 'codestyle.yml' template ([d27ad2b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/d27ad2b400e7703b44f592dccc789aaa26df8eb1))
- **gitlab-ci:** isolate 'lint' job to 'lint.yml' template ([56e93af](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/56e93af96dcf99f0218ad8b4ba3b729568a2335f))
- **gitlab-ci:** isolate 'typings' job to 'typings.yml' template ([5db52a8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/5db52a8e5012c59fced9672584e9bea579f07e23))
- **gitlab-ci:** create 'quality:coverage' job to generate HTML report ([881185a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/881185a119f00be6fd67a10076a1754113b6198b))
- **gitlab-ci:** cache HTML coverage reports in 'pages' ([103da68](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/103da6885d871c58c794e7f571bcfb3711ec0814))
- **gitlab-ci:** migrate to 'quality:sonarcloud' job name ([645fa51](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/645fa5190c55753aa86691872d2ed85e4e56dc1c))
- **gitlab-ci:** isolate 'clean' job to 'clean' template ([0a2056c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/0a2056c17360adfda96e6bdaf34a5e08bd0690ac))
- **gitlab-ci:** deprecate 'hooks' local job ([9e747cc](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/9e747cc91bf26cfd1b1da0d48c69ebea4abcc18d))
- **gitlab-ci:** use more CI/CD inputs in 'pages.yml' template ([581695a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/581695a7673b6dbfe414382d5cfa6581ec01372d))
- **gitlab-ci:** isolate '.test:template' to 'test.yml' template ([e767b7d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/e767b7d07b33b546c4544b9eb351e38aa932bac5))
- **gitlab-ci:** isolate '.coverage:*' to 'coverage.yml' template ([cbd4c94](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/cbd4c947055998df564a24cf97461ff9b8f13824))
- **gitlab-ci:** raise latest Python test images from 3.12 to 3.13 ([865c2f0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/865c2f05eb057608dca14da56299ccd4368e5b2c))
- **gitlab-ci:** migrate to RadianDevCore components submodule ([3ca952e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/3ca952e89cd80953b7bf97dc892762448a3f4fa5))
- **gitlab-ci:** isolate Python related templates to 'python-*.yml' ([22054b8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/22054b818effbcfca04b0b79a8ef96b41ccfa1ca))
- **gitlab-ci:** migrate to 'git-cliff' 2.9.1 and use CI/CD input ([3cb539a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/3cb539ac8055c14094a8ca1555bd8edb1950555b))
- **gitlab-ci:** create 'paths' CI/CD input for paths to cleanup ([270ec84](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/270ec8432f1bce829686dd537b067dabb0f1666b))
- **gitlab-ci:** create 'paths' CI/CD input for paths to format ([2fccf8a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/2fccf8adc5f5de9c995ae8102de1767d683dfd7d))
- **gitlab-ci:** create 'paths' CI/CD input for paths to check ([740bffa](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/740bffa4a49b0a216ec274c64883b8fe38c8b02d))
- **gitlab-ci:** create 'paths' CI/CD input for paths to lint ([ff891b8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/ff891b8cbd6deccf309559eae40b17c72dedd27c))
- **gitlab-ci:** create 'intermediates' and 'dist' CI/CD inputs ([b850fcd](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/b850fcd9aa6eb49e57793ee15bbb75e52742a6a4))
- **gitlab-ci:** isolate 'deploy:containers' to a components template ([e4c570c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/e4c570c0e85bdf717b04fddc4572cd0e6713bf93))
- **gitlab-ci:** implement ':x.y' containers automated tag release ([b8380b5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/b8380b5d1c5f5da2fc1fb9e4e4fd206c11e540fb))

### 📦 Build

- **pages:** install 'coverage.txt' requirements in 'pages' image ([fead360](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/fead360abe6b71bff49c3ae92ad26fc69fe067b2))
- **requirements:** add 'importlib-metadata' runtime requirement ([ad24f05](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/ad24f05cf5d7db75f2429c8fd45ab43320649859))
- **requirements:** migrate to 'commitizen' 4.8.2+adriandc.20250608 ([86cc97c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/86cc97c66cbb942b7c2e130621729fa2fa7a2887))
- **requirements:** install 'mkdocs-coverage>=1.1.0' for 'pages' ([6e03a43](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/6e03a437f756688b40474daf8ac326d1b2f65a1d))


<a name="3.2.0"></a>
## [3.2.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/compare/3.1.0...3.2.0) (2025-01-01)

### ✨ Features

- **cli:** implement '--get-milestone' feature ([90e04d6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/90e04d632644e156254f950877d05a6e2e5dc9f2))
- **cli:** implement '--set-milestone-...' features ([8cc195a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/8cc195a4d9d9999a852893913638cd646b85d5b5))
- **cli:** implement '--create-milestone' feature ([3bbd521](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/3bbd521d92711b920539ead419e505e28ead6da0))
- **entrypoint, milestones:** avoid milestone updates without changes ([6665602](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/6665602d2669ff238c63abc85df5a5443114f643))

### 🐛 Bug Fixes

- **cli:** use package name for 'Updates' checks ([7c34da0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/7c34da0990bd6ad2a5e5495c7ed81a12bcc28f27))
- **entrypoint:** validate GitLab issues feature and missing milestone ([f695006](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/f69500662718fa13ee162a5921e17b26c67efada))
- **main:** resolve '--milestones-statistics' usage without milestone ([f5eaae0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/f5eaae0ba68a32b4596ccd04e8d138108225d213))

### 📚 Documentation

- **mkdocs:** minor '(prefers-color-scheme...)' syntax improvements ([7713a73](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/7713a7324074b685efca7b6d1f384ae22564acf6))
- **mkdocs:** remove 'preview.py' and 'template.svg' files exclusions ([064efff](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/064efff336d7dfb899ad51185f7e2e86d766cb28))
- **mkdocs, pages:** use 'MKDOCS_EXPORTER_PDF_OUTPUT' for PDF file ([f13bf5e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/f13bf5ecc5c35ac95acaf72873c3aa8c43add543))
- **pages:** rename PDF link title to 'Export as PDF' ([ecbfdd0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/ecbfdd01211702de5665a6056935ee87a008f2f1))
- **pdf:** avoid header / footer lines on front / back pages ([e0dae64](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/e0dae64356b01c338e02d2cc4d47d44a7cfff648))
- **pdf:** minor stylesheets codestyle improvements ([37b163a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/37b163a1bc538fa551642aab670a95031be67a77))
- **pdf:** reverse PDF front / back cover pages colors for printers ([b6e008e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/b6e008eb5d85487db1072bc20a20a519f073e75c))
- **prepare:** use 'mkdocs.yml' to get project name value ([f4c487c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/f4c487c01abc4f543cd71d5d0d244306de4f29d7))
- **stylesheets:** resolve lines and arrows visibility in dark mode ([6a21bb4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/6a21bb4e8d8bc7d554a68702746004e05b6ac3e1))
- **templates:** add 'Author' and 'Description' to PDF front page ([c38f8d4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/c38f8d4b0113a274fe0052890545eeae7bbeab44))
- **templates:** add 'Date' detail on PDF front page ([36f0ad8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/36f0ad818a24275a6508aab7c1628a065befa0eb))
- **templates:** use Git commit SHA1 as version if no Git tag found ([c46b5b1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/c46b5b1615a41231e0bea575a2ba5355339b5b89))
- **webhooks:** document milestones update triggers with tokens ([60a6db9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/60a6db95f396ffc4692a7da87cad37e05346c393))

### 🧪 Test

- **test:** fix daily updates coverage test syntax ([8a68157](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/8a68157a1ade84483e1f2d7a4c00622afa0f2397))

### 🚀 CI

- **gitlab-ci:** avoid PDF slow generation locally outside 'pdf' job ([e9cbb16](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/e9cbb1659b208061282a9af2e8cee89558c55f33))
- **gitlab-ci:** validate host network interfaces support ([0c09b87](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/0c09b87629b715b5d7e9a9f4682f156b1b4e2bc4))
- **gitlab-ci:** enable '.local: no_regex' feature ([f7e8684](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/f7e86841aeaed18b6c26a049e06bba8058e9bb5d))
- **gitlab-ci:** append Git version to PDF output file name ([7adf216](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/7adf216837da21d431c4431d13215e9d93d15376))
- **gitlab-ci:** rename PDF to 'gitlab-projects-issues' ([bbf0e66](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/bbf0e66882e97718fab35ed13a5c366c506cdd29))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@4.0.0' ([aa7956f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/aa7956fe1ca4b12c32a81168260a0824bee63d36))
- **gitlab-ci:** ensure 'pages' job does not block pipeline if manual ([d826d86](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/d826d86a870b0d4d2bb54231600e97e1aa5ad85f))
- **gitlab-ci:** change release title to include tag version ([7e1b4d8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/7e1b4d8db204f36ada0dfb760e0818bc68cc8af9))


<a name="3.1.0"></a>
## [3.1.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/compare/3.0.2...3.1.0) (2024-10-28)

### 🐛 Bug Fixes

- **main:** ensure 'FORCE_COLOR=0' if using '--no-color' flag ([6fbbb9b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/6fbbb9ba44c4a8fb3b0bb86f5b3a11551ba706bf))
- **milestones:** resolve milestones sort if due dates are empty ([c360429](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/c360429aff5455ef2303932619bb0c566771327b))

### 📚 Documentation

- **assets:** prepare mkdocs to generate mermaid diagrams ([74aa2ef](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/74aa2efcc3f6b3af098507a465cf8ba6e6c06a38))
- **cliff:** improve 'Unreleased' and refactor to 'Development' ([d607c57](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/d607c57715ac6743f1a052bdbc92c04244e60859))
- **covers:** resolve broken page header / footer titles ([d0fed68](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/d0fed68a6c138f0635e6a6196e507d08e83d9e6e))
- **custom:** change to custom header darker blue header bar ([e990562](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/e9905627ac5cb00429d51cfc7b43403214937467))
- **docs:** improve documentation PDF outputs with page breaks ([4f8c595](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/4f8c595ae2af73009e7715a2fd3eb8944d565fae))
- **mkdocs:** enable 'git-revision-date-localized' plugin ([79ebaed](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/79ebaed0894426b9e896642d986ccf69a3dbc269))
- **mkdocs:** change web pages themes colors to 'blue' ([289d9a0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/289d9a0e43f4873ae685b8182126d338243a6ef1))
- **mkdocs:** fix 'git-revision-date-localized' syntax ([8434fb4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/8434fb4ce107c97e353c4d2eb7d11401c7db6783))
- **mkdocs:** migrate to 'awesome-pages' pages navigation ([e8bfbf4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/e8bfbf498bb06b6f68d39136a0bf931093512064))
- **mkdocs:** change 'auto / light / dark' themes toggle icons ([cfb8faa](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/cfb8faa0f40befa24093194dd070523fb93d625f))
- **mkdocs:** enable and configure 'minify' plugin ([fff8e09](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/fff8e09ee02430c4a3fd8e2d36d2d9a1c7dd8828))
- **mkdocs:** install 'mkdocs-macros-plugin' for Jinja2 templates ([6ce1d39](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/6ce1d391b7575dd37983e60239711f3b511bf3bf))
- **mkdocs:** enable 'pymdownx.emoji' extension for Markdown ([e6c5159](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/e6c5159d0365f9979ca486d636aaeee51b3bb92b))
- **mkdocs:** implement 'mkdocs-exporter' and customize PDF style ([4f9a045](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/4f9a04561b98c60005299a3850747427a4576f59))
- **mkdocs:** set documentation pages logo to 'solid/code' ('</>') ([ad7e659](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/ad7e65934cadf32d8c0f78ef6015ee83f7b693a6))
- **mkdocs:** enable 'permalink' headers anchors for table of contents ([314e71d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/314e71d2df984649e1bb3a3b7490eb16c91e41f9))
- **mkdocs:** prepare 'privacy' and 'offline' plugins for future usage ([4f0c78e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/4f0c78e126a66b2099904f74c79f728ab4f73b0b))
- **mkdocs:** disable Google fonts to comply with GDPR data privacy ([df5f19e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/df5f19e06a3a6a871683a2432a2e25dcc4c30ead))
- **mkdocs:** implement 'Table of contents' injection for PDF results ([9417c29](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/9417c291dbd0cf4227f457d2b2d3e21dc44f06c4))
- **mkdocs:** enable 'Created' date feature for pages footer ([4e07e50](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/4e07e50ac138d68da4364c87fd46d2b4fdfabab3))
- **mkdocs:** add website favicon image and configuration ([5eb522d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/5eb522dfe8f0b0a293654af80bc9607c19a6ed5d))
- **mkdocs:** implement 'book' covers to have 'limits' + 'fronts' ([0bef12b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/0bef12b8a75055026811c530b8fbb07f06e5fb2d))
- **mkdocs:** isolate assets to 'docs/assets/' subfolder ([a4afa3f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/a4afa3f480229f6ef3dc595a04420d342207606a))
- **mkdocs:** exclude '.git' from watched documentation sources ([b5b4f5b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/b5b4f5b9dcf01868a1bf4b5717417b94c1616be1))
- **mkdocs, prepare:** resolve Markdown support in hidden '<details>' ([ec82132](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/ec82132cb9aebc90c8a5cb2c588c58cff2360d42))
- **pages:** rename index page title to '‣ Usage' ([53cf129](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/53cf1295f6051f8146dea0af41c36d87b51b1bf5))
- **pdf:** simplify PDF pages copyright footer ([e5a69c6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/e5a69c63910acd5011b5725c9adcff17b47c13e5))
- **pdf:** migrate to custom state pseudo class 'state(...)' ([d030542](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/d0305428cd947f16fb672fb7586be0b41066723c))
- **prepare:** regenerate development 'CHANGELOG' with 'git-cliff' ([f1088bc](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/f1088bc29a4e050483d13c285c2e940f54c56af8))
- **prepare:** avoid 'md_in_html' changes to 'changelog' and 'license' ([b8196ec](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/b8196ecdde3ce088a65f06966e625e1181a7ba3e))
- **prepare:** fix '<' and '>' changelog handlings and files list ([dc404af](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/dc404af04195033c49dc4e2dc60b8b355d7efe6d))
- **prepare:** implement 'About / Quality' badges page ([b34c974](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/b34c9746af860b27deb4ba66562ea33e91067d46))
- **prepare:** improve 'Quality' project badges to GitLab ([aa17b59](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/aa17b595dcb570d19d2df8fda9cf00915acc06c6))
- **prepare:** use 'docs' sources rather than '.cache' duplicates ([1c6ce3b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/1c6ce3bca5558f593205502db151f255d0828075))
- **prepare:** resolve 'docs/about' intermediates cleanup ([e7b86dc](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/e7b86dc2a0320b44da7c0e795bf0e7ff3c4e096c))
- **prepare:** add PyPI badges and license badge to 'quality' page ([4ecf27c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/4ecf27cf2e55d2daa8f2b5112d6b948b618bafe4))
- **prepare:** avoid adding TOC to generated and 'no-toc' files ([dba60cf](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/dba60cfcf4e1de572778968e4233e2545940f378))
- **readme:** add 'gcil:enabled' documentation badge ([cb3a0c7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/cb3a0c7fd2a17a363391d434ee36cbe7c721b292))
- **readme:** add pypi, python versions, downloads and license badges ([bda3079](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/bda30791baa8dae3ad85cb7ea866698975c7a71a))
- **readme:** add '~/.python-gitlab.cfg' section title ([66b470e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/66b470eca7c280f0e90256f3022f932af43e25dd))
- **readme:** minor improvements to milestone statistics example ([a94a34a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/a94a34ac0f6cf60da3e038e07240bee3435831af))
- **robots:** configure 'robots.txt' for pages robots exploration ([e151f17](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/e151f17d58da850a79864c6b93fe43be192cbe35))

### ⚙️ Cleanups

- **gitignore:** exclude only 'build' folder from sources root ([224a9db](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/224a9dbc477f8a3d3874b1a72e1808414e344a64))
- **gitignore:** exclude '/build' folder or symlink too ([c82ae90](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/c82ae902e4b2d4d6e014e217864a1480a0c7723a))
- **sonar:** wait for SonarCloud Quality Gate status ([6b53619](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/6b53619629d643ba07755af1708d27b8cafe161c))
- **vscode:** use 'yzhang.markdown-all-in-one' for Markdown formatter ([f353e9e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/f353e9ecd28cbc0e4a406a5e1eff375119ebb1d1))

### 🚀 CI

- **gitlab-ci:** prevent 'sonarcloud' job launch upon 'gcil' local use ([df62caf](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/df62caf55edcd3eee6f325416daf905199b3aa4f))
- **gitlab-ci:** run SonarCloud analysis on merge request pipelines ([607974e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/607974efd338e5871b54a222894a76ced283a61d))
- **gitlab-ci:** watch for 'config/*' changes in 'serve' job ([432dbe4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/432dbe446a1fd77c65b9e82146eae2a98831edef))
- **gitlab-ci:** fetch Git tags history in 'pages' job execution ([0f62ead](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/0f62eadb0b1561cc62c18e84cada6e51356a2f0e))
- **gitlab-ci:** fetch with '--unshallow' for full history in 'pages' ([45e36af](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/45e36aff193b03062b7227ade8afd9a4f3a8955d))
- **gitlab-ci:** enforce 'requirements/pages.txt' in 'serve' job ([95758e9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/95758e98e85b9b617404b109d980c4707cfd8845))
- **gitlab-ci:** add 'python:3.12-slim' image mirror ([08f0ccb](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/08f0ccbd0002daef620c572a549eb28e67f1cfd7))
- **gitlab-ci:** inject only 'mkdocs-*' packages in 'serve' job ([a3dbec8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/a3dbec89f5b060ab5c4376ba60063ad4ad3d194d))
- **gitlab-ci:** install 'playwright' with chromium in 'serve' job ([17b8af9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/17b8af9b3a512175f74dac45dfe42fdfba5899c7))
- **gitlab-ci:** find files only for 'entr' in 'serve' ([6762249](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/6762249c99a44b4576079f246c941eb2be4da3ec))
- **gitlab-ci:** improve GitLab CI job outputs for readability ([67e8499](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/67e84997fbae41a44a49d6cb844cea276f21129d))
- **gitlab-ci:** deploy GitLab Pages on 'CI_DEFAULT_BRANCH' branch ([0a9ab9d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/0a9ab9dd5c5119be51aa594cdea1387083ac7f93))
- **gitlab-ci:** ignore 'variables.scss' in 'serve' watcher ([824951d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/824951d1850bfe8ef69e57c5b3ca15fce31e777d))
- **gitlab-ci:** preserve only existing Docker images after 'images' ([87aaf96](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/87aaf96191dd301897613eb2032c585c3ecb0b58))
- **gitlab-ci:** use 'MKDOCS_EXPORTER_PDF_ENABLED' to disable PDF exports ([836dd8f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/836dd8f16a957df51622c9e402a34936acac9a61))
- **gitlab-ci:** run 'pages' job on GitLab CI tags pipelines ([2f8e072](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/2f8e072894009afcfde8ccb1a2e4679b8324dd8e))
- **gitlab-ci:** isolate 'pages: rules: changes' for reuse ([488a182](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/488a182d724d654277fe947d56d5b9d7abd0ba59))
- **gitlab-ci:** allow manual launch of 'pages' on protected branches ([684ae40](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/684ae40f4e5de78967162d7eeaa12131d652be72))
- **gitlab-ci:** create 'pdf' job to export PDF on tags and branches ([971b815](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/971b8155b411c84ad8b1d169eea8f7cc2a4398a2))
- **gitlab-ci:** implement local pages serve in 'pages' job ([ee3097b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/ee3097bfa969a3384677c0e609b9f3548428bdef))
- **gitlab-ci:** raise minimal 'gcil' version to '11.0' ([31fae81](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/31fae8105345fd844cfd175ed2ecbd401f0a06b3))
- **gitlab-ci:** enable local host network on 'pages' job ([d06f4a4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/d06f4a4d036f8a7c6e8e1f1e345539a00ddc4e53))
- **gitlab-ci:** detect failures from 'mkdocs serve' executions ([9413853](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/9413853db91754996f06cf8a9a1e0deb5d0c84e9))
- **gitlab-ci:** refactor images containers into 'registry:*' jobs ([24fad8a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/24fad8a470fb9afdd4b805947e10cd8662d454ab))
- **gitlab-ci:** bind 'registry:*' dependencies to 'requirements/*.txt' ([d1ac987](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/d1ac98793a2ac9542707225be518ceaa20241457))

### 📦 Build

- **build:** import missing 'build' container sources ([d599a9b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/d599a9b9546bb3618a82f494f546c985aad11a83))
- **containers:** use 'apk add --no-cache' for lighter images ([721bdf2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/721bdf2f465e64f880898d9c97c1e799f096e2bd))
- **pages:** add 'git-cliff' to the ':pages' image ([e4515a4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/e4515a45b7422e9ea1bcbd02d95b91a4e4e5e513))
- **pages:** migrate to 'python:3.12-slim' Ubuntu base image ([73cfa3a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/73cfa3a2205e16f2ebdffc8c299b2c1c850943c5))
- **pages:** install 'playwright' dependencies for 'mkdocs-exporter' ([b04b34d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/b04b34dec5eb944bc92b0c8d23733c20d3704312))
- **pages:** install 'entr' in the image ([23f4f0e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/23f4f0ef1abe8729a473fb728bc02c3abcfcaa7a))
- **requirements:** install 'mkdocs-git-revision-date-localized-plugin' ([82f1f51](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/82f1f51fef6ebdfa8ec55582cea8c2124a41b21c))
- **requirements:** install 'mkdocs-awesome-pages-plugin' plugin ([5cbde0f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/5cbde0fcee95b442bdd94b1a989eaf14ff09fe8d))
- **requirements:** install 'mkdocs-minify-plugin' for ':pages' ([1d38343](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/1d38343a064c41e80681062b0592653e6b45c34b))
- **requirements:** install 'mkdocs-exporter' in ':pages' ([dae9328](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/dae9328f30773c3e1277676d297d718566f67797))
- **requirements:** migrate to 'mkdocs-exporter' with PR#35 ([de610a3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/de610a39116b8d40edc37b843c3d169b80d25861))
- **requirements:** upgrade to 'playwright' 1.48.0 ([c542f4b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/c542f4b719fc0102d1c5ab6ce0ddff59c2c2d9e6))
- **requirements:** migrate to 'mkdocs-exporter' with PR#42/PR#41 ([42919a5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/42919a50e1eb26e9f30ec63121b12d95c46f8df0))


<a name="3.0.2"></a>
## [3.0.2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/compare/3.0.1...3.0.2) (2024-08-25)

### ✨ Features

- **updates:** migrate from deprecated 'pkg_resources' to 'packaging' ([41b9b29](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/41b9b297122e4c6e40dc7b2747068e45fcb52899))

### 📚 Documentation

- **mkdocs:** implement GitLab Pages initial documentation and jobs ([ff84cb2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/ff84cb2e0b846c7f3beeef484657489316dec50f))
- **readme:** link against 'gcil' documentation pages ([cf35987](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/cf35987e9b5b106dfe87da984a63c5b6fac91cff))

### ⚙️ Cleanups

- **commitizen:** migrate to new 'filter' syntax (commitizen#1207) ([0461494](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/04614942053dfcd86a33b4952170fe2de7bd89e3))
- **pre-commit:** add 'python-check-blanket-type-ignore' and 'python-no-eval' ([d96a990](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/d96a99003cba1b3817adbb56f47c572d5f6be939))
- **pre-commit:** fail 'gcil' jobs if 'PRE_COMMIT' is defined ([972ecf0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/972ecf053b6d02e4156ffd169f0319f90273434f))
- **pre-commit:** simplify and unify 'local-gcil' hooks syntax ([4742542](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/4742542def5511507123210d042a1e6e38bc7d06))
- **pre-commit:** improve syntax for 'args' arguments ([4fa55b2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/4fa55b263506f3b526ccc7fbf6a8ce7e57a04b3b))
- **pre-commit:** migrate to 'run-gcil-*' template 'gcil' hooks ([e95b0c7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/e95b0c74d7c1c40f68174fecf3aefb6f2a9ff339))
- **pre-commit:** update against 'run-gcil-push' hook template ([a05195d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/a05195d11487651064a2d9e829a779fac08806df))
- **pre-commit:** migrate to 'pre-commit-crocodile' 3.0.0 ([988835b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/988835b4658f33d85778f7711616a00e62e8ddca))

### 🚀 CI

- **containers:** implement ':pages' image with 'mkdocs-material' ([ceafc32](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/ceafc3287e1d6bc4785dd5959c39adb5718384a1))
- **gitlab-ci:** avoid failures of 'codestyle' upon local launches ([a37b540](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/a37b54048999e91b8b1fcf87d761f1b3c27d296d))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@2.1.0' component ([011e795](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/011e795d6be1e6fb850b3485c19680cc537f7ccd))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@3.0.0' component ([0311b02](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/0311b02489285b7648b80f1cfb7bbcd61c337eb4))


<a name="3.0.1"></a>
## [3.0.1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/compare/3.0.0...3.0.1) (2024-08-21)

### 🚀 CI

- **gitlab-ci:** fix 'deploy:container' release job ([103f564](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/103f56475789ebf5c154fb0003ff7e816ae01728))


<a name="3.0.0"></a>
## [3.0.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/compare/2.2.0...3.0.0) (2024-08-21)

### ✨ Features

- **🚨 BREAKING CHANGE 🚨 |** **setup:** drop support for Python 3.6 ([48b40fd](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/48b40fd65464c02c7d31969156bc643102b19050))
- **🚨 BREAKING CHANGE 🚨 |** **setup:** drop support for Python 3.7 ([ae1ed7a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/ae1ed7acdd51662c349916b5c0ec4f9ca561eaf2))

### 🐛 Bug Fixes

- **package:** fix package name for 'importlib' version detection ([a95fd74](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/a95fd74c96f8757ebf773f505eb71fea355ea2a8))
- **platform:** always flush on Windows hosts without stdout TTY ([0c2df39](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/0c2df397cebd9b85e4f07855dcf1568b23bdd84e))
- **statistics:** resolve floating point equalities (python:S1244) ([6c6e4c2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/6c6e4c299f92800a482be1e535ea7edfa4167366))

### 📚 Documentation

- **readme:** add 'pre-commit enabled' badges ([3fff570](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/3fff570f8a2ffc51ad537dc1682be0267f0f9071))
- **readme:** add SonarCloud analysis project badges ([ebc6038](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/ebc60382130b887f5f52d5905dbe646210fb9bb8))
- **readme:** link 'gcil' back to 'gitlabci-local' PyPI package ([2f3c8e3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/2f3c8e370b48a4964044b23a7ef94ab074b25dd1))

### ⚙️ Cleanups

- **commitizen:** migrate to 'pre-commit-crocodile' 2.0.1 ([5da2ff0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/5da2ff0e716c52ce26d6f8cd5209126ea0b8b382))
- **gitattributes:** always checkout Shell scripts with '\n' EOL ([dce2373](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/dce2373af49fe6690a99b329d80bfd5c7ced5d2d))
- **gitignore:** ignore '.*.swp' intermediates 'nano' files ([75a727a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/75a727a93ea2547d6febca022cd6d620c0030d5c))
- **hooks:** implement evaluators and matchers priority parser ([851bfa1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/851bfa1ab23bc452f0978b149810ac1d0ccc835b))
- **pre-commit:** run 'codestyle', 'lint' and 'typings' jobs ([49aa37e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/49aa37e74d642bbaed6bc35a2af154731b505bfb))
- **pre-commit:** migrate to 'pre-commit-crocodile' 2.0.0 ([773236c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/773236cf60d923c68ba065773f84260c5d46b815))

### 🚀 CI

- **gitlab-ci:** show fetched merge request branches in 'commits' ([6fa4f87](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/6fa4f87b93ad61dcea52f8d6e4c4a999dcbab906))
- **gitlab-ci:** fix 'image' of 'commits' job ([4b3ce16](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/4b3ce16ad584097452780f85a03537204f9ae317))
- **gitlab-ci:** always run 'commits' job on merge request pipelines ([0bd22cc](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/0bd22cced9f6201987e4b5430d38117cf50d3b9e))
- **gitlab-ci:** make 'needs' jobs for 'build' optional ([1bed1f6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/1bed1f6ff546a1af500af82e13657a2d12159b00))
- **gitlab-ci:** validate 'pre-commit' checks in 'commits' job ([8506e8d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/8506e8da40a1c507930717901793596addb01e7b))
- **gitlab-ci:** refactor images into 'containers/*/Dockerfile' ([8788e71](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/8788e71375f0b33a36adbaeef90493155cd4b799))
- **gitlab-ci:** use 'HEAD~1' instead of 'HEAD^' for Windows compatibility ([e613bb1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/e613bb1db52f06584cdb0576b2eaaa377869c152))
- **gitlab-ci:** check only Python files in 'typings' job ([787e84c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/787e84c8465f0d598d655458e74cbcea54bf42e0))
- **gitlab-ci:** implement SonarCloud quality analysis ([90dbb69](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/90dbb6901bd7b21eea8254b954983c51436cb70f))
- **gitlab-ci:** detect and refuse '^wip|^WIP' commits ([b2a8071](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/b2a80711c943b3d8d5da4a39f3cc3d3504b1f143))
- **gitlab-ci:** isolate 'commits' job to 'templates/commit.yml' ([eb8431b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/eb8431bf6845b5a3643547fe915b67f3fb36cf4c))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@2.0.0' component ([8f92b7c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/8f92b7c440c46164773bdaa80943ad3159568efb))
- **gitlab-ci:** create 'hooks' local job for maintenance ([dd429da](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/dd429da8d631ca9de2bc3d9ac336e506cc56a85f))
- **gitlab-ci, tests:** implement coverage initial jobs and tests ([d72e5ce](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/d72e5cedae88268e755cc2b9f25f01df7de407ce))

### 📦 Build

- **pre-commit:** migrate to 'pre-commit-crocodile' 1.1.0 ([ef26db9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/ef26db9fb40bc6aa80010d5131aec48b53b341f0))


<a name="2.2.0"></a>
## [2.2.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/compare/2.1.0...2.2.0) (2024-08-15)

### 🐛 Bug Fixes

- **setup:** refactor 'python_requires' versions syntax ([7ee6dc2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/7ee6dc29778b35bd9be265e1b3c6a27be001d709))
- **setup:** resolve project package and name usage ([0afa3a7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/0afa3a74dc678dae87610df39e30818816473438))
- **updates:** ensure 'DEBUG_UPDATES_DISABLE' has non-empty value ([18d921b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/18d921b8aca5b67cba7ea60acefef5d34bcd5da1))
- **updates:** fix offline mode and SemVer versions comparisons ([a67c8b7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/a67c8b7dd08d459a50984ac90e37f82614f34915))

### 📚 Documentation

- **cliff:** use '|' to separate breaking changes in 'CHANGELOG' ([af857b2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/af857b2ad2ee59dce9bb2ebb2c8ccf0919ed97a9))
- **license:** update copyright details for 2024 ([3eca176](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/3eca1763ffa476971267abca451e84152d38e226))
- **readme:** add 'Commitizen friendly' badge ([b96b30a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/b96b30a223da97639ab33616e3504cf6084aed64))

### 🎨 Styling

- **cli:** improve Python arguments codestyle syntax ([ce9cac6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/ce9cac6fb0dac3e74d3a3a5cf0ea4c79c14cc545))
- **commitizen, pre-commit:** implement 'commitizen' custom configurations ([9488db6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/9488db65c415d14545e9843a30e5fb87b95d87e4))
- **pre-commit:** implement 'pre-commit' configurations ([34534f1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/34534f1622138fc70716de8a9b04b58096e8aff4))

### ⚙️ Cleanups

- **cli, package:** minor Python codestyle improvements ([02ea0ae](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/02ea0aeea6c12a465d36855fab865994961627e2))
- **pre-commit:** disable 'check-xml' unused hook ([4e7e544](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/4e7e544c6c476ec1bd9d0840cd96e1f58aef5703))
- **pre-commit:** fix 'commitizen-branch' for same commits ranges ([ca6817f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/ca6817f4411f45abb7aab6361ccadde731f73480))
- **setup:** refactor with more project configurations ([f07ae78](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/f07ae7819a5598b063dc9c94f325e6dc6bb0f705))
- **updates:** ignore coverage of online updates message ([c408cdd](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/c408cdd8de88210b75fcb82604a0237e0b8ec6d8))
- **vscode:** remove illegal comments in 'extensions.json' ([7a37d41](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/7a37d414a37add5effa5cbd5bda4e49d533ae204))

### 🚀 CI

- **gitlab-ci:** watch for 'codestyle', 'lint' and 'typings' jobs success ([b0504e5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/b0504e537c5e2b53933553511d41943042f9e0d2))
- **gitlab-ci:** create 'commits' job to validate with 'commitizen' ([51d41d5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/51d41d583a2f4a3ea7894f33e447f88446a41475))
- **gitlab-ci:** fix 'commits' job for non-default branches pipelines ([b60089f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/b60089fccce504f631ae909941c5d38fe8eed1c4))

### 📦 Build

- **hooks:** create './.hooks/manage' hooks manager for developers ([237612c](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/237612cdd2db2edb67dec6b31c6aa2f1269d76df))
- **hooks:** implement 'prepare-commit-msg' template generator ([dc436aa](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/dc436aaac1109c40ff7ac3c3b193f3f0e34e0673))
- **pre-commit:** enable 'check-hooks-apply' and 'check-useless-excludes' ([4b361d5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/4b361d50608b6e01f6d2891d689abc4d176e9333))


<a name="2.1.0"></a>
## [2.1.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/compare/2.0.2...2.1.0) (2024-08-11)

### ✨ Features

- **cli:** implement '--no-color' to disable colors ([e3c3376](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/e3c3376ed07b726da6757ed9755949f399571461))

### 🐛 Bug Fixes

- **package:** check empty 'environ' values before usage ([a9b8937](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/a9b89378672f392fe22a04c3044214487bd747ae))
- **updates:** remove unused 'recommended' feature ([7b3a4c4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/7b3a4c43ee480a2daec05556a4d09ab4fe11feea))

### 📚 Documentation

- **readme:** migrate from 'gitlabci-local' to 'gcil' package ([326712f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/326712f003cd1667f2e1f12f13ce8579667154db))

### ⚙️ Cleanups

- **colors:** resolve 'pragma: no cover' detection ([6559e13](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/6559e138fda507cb710179af213c352e0a1608a3))
- **platform:** disable coverage of 'SUDO' without write access ([09c2042](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/09c2042032399fd563821d1c17da9a265aa3d55c))
- **setup:** remove faulty '# pragma: exclude file' flag ([f6a4310](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/f6a431038603fd4e084c89eb07aaed3934b1718a))


<a name="2.0.2"></a>
## [2.0.2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/compare/2.0.1...2.0.2) (2024-08-10)

### ✨ Features

- **setup:** add support for Python 3.12 ([ad3d5f6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/ad3d5f67c6f30e97a8cdb9b599a53dbfbf9b54a5))

### 🧪 Test

- **setup:** disable sources coverage of the build script ([4653fa4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/4653fa49fb6e99a0023f5b3421486b2e828e6af2))

### 🚀 CI

- **gitlab-ci:** raise latest Python test images from 3.11 to 3.12 ([60f3c29](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/60f3c29edba83d2d26106c9b11725f2f775342f9))
- **gitlab-ci:** deprecate outdated and unsafe 'unify' tool ([e820b67](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/e820b6777aa967e267a4d7cf61cf74b3893e87db))


<a name="2.0.1"></a>
## [2.0.1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/compare/2.0.0...2.0.1) (2024-08-10)

### ✨ Features

- **gitlab-projects-issues:** migrate under 'RadianDevCore/tools' group ([55516fa](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/55516fa8bc3f091269809a87ebcbe38ac718b92a))

### 🐛 Bug Fixes

- **settings:** ensure 'Settings' class initializes settings file ([b8afd5b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/b8afd5b3b3286c5e22a3a0a3bb7479800893bd02))
- **src:** use relative module paths in '__init__' and '__main__' ([965c996](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/965c9962298f114285b88425c6b9142947817acd))


<a name="2.0.0"></a>
## [2.0.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/compare/1.0.5...2.0.0) (2024-08-08)

### 🛡️ Security

- **🚨 BREAKING CHANGE 🚨 |** **cli:** acquire tokens only from environment variables ([ca80cfe](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/ca80cfe398875e043f6b266af7c812a718bfd7d3))

### ✨ Features

- **🚨 BREAKING CHANGE 🚨 |** **cli:** refactor CLI into simpler GitLab URL bound parameters ([f589c8d](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/f589c8d8948d73770c0ccb12276a18fe78af568f))
- **cli:** add tool identifier header with name and version ([ffb86e6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/ffb86e6bafb5066c599fb99f6e4f7656b55bccb6))
- **cli:** implement '.python-gitlab.cfg' GitLab configurations files ([e87a3c7](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/e87a3c714a62cb8118cfaa6fc80991ed13a6fdc0))
- **cli, argparse:** implement environment variables helpers ([74acb0e](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/74acb0e85713aff9e51b1733fc3b5016ea6c1750))
- **cli, gitlab:** implement CI job token and public authentications ([57b7253](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/57b7253e275c86e6a3e6d26a1eb5b234d5b034f9))
- **main:** document '--default-estimate' metavar as 'ESTIMATE' ([d5a46d8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/d5a46d861bd183a15465efa3416f4210b9a45761))

### 🐛 Bug Fixes

- **environments:** add missing ':' to the README help description ([7e05429](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/7e05429536b559ee26219e5893bde94ce5550054))

### 📚 Documentation

- **cliff:** document 'security(...)' first in changelog ([e0e2b46](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/e0e2b4690aa005e3116b8e92119c193e9c28a6e4))
- **readme:** document '~/.python-gitlab.cfg' configuration file ([d9b5954](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/d9b59541ab07de337e16d0ceed249a1f8a91b201))

### ⚙️ Cleanups

- **cli/main:** minor codestyle improvement of 'import argparse' ([33e608b](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/33e608b23e4365e88a086bb74931f251a0493a0f))
- **types:** cleanup inconsistent '()' over base classes ([a0eaa89](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/a0eaa898e8d8a8830223213c619d6ba4a168a0a0))

### 🚀 CI

- **gitlab-ci:** migrate from 'git-chglog' to 'git-cliff' ([79b29f0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/79b29f070d81d5fafcdefe8478e8c331e7a76b08))
- **gitlab-ci:** bind '.docker/config.json' for local test builds ([5ac41d5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/5ac41d57fff03095b4a63650e9b039d6605759f1))


<a name="1.0.5"></a>
## [1.0.5](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/compare/1.0.4...1.0.5) (2024-07-14)

### 🐛 Bug Fixes

- **entrypoint:** initialize for issues without assignee and milestone ([f3692b8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/f3692b8a8cad3d84c52eedbf572d6d11f04730b5))


<a name="1.0.4"></a>
## [1.0.4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/compare/1.0.3...1.0.4) (2024-07-14)

### 🐛 Bug Fixes

- **entrypoint:** avoid failures upon issues without milestones ([57c8dc6](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/57c8dc614371486c5dcb40a79ca7f6f24f5b42ed))


<a name="1.0.3"></a>
## [1.0.3](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/compare/1.0.2...1.0.3) (2024-06-10)

### 📚 Documentation

- **readme:** improve milestones statistics outputs example ([decf7f4](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/decf7f42d9cdc534d41fec89ee098327d36f6c43))

### 🚀 CI

- **gitlab-ci:** install 'coreutils' in the deployed container image ([4946bdb](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/4946bdb226d33806634c6438461b92e7395770ca))
- **gitlab-ci:** use 'buildah' instead of 'docker' to pull images ([0b969b9](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/0b969b9f742a9a450f11aa45d7807ceee41dd723))


<a name="1.0.2"></a>
## [1.0.2](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/compare/1.0.1...1.0.2) (2024-06-01)

### 🚀 CI

- **gitlab-ci:** set '/bin/sh' as 'CMD' rather than 'ENTRYPOINT' ([5e742d8](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/5e742d8d9b1cae59891d5048b422ad50db04131d))


<a name="1.0.1"></a>
## [1.0.1](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/compare/1.0.0...1.0.1) (2024-06-01)

### 📚 Documentation

- **chglog:** add 'ci' as 'CI' configuration for 'CHANGELOG.md' ([29f0b43](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/29f0b43b95d49ee2f53ea07129ef675e8cbb57ed))
- **readme:** update 'README.md' for 'gitlab-projects-issues' ([4fb7d02](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/4fb7d024b45ae68112eac54e5b864f4099d9649a))

### 🚀 CI

- **gitlab-ci:** change commit messages to tag name ([8f8016f](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/8f8016f2c9f03d72afadc62a25109c42d2222dd3))


<a name="1.0.0"></a>
## [1.0.0](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commits/1.0.0) (2024-06-01)

### ✨ Features

- **gitlab-projects-issues:** initial sources implementation ([f1cc034](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/f1cc03421e051da80b4d2d1b9227fe03f05a66a7))

### 🚀 CI

- **gitlab-ci:** use 'CI_DEFAULT_BRANCH' to access 'develop' branch ([bae1c08](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/bae1c0826a97aca9805df868f11d08b480901bf2))
- **gitlab-ci:** rehost 'docker:latest' image in 'images' job ([c4cfc9a](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/c4cfc9aa78e408586247741944cd00c85cb3f20a))
- **gitlab-ci:** rehost 'quay.io/buildah/stable:latest' image ([100c069](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/100c069e5f4220f4ebfe9d12dcbb7d863665489e))
- **gitlab-ci:** implement 'deploy:container' release container image ([d3eae88](https://gitlab.com/RadianDevCore/tools/gitlab-projects-issues/commit/d3eae8870274a333768078e5fbd7f192fa717bd6))


