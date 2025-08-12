# Project cmd~ai~

/Another ChatGPT project. CLI one /

## New:

1.  0.3.0 - names are separate, history is always! loaded.

TODO : documentation now

------------------------------------------------------------------------

README for version `0.0.8`

## EXAMPLE

`cmd_ai "Jak bude zitra (pouze) ve Stredoceskem kraji?" -u -vcs`

`cmd_ai -a dalle "Landscape with hills and lakes, photographic quality"`

## Installation

It should work with `pip3 install`, not tested yet.

Needs `API_KEY` for OpenAI in `~/.openai.token` , than it creates own
copy at `~/.config/cmd_ai/cfg.json`

## Main Features

-   terminal with gpt4
-   incremental saving conversation to `conversations.org`
-   *pythonista* mode
-   shows (keepsrecords) the spent money
-   saves PY/SH code to `/tmp` and lets it execute with `.e`
-   PIPE mode

## Help

``` example

.h      help
.q      quit
.e      execute code
.r      reset messages, scripts
.l      show tokens
.m      show models
.l number ... change limit tokens
________________ ROLES _____________
.a   assistant
.t   translator
.p   python coder
.s   secretary (.g for gmail and calendar)
.d   NO dalle
________________ MODEL
.i   NO use dalle
.v   NO use vision
```

### Assistent

Instructed to be brief and clear, non-repetitive

### Secretary

Instructed to be brief and clear, non-repetitive, uses gmail and
calendar, checks time everytime.

### Pythonista

Be brief, one code block per answer max. Creates a file in /tmp and lets
it run with `.e`{.verbatim}

### Piper

Works only from commandline, when pipe (stdin) is detected. No memory,
on task/question, asks before runs the code

### Dalle

Gets one image, 1024x1024, restricted prompt rewrite

1.  [DONE]{.done .DONE} Commit message example

    ``` example
    git diff | ai 'write a commit message, show it as git commit -a -m "message" command'
    ```

## DOING Function calls / tools

-   `function_*.py` files

-   This is in an experimental phase

-   the best guide is at
    <https://platform.openai.com/docs/guides/function-calling>

### [DONE]{.done .DONE} Weather grab test (needs some tweak to prompt to focus on SCK) {#weather-grab-test-needs-some-tweak-to-prompt-to-focus-on-sck}

-   today or tommorow is understood

### WAITING Document upload

-   it costs 0.20\$ per 1GB per day....

## Images

### [DONE]{.done .DONE} Dalle3 {#dalle3}

First attmpt works also in cmdline (-a dalle)

### [TODO]{.todo .TODO} Upload for analysis to GPT-v {#upload-for-analysis-to-gpt-v}

That would be interesting from commandline

# Dependencies

-   googlesearch-python

### Adding TasksAPI

pip install --upgrade google-api-python-client google-auth-httplib2
google-auth-oauthlib
