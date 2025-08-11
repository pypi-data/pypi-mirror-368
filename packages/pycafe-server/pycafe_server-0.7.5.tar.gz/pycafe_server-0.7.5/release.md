# Fully automated

    $ ./release.sh patch

## Making an alpha release

    $ ./release.sh patch --new-version 0.7.5a1

# semi automated

To make a new release

```
# update src/pycafe_server/__about__.py
$ git add -u && git commit -m 'Release v0.7.5' && git tag v0.7.5 && git push upstream master v0.7.5
```

If a problem happens, and you want to keep the history clean

```
# drop the automatically created commits
$ git rebase -i HEAD~3
$ git tag v0.7.5 -f &&  git push upstream master v0.7.5 -f
```
