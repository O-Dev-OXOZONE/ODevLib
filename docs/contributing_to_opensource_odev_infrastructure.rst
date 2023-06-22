Contributing to open-source O.dev infrastructure
================================================

O.dev hosts some of internal infrastructure and libraries as open-source projects.

Our main private projects pipeline (which happens on GitLab) differs from the
open-source one (which happens on GitHub), to suit common open-source flow:

- Every contributor forks repository
- All contributor's work happens in his own repository
- Once changes are ready, contributor creates a pull request 
  from own repository to O.dev repository
- Review and discussion happens publicly in comments by entire community
- After all concerns (if any) are ruled out, pull request is merged,
  and version is bumped.

We use semantic versioning, consisting of 3 values:

- Major version is incremented when there are major breaking changes
- Minor version is incremented when there are new features
- Patch version is incremented when there are bug fixes

During version 0.x.x, we do not guarantee backward compatibility 
between minor versions, but strive to keep it.

Main repository contains 2 branches:

- ``master``. This branch is in sync with pypi.
- ``develop``. Pull requests are merged into this branch. 
  When O.dev team is ready to release new version,
  it is thoroughly tested and merged into ``master``.
