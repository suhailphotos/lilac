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
  set -g status-style "fg=#7c87a8,bg=#1a1b25"
  set -g message-style "fg=#cfd6f5,bg=#4c4e69"
  set -g pane-border-style "fg=#4c4e69"
  set -g pane-active-border-style "fg=#87abf5"
  set -g status-left ""
  set -g status-right "#[fg=#87abf5]#S #[fg=#7c87a8]| %H:%M"
}
if -b '[ "#{@@lilac_flavor}" = "pearlbloom" ]' {
  set -g status-style "fg=#7c87a8,bg=#1a1b25"
  set -g message-style "fg=#cfd6f5,bg=#4c4e69"
  set -g pane-border-style "fg=#4c4e69"
  set -g pane-active-border-style "fg=#87abf5"
  set -g status-left ""
  set -g status-right "#[fg=#87abf5]#S #[fg=#7c87a8]| %H:%M"
}
