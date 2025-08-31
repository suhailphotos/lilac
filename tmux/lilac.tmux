# lilac/tmux: set @lilac_flavor to one of the generated flavors, then reload tmux
set -gq @lilac_flavor "#{@@lilac_flavor}"
if -b '[ -z "#{@@lilac_flavor}" ]' { set -g @lilac_flavor "nightbloom" }
if -b '[ "#{@@lilac_flavor}" = "mistbloom" ]' {
  set -g status-style "fg=#848faa,bg=#1f2230"
  set -g message-style "fg=#d1d8f6,bg=#535a73"
  set -g pane-border-style "fg=#535a73"
  set -g pane-active-border-style "fg=#7eabf3"
  set -g status-left ""
  set -g status-right "#[fg=#7eabf3]#S #[fg=#848faa]| %H:%M"
}
if -b '[ "#{@@lilac_flavor}" = "nightbloom" ]' {
  set -g status-style "fg=#848da8,bg=#8787a5"
  set -g message-style "fg=#d1d9f6,bg=#8787a5"
  set -g pane-border-style "fg=#8787a5"
  set -g pane-active-border-style "fg=#95d0ff"
  set -g status-left ""
  set -g status-right "#[fg=#95d0ff]#S #[fg=#848da8]| %H:%M"
}
if -b '[ "#{@@lilac_flavor}" = "pearlbloom" ]' {
  set -g status-style "fg=#303132,bg=#818485"
  set -g message-style "fg=#0c0c0c,bg=#818485"
  set -g pane-border-style "fg=#818485"
  set -g pane-active-border-style "fg=#073d6a"
  set -g status-left ""
  set -g status-right "#[fg=#073d6a]#S #[fg=#303132]| %H:%M"
}
