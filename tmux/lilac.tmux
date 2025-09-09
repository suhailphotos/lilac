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
  set -g status-style "fg=#b1b8d0,bg=#a5a5b9"
  set -g message-style "fg=#f0f3fe,bg=#a5a5b9"
  set -g pane-border-style "fg=#a5a5b9"
  set -g pane-active-border-style "fg=#a8d9ff"
  set -g status-left ""
  set -g status-right "#[fg=#a8d9ff]#S #[fg=#b1b8d0]| %H:%M"
}
if -b '[ "#{@@lilac_flavor}" = "pearlbloom" ]' {
  set -g status-style "fg=#303132,bg=#6d7075"
  set -g message-style "fg=#0c0c0c,bg=#6d7075"
  set -g pane-border-style "fg=#6d7075"
  set -g pane-active-border-style "fg=#07406f"
  set -g status-left ""
  set -g status-right "#[fg=#07406f]#S #[fg=#303132]| %H:%M"
}
