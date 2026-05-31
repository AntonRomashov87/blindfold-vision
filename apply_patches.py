#!/usr/bin/env python3
"""
Run this script alongside logo.png and your blindfold_vision.html:
  python3 apply_patches.py blindfold_vision.html
It creates blindfold_vision_patched.html with all 3 changes applied.
"""
import sys, base64, os

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else 'blindfold_vision.html'
    with open(src, encoding='utf-8') as f:
        html = f.read()

    changes = 0

    # ── CHANGE 1: Logo ──
    logo_path = os.path.join(os.path.dirname(src), 'logo.png')
    if os.path.exists(logo_path):
        with open(logo_path, 'rb') as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        logo_uri = f"data:image/png;base64,{logo_b64}"
        old = '<div class="home-eye">♟</div>'
        new = (f'<div class="home-eye"><img src="{logo_uri}" alt="Smart Chess System" '
               f'style="width:90px;height:90px;object-fit:contain;'
               f'filter:drop-shadow(0 0 20px rgba(232,184,75,0.4));'
               f'animation:pulse 3s ease-in-out infinite"></div>')
        if old in html:
            html = html.replace(old, new)
            changes += 1
            print("✅ Change 1: Logo applied")
        else:
            print("⚠️  Change 1: Logo target not found (already patched?)")
    else:
        print("⚠️  Change 1: logo.png not found, skipping")

    # ── CHANGE 2: Grammar fixes ──
    grammar_patches = [
        ("text:`На якій горизонталі стоїть ${preciseLabelAcc(p)}?`,",
         "text:`На якій горизонталі стоїть ${preciseLabel(p)}?`,"),
        ("text:`На якій лінії стоїть ${preciseLabelAcc(p)}?`,",
         "text:`На якій лінії стоїть ${preciseLabel(p)}?`,"),
        ("text:`На якому полі стоїть ${preciseLabelAcc(p)}?`,",
         "text:`На якому полі стоїть ${preciseLabel(p)}?`,"),
    ]
    for old, new in grammar_patches:
        if old in html:
            html = html.replace(old, new)
            changes += 1
            print(f"✅ Grammar fix: {old[:60]}…")
        else:
            print(f"⚠️  Not found: {old[:60]}…")

    # ── CHANGE 3: Trainer — "← Головна" to top ──
    old3 = ('  <div class="screen-header">\n'
            '    <div class="page-title" style="margin-bottom:0">🎓 Учні</div>\n'
            '    <div style="display:flex;gap:8px">\n'
            '      <button class="btn btn-outline btn-sm" onclick="trainerRefresh()">🔄</button>\n'
            '      <button class="btn btn-sm" onclick="exportExcel()">⬇ Excel</button>\n'
            '    </div>\n'
            '  </div>')
    new3 = ('  <div class="screen-header">\n'
            '    <div class="page-title" style="margin-bottom:0">🎓 Учні</div>\n'
            '    <div style="display:flex;gap:8px">\n'
            '      <button class="btn btn-outline btn-sm" onclick="goHome()">← Головна</button>\n'
            '      <button class="btn btn-outline btn-sm" onclick="trainerRefresh()">🔄</button>\n'
            '      <button class="btn btn-sm" onclick="exportExcel()">⬇ Excel</button>\n'
            '    </div>\n'
            '  </div>')
    if old3 in html:
        html = html.replace(old3, new3)
        changes += 1
        print("✅ Change 3a: Головна moved to top")
    else:
        print("⚠️  Change 3a: trainer header not found")

    # Remove duplicate bottom "← Головна" from trainer dashboard
    old3b = '  <button class="btn btn-outline" style="margin-top:12px" onclick="goHome()">← Головна</button>\n</div>\n\n<!-- ═══ TRAINER PLAYER DETAIL'
    new3b = '</div>\n\n<!-- ═══ TRAINER PLAYER DETAIL'
    if old3b in html:
        html = html.replace(old3b, new3b)
        changes += 1
        print("✅ Change 3b: Duplicate Головна removed")

    # ── CHANGE 4: Delete student in trainer panel ──
    # Add trainerDeletePlayer function
    delete_fn = """
// ── Delete student from Firebase ──
async function trainerDeletePlayer(key, name){
  if(!fbDB){ notif('Firebase не підключено'); return; }
  if(!confirm(`Видалити учня "${name}"? Всі дані буде втрачено.`)) return;
  try{
    await fbDB.ref(`${FB_ROOT}/players/${key}`).remove();
    delete trainerData[key];
    renderTrainerSummary();
    trainerFilterRender();
    notif(`✅ Учня "${name}" видалено`);
  }catch(e){
    notif('Помилка видалення: '+e.message);
  }
}

"""
    anchor = "// ── Current player name ──"
    if anchor in html and "trainerDeletePlayer" not in html:
        html = html.replace(anchor, delete_fn + anchor)
        changes += 1
        print("✅ Change 4a: Delete function added")

    # Modify trainer row HTML to add delete button
    old_row = """    html+=`
      <div class="trainer-row" onclick="trainerShowPlayer('${p.key}')">
        <div class="tr-rank">${medal}</div>
        <div class="tr-info">
          <div class="tr-name">${p.name||'?'}</div>
          <div class="tr-meta">✅${p.total?.c||0} ❌${p.total?.w||0} · глиб.${p.best||0} · ${p.lastSeen||'—'}</div>
          <div class="tr-bar"><div class="tr-bar-fill" style="width:${pct}%"></div></div>
          <div style="margin-top:4px">${catHtml}</div>
        </div>
        <div class="tr-pct">${pct}%</div>
      </div>`"""
    new_row = """    html+=`
      <div class="trainer-row" style="cursor:default">
        <div onclick="trainerShowPlayer('${p.key}')" style="display:flex;align-items:center;gap:10px;flex:1;min-width:0;cursor:pointer">
          <div class="tr-rank">${medal}</div>
          <div class="tr-info">
            <div class="tr-name">${p.name||'?'}</div>
            <div class="tr-meta">✅${p.total?.c||0} ❌${p.total?.w||0} · глиб.${p.best||0} · ${p.lastSeen||'—'}</div>
            <div class="tr-bar"><div class="tr-bar-fill" style="width:${pct}%"></div></div>
            <div style="margin-top:4px">${catHtml}</div>
          </div>
          <div class="tr-pct">${pct}%</div>
        </div>
        <button class="p-item-del" onclick="trainerDeletePlayer('${p.key}','${(p.name||'').replace(/'/g,\\\"'\\\")}')" title="Видалити учня">✕</button>
      </div>`"""
    if old_row in html:
        html = html.replace(old_row, new_row)
        changes += 1
        print("✅ Change 4b: Delete button added to trainer rows")
    else:
        print("⚠️  Change 4b: trainer row template not found (may need manual check)")

    # Write output
    out = src.replace('.html', '_patched.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n✅ Done! {changes} changes applied.")
    print(f"📄 Output: {out}")

if __name__ == '__main__':
    main()
