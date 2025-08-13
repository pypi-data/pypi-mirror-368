# gbp-webhook-playsound

A [gbp-webhook](https://github.com/enku/gbp-webhook) plugin to play a sound on
your desktop on events.  It currently reacts only to the `build_pulled` event
(see [gbp-notifications](https://github.com/enku/gbp-notifications)).



## Installation

gbp-webhook-playsound requires gbp-webhook (which requires
[gbpcli](https://github.com/enku/gbpcli)). You should install
gbp-webhook-playsound in the same (virtual) environment that you installed
those two. For example:

```console
$ pip install --user gbp-webhook-playsound
```

or

```console
$ pipx inject gbpcli gbp-webhook-playsound
```

## Usage

You should ensure that gbp-notifications is installed on the [Gentoo Build
Publisher](https://github.com/enku/gentoo-build-publisher) server for which
you want to subscribe and the webhook receiver is configured to receive
`build_pulled` events:

#### On the server

```toml
# /etc/gbp-notifications.toml

[recipients]
laptop = { webhook = "https://laptop:5000/webhook|X-Pre-Shared-Key=foobar" }

[subscriptions]
babette = { build_pulled = ["laptop"] }
```

As gbp-webhook-playsound is a plugin for gbp-webhook, it is picked up
automatically when that application is run (see the README for details). In
order to be picked up it requires a restart of the gbp-webhook service. In
systemd this means

```console
$ systemctl restart --user gbp-webhook
```

## Environment variables

Like gbp-webhook, gbp-webhook-playsound can be configured via environment
variables.  If you are using the (preferred) systemd integration, then they
will be defined in `~/.config/gbp-webhook.conf`.  The following environment
variables are recognized:

- `GBP_WEBHOOK_PLAYSOUND_BUILD_PULLED`: If provided, uses the sound file in
  this variable to play instead of the default sound.
- `GBP_WEBHOOK_PLAYSOUND_PLAYER`: The name/path to use to play the sound file.
  The default is "pw-play".


## Audio Attribution

This project uses the "Level Up" audio file from
[Pixabay](https://pixabay.com/). The audio file is licensed under the Pixabay
Content License, which allows for free use without attribution, but we still
want to give credit to the creator.

- **Audio Title:** Level Up
- **Artist:** [Universfield](https://pixabay.com/users/universfield-28281460/)
- **Source:** https://pixabay.com/sound-effects/level-up-191997/
- **License:** https://pixabay.com/service/license-summary/
