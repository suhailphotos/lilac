# lilac/tmux: set @lilac_flavor to one of the generated flavors, then reload tmux
set -gq @lilac_flavor "#{@@lilac_flavor}"
if -b '[ -z "#{@@lilac_flavor}" ]' { set -g @lilac_flavor "nightbloom" }
if -b '[ "#{@@lilac_flavor}" = "mistbloom" ]' {
  set -g status-style "fg=#babec3,bg=#596275"
  set -g message-style "fg=#d8dee9,bg=#596275"
  set -g pane-border-style "fg=#596275"
  set -g pane-active-border-style "fg=#aad1f8"
  set -g status-left ""
  set -g status-right "#[fg=#aad1f8]#S #[fg=#babec3]| %H:%M"
}
if -b '[ "#{@@lilac_flavor}" = "nightbloom" ]' {
  set -g status-style "fg=#e0def4,bg=#6e6a86"
  set -g message-style "fg=#e0def4,bg=#6e6a86"
  set -g pane-border-style "fg=#6e6a86"
  set -g pane-active-border-style "fg=#9ad0f4"
  set -g status-left ""
  set -g status-right "#[fg=#9ad0f4]#S #[fg=#e0def4]| %H:%M"
}
if -b '[ "#{@@lilac_flavor}" = "pearlbloom" ]' {
  set -g status-style "fg=#303132,bg=#868686"
  set -g message-style "fg=#020202,bg=#868686"
  set -g pane-border-style "fg=#868686"
  set -g pane-active-border-style "fg=#1275be"
  set -g status-left ""
  set -g status-right "#[fg=#1275be]#S #[fg=#303132]| %H:%M"
}
