# Publishing this site

The URL `tgreen-fe.github.io` is the address the CV header will carry, so it
has to be the canonical address. Publish the site first, then add the URL to
the CV (adding it while the site 404s is the pre-send blocker in the
checklist). A GitHub *user* site is served from a repo named exactly after
the account.

## One time

1. Create the repo on GitHub, named exactly `tgreen-fe.github.io`, public,
   with no README, no .gitignore and no licence (this folder already has what
   it needs).

2. From inside this folder:

```sh
git init -b main
git add .
git commit -m "Portfolio site: six project case studies"
git remote add origin https://github.com/tgreen-fe/tgreen-fe.github.io.git
git push -u origin main
```

3. On GitHub, go to Settings, then Pages. Set Source to "Deploy from a branch",
   branch `main`, folder `/ (root)`. Save.

Give it two or three minutes, then load https://tgreen-fe.github.io and check
that the CV downloads and the figures render.

## Every update after that

```sh
git add . && git commit -m "what changed" && git push
```

Pages redeploys on push, usually within a minute.

## If you add a custom domain later

Put the domain in Settings > Pages > Custom domain. GitHub writes a CNAME file
and redirects `tgreen-fe.github.io` to the new address, so the links on CVs you
have already sent keep working.
