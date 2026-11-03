// The brain picker drawn by Naota, in the owner's order (dashboard/brain-picker.js).
"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const BP = require("../../dashboard/brain-picker.js");
const read = (f) => fs.readFileSync(path.resolve(__dirname, "../../dashboard", f), "utf8");

function check(name, fn) {
  try { fn(); console.log("ok   " + name); }
  catch (e) { console.error("FAIL " + name + ": " + e.message); process.exitCode = 1; }
}
check("moving a brain up or down keeps every other brain", () => {
  assert.deepEqual(BP.moveItem(["a", "b", "c", "d"], 3, 1), ["a", "d", "b", "c"]);
  assert.deepEqual(BP.moveItem(["a", "b", "c"], 0, 2), ["b", "c", "a"]);
  assert.deepEqual(BP.moveItem(["a", "b", "c"], 1, -5), ["b", "a", "c"]);   // clamped to the top
  assert.deepEqual(BP.moveItem(["a", "b"], 5, 0), ["a", "b"]);              // bad index: unchanged
});
check("the saved order is the list of folder names, no duplicates", () => {
  const order = BP.orderFromOptions([{ brainName: "OPC" }, { brainName: "Brain Default" }, { brainName: "" }, { brainName: "OPC" }]);
  assert.deepEqual(order, ["OPC", "Brain Default"]);
});
check("the native select stays the source of truth", () => {
  const src = read("brain-picker.js");
  assert.ok(src.includes('document.getElementById("graphSource")'));
  assert.ok(src.includes('sel.dispatchEvent(new Event("change", { bubbles: true }))'), "picking fires the select's change");
  assert.ok(src.includes('fetch("/brains/order"'), "the order is saved on the server, for every device");
});
// 1.3.0: the picker is one line; New / Rename / Open folder / Delete are labelled rows in its panel that click the
// original hidden buttons, Delete last and in red.
check("brain actions are labelled rows in the panel, Delete last", () => {
  const src = read("brain-picker.js");
  const ids = [...src.matchAll(/\{ id: "(\w+)", icon:/g)].map((m) => m[1]);
  assert.deepEqual(ids, ["newBrainBtn", "renameBrainBtn", "pickFolderBtn", "delBrainBtn"]);
  assert.ok(/id: "delBrainBtn"[^}]*danger: true/.test(src), "Delete is marked danger");
  assert.ok(src.includes("if (target) target.click();"), "a row clicks the original button");
  const html = read("index.html");
  // Owner 03/11/2026 (new sidebar, old middle): the four buttons stay in the 1.2.1 top bar, beside a mirror of the picker.
  assert.ok(/class="bp-btn bp-mirror"/.test(html), "the top bar shows a mirror of the picker");
  assert.ok(src.includes('closest(".bp-mirror")'), "a mirror opens the same panel");
  ["bpick.act_new", "bpick.act_rename", "bpick.act_folder", "bpick.act_delete"].forEach((k) => {
    assert.ok(JSON.parse(read("i18n/vi.json"))[k] && JSON.parse(read("i18n/en.json"))[k], k);
  });
});
check("brains-ui keeps the server's order, Brain Default included", () => {
  const src = read("brains-ui.js");
  assert.ok(src.includes("const opt = b.is_default && defOpt ? defOpt : document.createElement(\"option\");"));
  assert.ok(src.includes("opt.dataset.notes"));
});
check("brain-picker.js loads after brains-ui.js", () => {
  const html = read("index.html");
  const at = html.indexOf("/static/brain-picker.js?v=");
  assert.ok(at > html.indexOf("/static/brains-ui.js?v=") && at > html.indexOf("/static/app.js?v="));
});
if (process.exitCode) process.exit(process.exitCode);
