# taplo-shell

custom taplo docker image with shell environment for ci/cd usage.

## rationale

upstream `tamasfe/taplo` went full distroless (no shell, no nothing) which breaks gitlab-ci jobs that expect basic posix tooling. this wrapper adds alpine base with the taplo binary for compatibility.

## usage

```yml
check:toml:
  stage: test
  image: shaddydc/taplo
  script:
    - taplo lint "**/*.toml"
    - taplo format "**/*.toml" --check
```

## maintenance

both base alpine and source taplo images are pinned with sha256 hashes and kept current via renovate bot.

## alternatives

- `nixery.dev/shell/taplo` - cleaner, bigger and requires nix literacy
- installing taplo manually in alpine job - slower, less cacheable
