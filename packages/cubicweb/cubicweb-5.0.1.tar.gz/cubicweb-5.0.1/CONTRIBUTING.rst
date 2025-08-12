Install from version control system
===================================

To keep-up with on-going development, clone the mercurial repository::

  hg clone -u 'last(tag())' https://forge.extranet.logilab.fr/cubicweb/cubicweb # stable version
  hg clone https://forge.extranet.logilab.fr/cubicweb/cubicweb # development branch

Then in run::

   pip install -e cubicweb

Commit messages
===============
Commits message follow the `conventional commit naming convention
<https://www.conventionalcommits.org/en/v1.0.0/>`_.

You can add the following block to your mercurial commit template:

.. code-block::

   HG: --
   HG: type(scope?): subject  #scope is optional
   HG: --
   HG: Prefix the changeset's title with the type of change that you're commiting:
   HG:    - chore:    Build process or auxiliary tool changes
   HG:    - ci:       CI related changes
   HG:    - docs:     Documentation only changes
   HG:    - feat:     Adding a new feature
   HG:    - fix:      A bug fix
   HG:    - perf:     A code change that improves prformance
   HG:    - refactor: A code change that neither fixes a bug or adds a feature
   HG:    - style:    Markup, white-space, formatting, missing semil-colons, …
   HG:    - test:     Adding missing tests
   HG:    - revert:   Revert a previous commit


Branches
========

We work on different branches during development depending on the changes we
make. The `default` branch receives commits intended to be published in the
next major version of CubicWeb. The releases branches (`4.x`, `5.x`, ..., `X.x`)
receive commits that don't include breaking changes, either new features or
bug-fixes.

The `default` branch is kept up-to-date by merging changes made on releases
branches into it regularly.

Releases
========

When releasing a new version of CubicWeb we use the `release-new` tool which
prepare an updated changelog and creates a tag. When the tag is pushed a CI
pipeline is triggered and if all the tests pass, the new version is released on
PyPI.
