#!/usr/bin/env bash
# 重建三张方法图的 .dc.html（Design画布格式）并渲染本地预览PNG。
# 用法：bash 图表/design_canvas/build.sh   （需python3；预览需node+playwright）
set -e
H=$(cd "$(dirname "$0")" && pwd); S=$H/src; O=$H/output; mkdir -p "$O" "$H/preview"
export FIG_OUT="$O"
cat "$S/head.py" "$S/body_v5.py" "$S/tail.py" > /tmp/gen_fig1.py && python3 /tmp/gen_fig1.py
cat "$S/head.py" "$S/styles.py" "$S/body_fig2v2.py" "$S/tail_generic.py" > /tmp/gen_fig2.py && python3 /tmp/gen_fig2.py
cat "$S/head.py" "$S/styles.py" "$S/body_fig3v3.py" "$S/tail_generic.py" > /tmp/gen_fig3.py && python3 /tmp/gen_fig3.py
if command -v node >/dev/null; then
  for f in Main:fig1:718:404 Fig2:fig2:718:372 Fig3:fig3:718:426; do IFS=: read n p w h <<< "$f"
    python3 "$H/tools/mk.py" "$O/$n.dc.html" "$H/tools/_$p.html" && node "$H/tools/shot.js" "$H/tools/_$p.html" "$H/preview/$p.png" $w $h; done
fi
echo done
