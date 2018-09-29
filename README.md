## What is ansible-acme-sh? [![Build Status](https://secure.travis-ci.org/nickjj/ansible-acme-sh.png)](http://travis-ci.org/nickjj/ansible-acme-sh)

It is an [Ansible](http://www.ansible.com/home) role to:

- Install acme.sh to issue, renew or remove Let's Encrypt based SSL certificates
- Issue certificates for single, multiple or wildcard domains
- Configure multiple domains through 1 certificate or separate certificates
- Issue DNS based challenges using acme.sh's automated DNS API feature
- Run custom acme.sh commands if the presets are not enough for you

## Why would you want to use this role?

This role uses [acme.sh](https://github.com/Neilpang/acme.sh) which is a self
contained Bash script to handle all of the complexities of issuing and
automatically renewing your SSL certificates.

This role's goals are to be highly configurable but have enough sane defaults
so that you can get going by supplying nothing more than a list of domain names,
setting your DNS provider and supplying your DNS provider's API key.

It's also idempotent for every task because that's the only way I roll!

#### Why is DNS based challenges the only supported method?

Having challenges done through DNS means you can set up your certificates before
your web server or proxy is provisioned. It also means your web server doesn't
need to know anything about how the ACME challenge works. All you have to do is
reference the final certificates this role generates.

Another perk is if you're running a web server inside of Docker, you might not
have that up and running until after your server has been provisioned by Ansible.
For example, it's common to set up git based deploys to kick off an app deploy.

Also, it's nice using DNS challenges because DNS challenges are the only way to
issue wildcard certificates using Let's Encrypt. Focusing efforts onto 1 solution
that works with all certificate types seemed like the right move.

With that said, I probably won't be supporting other modes such as standalone,
webroot, nginx or Apache but nothing is set in stone.

## Supported platforms

- Ubuntu 16.04 LTS (Xenial)
- Ubuntu 18.04 LTS (Bionic)
- Debian 8 (Jessie)
- Debian 9 (Stretch)

## Role variables

```
# The user on the system that acme.sh will run as. Keep in mind this user
# needs to already exist, this role will not create it.
acme_sh_become_user: "root"

# The acme.sh repo to clone.
acme_sh_git_url: "https://github.com/Neilpang/acme.sh"

# The branch, tag or commit that will be cloned.
acme_sh_git_version: "master"

# By default if you were to clone this repo now and then 6 months from now you
# clonged it again, it will stick with the old master version from 6 months ago.
# If you want to pull the latest master version on every run, set this to True.
acme_sh_git_update: False

# Where will this repo get cloned to?
acme_sh_git_clone_dest: "/usr/local/src/acme.sh"

# When enabled, acme.me will upgrade itself to the latest version which is
# separate from updating the git repo. That's because acme.sh installs itself
# with an installer after cloning the source code.
#
# Enabling it could be good to get the latest release which may have bug fixes
# but keep in mind if you do this, you may get different results per run. I
# recommend occasionally setting this to True but keeping it disabled usually.
acme_sh_upgrade: False

# When enabled the cloned source code, installation path, log files and renewal
# cron jobs will be removed.
#
# Installed certificates will not be removed. If you want to remove the installed
# certificates there is another option for that which we'll cover later.
acme_sh_uninstall: False

# When creating an initial Let's Encrypt account, you can optionally supply an
# email address. By default this isn't set, but feel free to add your email
# address in if you want. If you do set it, you'll get emailed when your
# certificates are within 20 days of expiring.
#
# I highly recommend setting this because if all goes as planned you'll never
# get emailed unless acme.sh malfunctioned and failed to renew a certificate.
acme_sh_account_email: ""

# Certificates will be renewed through an acme.sh managed cron job. By default
# acme.sh uses 60 days for each renewal attempt, but I've chosen to go with 30
# by default to give 1 extra attempt in case something unexpected happens.
#
# Certificates that don't need to be renewed will be skipped by acme.sh, so
# it's all good. It's also worth mentioning this value cannot be > 60 days which
# is a limit enforced by acme.sh, this role does not double check the value.
acme_sh_renew_time_in_days: 30

# The base path where certificates will be copied into. If you're familiar with
# acme.sh, this is for the certificates generated with --install-cert.
#
# This is the final destination for your certificates and the user you've chosen
# will need write access to this path. This path will end up being having its
# owner:group set to the acme_sh_become_user's value.
acme_sh_copy_certs_to_path: "/etc/ssl/ansible"

# At the end of the run, an Ansible debug message will print out a list of
# domains that have valid SSL certificates along with their expiration dates.
# You can disable this by setting it to False.
acme_sh_list_domains: True

# When set to False, it will use the live Let's Encrypt servers, so please make
# sure everything works with staging True or you may find yourself rate limited.
#
# It is worth mentioning you'll need to force issue a new certificate when
# swiching between staging and live or vice versa.
acme_sh_default_staging: True

# When set to True, this will regenerate a new certificate even if your list of
# domains didn't change. It's also used to set a new DNS provider and API keys.
#
# Be careful with this because you may get rate limited if on the live server.
# Only consider using this to update your DNS provider. You should set it back
# to False when you're done.
acme_sh_default_force_issue: False

# When set to True, this will regenerate a new certificate for an existing list
# of certificates. This will not update your DNS provider or API keys.
#
# This could be useful to use if your certificates expired. You should set it
# back to False when you're done.
acme_sh_default_force_renew: False

# When set to True, this will provide more detailed information to STDOUT. This
# could be useful if you're testing the role in staging mode.
acme_sh_default_debug: False

# Which DNS provider should you use?
# A list of supported providers can be found at:
#   https://github.com/Neilpang/acme.sh#7-automatic-dns-api-integration
# As for getting the name to use, you can find that at:
#   https://github.com/Neilpang/acme.sh/tree/master/dnsapi
#
# It defaults to DigitalOcean. Make sure to include the dns_ part of the name,
# but leave off the .sh file extension.
acme_sh_default_dns_provider: "dns_dgon"

# What are your DNS provider's API key(s)?
# The key names to use can be found at:
#   https://github.com/Neilpang/acme.sh/tree/master/dnsapi
#
# The API key can be created on your DNS provider's website. Some providers
# require 1 key, while others require 2+. Just add them as key / value pairs here
# without the "export ".
#
# For example if you were using DigitalOcean you would enter:
#    acme_sh_default_dns_provider_api_keys:
#      "DO_API_KEY": "THE_API_SECRET_TOKEN_FROM_THE_DO_DASHBOARD"
acme_sh_default_dns_provider_api_keys: {}

# How long should acme.sh sleep after attempting to set the TXT record to your
# DNS records? Some DNS providers do not update as fast as others.
#
# 120 is the default value from acme.sh itself but keep in mind if you use
# NameSilo, their DNS updates only propagate once per 15 minutes so you'll need
# to set this value to 900 or you run the risk of getting a DNS NXDOMAIN error.
#
# I recommend keeping it set to 120 or higher if your DNS provider requires it.
#
# Although as an aside, I used 10 when testing this role against DigitalOcean
# and it worked about 30 times in a row. Still, in production I would use 120
# just to be safe because this 2 minute delay will only affect you on the first
# Ansible run. After that it will be updated in the background through a cron job.
acme_sh_default_dns_sleep: 120

# When issuing new certificates, you can choose to add additional flags that
# are not present here by default. Supply them just as you would on the command
# line, such as "--help".
acme_sh_default_extra_flags_issue: ""

# When renewing certificates, you can choose to add additional flags that
# are not present here by default. Supply them just as you would on the command
# line, such as "--help".
acme_sh_default_extra_flags_renew: ""

# When installing certificates, you can choose to add additional flags that
# are not present here by default. Supply them just as you would on the command
# line, such as "--help".
#
# Installing is different than issuing and we'll cover that later.
acme_sh_default_extra_flags_install_cert: ""

# When a certificate is issued or renewed, acme.sh will attempt to run a command
# of your choosing. This could be to restart or reload your web server or proxy.
#
# Keep in mind the user you set in acme_sh_become_user needs access rights to
# sudo if you use sudo here, or if not, they need access rights to reload your
# web server / proxy.
#
# For a Docker example, check the example section of this README.
acme_sh_default_install_cert_reloadcmd: "sudo systemctl reload nginx"

# If you need more fine grain control than the reloadcmd you can hook into the
# life cycle of issuing or renewing a certificate. By default the following 3
# options do nothing unless you fill them out. They are not needed for everything
# to function as long as your reloadcmd works.
#
# When a certificate is issued or renewed, acme.sh will attempt to run a command
# before attempting to issue a certificate. This can only be applied while
# issuing a certificate but it will be saved and used for renewing as well.
#
# This will execute even if the certificate wasn't successfully issued / renewed.
acme_sh_default_issue_pre_hook: ""

# When a certificate is issued or renewed, acme.sh will attempt to run a command
# after attempting to issue a certificate. This can only be applied while
# issuing a certificate but it will be saved and used for renewing as well.
#
# This will execute even if the certificate wasn't successfully issued / renewed.
acme_sh_default_issue_post_hook: ""

# When a certificate is issued or renewed, acme.sh will attempt to run a command
# after a certificate is successfully renewed. This can only be applied while
# issuing a certificate but it will be saved and used for renewing as well.
#
# This will only execute if the certificate was successfully issued / renewed.
acme_sh_default_issue_renew_hook: ""

# When set to True, certificates will be removed and unset from being renewed
# instead of being created and set for renewal. This will not uninstall acme.sh.
acme_sh_default_remove: False

# This list contains a list of domains, along with key / value pairs to
# configure each set of domains individually.
#
# Here's an example with every available option documented, and a couple of real
# examples will also be included in the example section of this README:
acme_sh_domains:
#  A list of 1 or more domains, you can use ["*.example.com" ,"example.com] for
# setting a wildcard + root domain certificate. Domains listed here will
#  all belong to the same certificate. If you want separate certificate files
#  then create a new "domains:" item in the list.
#
#  The first domain in the list will end up being used as a base file name for
#  the certificate name. In this case it would be "example.com.pem".
#  - domains: ["example.com", "www.example.com]
#    # Optionally override the default staging variable. This overall pattern lets
#    # you situationally override the defaults listed above for each domain list.
#    staging: False
#    # Optionally force issue new certificates.
#    force_issue: False
#    # Optionally force renew certificates.
#    force_renew: False
#    # Optionally turn on debug mode.
#    debug: True
#    # Optionally override the default DNS provider.
#    dns_provider: "dns_namesilo"
#    # Optionally override the default DNS API keys.
#    dns_provider_api_keys:
#     "Namesilo_Key": "THE_API_SECRET_TOKEN_FROM_THE_NAMESILO_DASHBOARD"
#    # Optionally override the default DNS sleep time.
#    dns_sleep: 900
#    # Optionally add extra flags to any of these 3 actions:
#    extra_flags_issue: ""
#    extra_flags_renew: ""
#    extra_flags_install_cert: ""
#    # Optionally set a different reload command.
#    install_cert_reloadcmd: "whoami"
#    # Optionally run commands during different points in the cert issue process:
#    extra_issue_pre_hook: ""
#    extra_issue_post_hook: ""
#    extra_issue_renew_hook: ""
#    # Optionally remove and disable the certificate.
#    remove: True

# How long should the apt-cache last in seconds?
acme_sh_apt_cache_time: 86400
```

## Example usage

For the sake of this example let's assume you have a group called **app** and
you have a typical `site.yml` file.

To use this role edit your `site.yml` file to look something like this:

```
---

- name: Configure app server(s)
  hosts: "app"
  become: True

  roles:
    - { role: "nickjj.acme-sh", tags: ["acme-sh"] }
```

Here's a few examples. You can recreate this example on your end by opening or
creating `group_vars/app.yml` which is located relative to your `inventory`
directory and  then making it look like this:

```
---

acme_sh_account_email: "you@example.com"

# An example where a DNS provider has 2 keys for API access:
acme_sh_default_dns_provider: "dns_cf"
acme_sh_default_dns_provider_api_keys:
  "CF_Key": "THE_API_SECRET_TOKEN_FROM_THE_CLOUDFLARE_DASHBOARD"
  "CF_Email: "you@example.com"

# Reloading nginx inside of a Docker container that is named "nginx".
# If you are running nginx in a Docker container then you'll also need to volume
# mount in your certificates, but I'm sure you knew that already!
acme_sh_default_install_cert_reloadcmd: "docker exec nginx nginx -s reload"

# --- Here's a few different acme_sh_domains examples --------------------------
# You would only need to supply one of these based on what you wanted to do!
# ------------------------------------------------------------------------------

# 1 certificate file for all of the domains.
acme_sh_domains:
  - domains: ["example.com", "www.example.com", "admin.example.com"]

# Produces this on your server:
#   /etc/ssl/ansible/example.com.key (the private key)
#   /etc/ssl/ansible/example.com.pem (the full chain certificate)

# ------------------------------------------------------------------------------

# 2 certificate files using the same domains as above.
acme_sh_domains:
  - domains: ["example.com", "www.example.com"]
  - domains: ["admin.example.com"]

# Produces this on your server:
#   /etc/ssl/ansible/example.com.key (the private key)
#   /etc/ssl/ansible/example.com.pem (the full chain certificate)
#   /etc/ssl/ansible/admin.example.com.key (the private key)
#   /etc/ssl/ansible/admin.example.com.pem (the full chain certificate)

# ------------------------------------------------------------------------------

# 2 certificate files using the same example but the admin certificate will get
# removed and disabled.
acme_sh_domains:
  - domains: ["example.com", "www.example.com"]
  - domains: ["admin.example.com"]
    remove: True

# Produces this on your server:
#   /etc/ssl/ansible/example.com.key (the private key)
#   /etc/ssl/ansible/example.com.pem (the full chain certificate)

# ------------------------------------------------------------------------------

# 2 certificate files using the same example but switching from staging to live
# on admin.example.com (but remember to remove force_issue after it runs once).
acme_sh_domains:
  - domains: ["example.com", "www.example.com"]
  - domains: ["admin.example.com"]
    staging: False
    force_issue: True

# ------------------------------------------------------------------------------

# 2 certificate files using the same example but forcing a renew on
# admin.example.com (let's say a catastrophic error happened and the cert expired).
acme_sh_domains:
  - domains: ["example.com", "www.example.com"]
  - domains: ["admin.example.com"]
    force_renew: True
```

*If you're looking for an Ansible role to create users, then check out my
[user role](https://github.com/nickjj/ansible-user)*.

Now you would run `ansible-playbook -i inventory/hosts site.yml -t acme-sh`.

## Installation

`$ ansible-galaxy install nickjj.acme-sh`

## Ansible Galaxy

You can find it on the official
[Ansible Galaxy](https://galaxy.ansible.com/nickjj/acme-sh/) if you want to
rate it.

## License

MIT
