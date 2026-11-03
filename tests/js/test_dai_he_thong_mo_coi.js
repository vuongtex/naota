/* Dải "Hệ thống" trong rail không được đứng lại một mình sau khi rỗng ruột.

       node tests/js/test_dai_he_thong_mo_coi.js

   Lỗi đã gặp: "thi thoảng chữ hệ thống to lại hiện ra trong khi chỗ đó đáng
   nhẽ là không có gì" - một nhãn "Hệ thống" cỡ lớn nằm giữa ô chọn ngôn ngữ và hàng version,
   bên dưới trống trơn. Nguyên nhân: `mobile-chat.js` dựng một khung `.rail-sys` (nhãn + chỗ chứa)
   để mượn ô chọn brain và nút sáng tối, rồi quên dọn khi khung rỗng.

   1.3.0: ô chọn bộ não nằm sẵn ở đầu thanh bên trên mọi màn, nên không còn khung "Hệ thống" nào
   để mồ côi. Chỉ còn nút sáng tối được mượn xuống đáy ngăn kéo trên điện thoại. Test canh rằng
   khung cũ không quay lại, và nút sáng tối đi đúng hai chiều. */
const fs = require("fs");
const path = require("path");

const ROOT = path.join(__dirname, "..", "..");
const JS = fs.readFileSync(path.join(ROOT, "dashboard", "mobile-chat.js"), "utf8");
const IDX = fs.readFileSync(path.join(ROOT, "dashboard", "index.html"), "utf8");

const fails = [];
const check = (name, cond, them) => {
  console.log((cond ? "ok   " : "FAIL ") + name + (!cond && them ? "  [" + them + "]" : ""));
  if (!cond) fails.push(name);
};

const place = (JS.match(/function placeSystem\(\)[\s\S]*?\n    \}/) || [""])[0];
check("tìm được placeSystem", place.length > 100);

// ---- 1. Khung "Hệ thống" không còn ----
check("không dựng khung .rail-sys nữa", !/rail-sys/.test(JS));
check("không mượn ô chọn brain nữa", !/navbar-brain/.test(JS));

// ---- 2. Bộ não nằm ở đầu thanh bên ----
const top = (IDX.match(/<div class="rail-top">[\s\S]*?<div class="rail-nav">/) || [""])[0];
check("ô chọn bộ não ở đầu thanh bên, dưới logo",
  /class="rail-brand"[\s\S]*class="orb-graph-ctl navbar-brain rail-brain"/.test(top) && /id="graphSource"/.test(top));
// Owner 03/11/2026: new sidebar, old middle, so the four buttons stay in the 1.2.1 top bar next to a mirror of the picker.
const hudTop = (IDX.match(/<div class="hud-top-left">[\s\S]*?<\/div>\s*<\/div>/) || [""])[0];
check("đủ bốn nút của bộ não ở thanh trên, cạnh ô bộ não soi gương", /bp-mirror/.test(hudTop) &&
  ["newBrainBtn", "renameBrainBtn", "delBrainBtn", "pickFolderBtn"].every((id) => hudTop.includes('id="' + id + '"')));
check("thanh trên không còn ô chọn bộ não", (IDX.match(/id="graphSource"/g) || []).length === 1);

// ---- 3. Nút sáng tối: xuống đáy ngăn kéo, quay về khi màn rộng ----
check("màn hẹp: nút sáng tối xuống đáy, cạnh nút thu mở",
  /foot\.insertBefore\(el, foot\.querySelector\("\.rail-collapse-btn"\)\)/.test(place));
check("chỉ mượn khi chưa nằm ở đáy (không mượn chồng)", /if \(el\.parentElement !== foot\)/.test(place), place);
check("màn rộng: trả về đúng chỗ cũ", /themeHome\.parent\.insertBefore\(el, themeHome\.next\)/.test(place)
  && /themeHome = null/.test(place), place);
check("không còn mượn dải VỪA GỌI đã bỏ", !/sysBar/.test(JS));

console.log();
if (fails.length) {
  console.log("FAIL " + fails.length + ": " + fails.join("; "));
  process.exit(1);
}
console.log("Tất cả xanh.");
