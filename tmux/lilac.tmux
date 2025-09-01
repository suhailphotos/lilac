# lilac/tmux: set @lilac_flavor to one of the generated flavors, then reload tmux
set -gq @lilac_flavor "#{@@lilac_flavor}"
if -b '[ -z "#{@@lilac_flavor}" ]' { set -g @lilac_flavor "nightbloom" }
if -b '[ "#{@@lilac_flavor}" = "mistbloom" ]' {
  set -g status-style "fg=#d2dae4,bg=#98a5bd"
  set -g message-style "fg=#dae3f8,bg=#98a5bd"
  set -g pane-border-style "fg=#98a5bd"
  set -g pane-active-border-style "fg=#88bce6"
  set -g status-left ""
  set -g status-right "#[fg=#88bce6]#S #[fg=#d2dae4]| %H:%M"
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
  set -g status-style "fg=#303132,bg=#6d7075"
  set -g message-style "fg=#0c0c0c,bg=#6d7075"
  set -g pane-border-style "fg=#6d7075"
  set -g pane-active-border-style "fg=#07406f"
  set -g status-left ""
  set -g status-right "#[fg=#07406f]#S #[fg=#303132]| %H:%M"
}
