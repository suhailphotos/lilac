-- plugin/lilac.lua
local ok, lilac = pcall(require, "lilac")
if not ok then return end

vim.api.nvim_create_user_command("Lilac", function(opts)
  lilac.load(opts.args)
end, {
  nargs = 1,
  complete = function()
    local ok2, f = pcall(require, "lilac.flavors")
    if not ok2 then return {} end
    local out = {}
    for _, e in ipairs(f.list or {}) do table.insert(out, e.id) end
    return out
  end,
})

vim.api.nvim_create_user_command("LilacList", function()
  local ok2, f = pcall(require, "lilac.flavors")
  if not ok2 then
    print("No flavors generated yet. Run: python3 tools/gen.py")
    return
  end
  for _, e in ipairs(f.list or {}) do
    print(string.format("%s\t(%s)", e.id, e.label or e.id))
  end
end, {})

vim.api.nvim_create_user_command("LilacTransparentToggle", function()
  lilac.toggle_transparent()
end, {})
