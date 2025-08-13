# gbp-webhook-tts

A [gbp-webhook](https://github.com/enku/gbp-webhook) plugin to speak the name
of a machine or machines when a build is pulled for that machine.  See
[gbp-notifications](https://github.com/enku/gbp-notifications).  The `tts` in
gbp-webhook-tts stands for "text to speech".


## Installation

gbp-webhook-tts requires gbp-webhook (which requires
[gbpcli](https://github.com/enku/gbpcli)). You should install gbp-webhook-tts
in the same (virtual) environment that you installed those two. For example:

```console
$ pip install --user gbp-webhook-tts
```

or

```console
$ pipx inject gbpcli gbp-webhook-tts
```

## Usage

You should ensure that gbp-notifications is installed on the [Gentoo Build
Publisher](https://github.com/enku/gentoo-build-publisher) server for which
you want to subscribe and the webhook receiver is configured to receive
`build_pulled` events.

This plugin uses [AWS Polly](https://aws.amazon.com/polly/) to convert text to
to speech. As such it requires you to have an AWS account and an access
account to AWS Polly. It uses standard [AWS
(boto3)](https://github.com/boto/boto3) environment variables to configure
access to AWS and this can be set in the `~/.config/gbp-webhook.conf` file.
For example:

```
AWS_ACCESS_KEY_ID=QVCLXRFGNHXLJRSXZQZK
AWS_SECRET_ACCESS_KEY=vRgJyuacKhYPdTEzopGEMxrvWDSSWavXGEROZbdY
AWS_DEFAULT_REGION=us-east-2
```

#### On the server

```toml
# /etc/gbp-notifications.toml

[recipients]
laptop = { webhook = "https://laptop:5000/webhook|X-Pre-Shared-Key=foobar" }

[subscriptions]
babette = { build_pulled = ["laptop"] }
```

As gbp-webhook-tts is a plugin for gbp-webhook, it is picked up automatically
when that application is run (see the README for details). In order to be
picked up it requires a restart of the gbp-webhook service. In systemd this
means

```console
$ systemctl restart --user gbp-webhook
```


## Environment variables

Like gbp-webhook, gbp-webhook-tts can be configured via environment variables.
If you are using the (preferred) systemd integration, then they will be
defined in `~/.config/gbp-webhook.conf`.  The following environment variables
are recognized:

- `GBP_WEBHOOK_TTS_DELAY`: If provided, there will be a delay (in seconds)
  between the time that the notification is received and the machine name is
  spoken. The default is `0` meaning no delay.

In addition environment variables prefixed with `GBP_WEBHOOK_TTS_PHONETIC_`
will be used to pass a "phonetic" translation to the text-to-speech engine.
This can be used in cases where the spelling and the sound of a machine name
differ, or where the TTS engine misspeaks.  For example if one has a GBP
machine called "kde-desktop" one could use the environment variable setting:

```sh
GBP_WEBHOOK_TTS_PHONETIC_KDE_DESKTOP="kay-dee-ee desktop"
```

## Cache

gbp-webhook-tts caches the audio received from the TTS engine. This is used to
both speed up the processing and to save on AWS charges.  The cached audio is
stored in `~/.cache/gbp-webhook/tts/`, for example
`~/.cache/gbp-webhook/tts/kde-desktop.mp3`. These audio files can be safely
deleted and will be re-created on demand.


## Tips

I use this plugin in concert with
[gbp-webhook-playsound](https://github.com/enku/gbp-webhook-playsound), with a
0.8-second delay. So I effectively get a chime followed by the name of the
machine.
