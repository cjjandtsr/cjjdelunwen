body = "\n".join(bands + arrows + cards + labels)
html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Figure 1 Method overview</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Tinos:ital,wght@0,400;0,700;1,400;1,700&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
a{{color:#2F5FC4}}a:hover{{color:#1d3f8a}}
</style>
</helmet>
<div style="position: relative; width: {W}px; height: {H}px; background: #ffffff; font-family: 'Tinos', 'Times New Roman', serif; color: {INK}; overflow: hidden">
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{W},"height":{H}}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''
open(os.path.join(ROOT, "Main.dc.html"), "w", encoding="utf-8").write(html)
print("ok", len(html))
