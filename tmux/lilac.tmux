# lilac/tmux: set @lilac_flavor to one of the generated flavors, then reload tmux
set -gq @lilac_flavor "#{@@lilac_flavor}"
if -b '[ -z "#{@@lilac_flavor}" ]' { set -g @lilac_flavor "nightbloom" }
if -b '[ "#{@@lilac_flavor}" = "mistbloom" ]' {
  set -g status-style "fg=#c6c4cf,bg=#908d95"
  set -g message-style "fg=#ffffff,bg=#908d95"
  set -g pane-border-style "fg=#908d95"
  set -g pane-active-border-style "fg=#a5d0ff"
  set -g status-left ""
  set -g status-right "#[fg=#a5d0ff]#S #[fg=#c6c4cf]| %H:%M"
}
if -b '[ "#{@@lilac_flavor}" = "nightbloom" ]' {
  set -g status-style "fg=#b4b3c0,bg=#84838c"
  set -g message-style "fg=#ebeaf3,bg=#84838c"
  set -g pane-border-style "fg=#84838c"
  set -g pane-active-border-style "fg=#a5befa"
  set -g status-left ""
  set -g status-right "#[fg=#a5befa]#S #[fg=#b4b3c0]| %H:%M"
}
if -b '[ "#{@@lilac_flavor}" = "pearlbloom" ]' {
  set -g status-style "fg=#303132,bg=#868686"
  set -g message-style "fg=#020202,bg=#868686"
  set -g pane-border-style "fg=#868686"
  set -g pane-active-border-style "fg=#1275be"
  set -g status-left ""
  set -g status-right "#[fg=#1275be]#S #[fg=#303132]| %H:%M"
}
