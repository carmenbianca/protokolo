- Fixed a bug where, if a subdirectory in `changelog.d` did not contain a
  `.protokolo.toml` file, the program would crash.
- Made sure that `changelog.d` subdirectories that do not contain a
  `.protokolo.toml` file retain all their files after `protokolo compile` is
  run.
