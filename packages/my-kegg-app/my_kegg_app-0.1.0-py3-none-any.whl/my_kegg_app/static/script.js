function loadEcInfo(ec) {
  fetch('/ec_info/' + ec)
    .then(res => res.text())
    .then(html => { document.getElementById('side-panel').innerHTML = html; });
}
function loadKeggInfo(rid) {
  fetch('/kegg_info/' + rid)
    .then(res => res.text())
    .then(html => { document.getElementById('side-panel').innerHTML = html; });
}
