-- Hide the docs helper calls (fresh_scene(...), render_result(...)) from rendered code cells.
-- The notebooks keep them, so they still run in Blender.

local function is_helper_call(line)
  return line:match("^%s*fresh_scene%(.*%)%s*$") or line:match("^%s*render_result%(.*%)%s*$")
end

function CodeBlock(el)
  if not el.classes:includes("python") then
    return nil
  end

  local kept = {}
  for line in (el.text .. "\n"):gmatch("(.-)\n") do
    if not is_helper_call(line) then
      -- drop blank lines left at the top and doubled blank lines
      local blank = line:match("^%s*$")
      local prev_blank = #kept == 0 or kept[#kept]:match("^%s*$")
      if not (blank and prev_blank) then
        table.insert(kept, line)
      end
    end
  end
  while #kept > 0 and kept[#kept]:match("^%s*$") do
    table.remove(kept)
  end

  if #kept == 0 then
    return {}
  end
  el.text = table.concat(kept, "\n")
  return el
end
