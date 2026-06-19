A stray non-YAML file in a module directory. The config loader treats every entry
under a module folder as a release file, so this must be rejected with a LoadError.
