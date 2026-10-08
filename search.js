(function () {
  var catalog = window.CATALOG || [];
  var tags = {
    build: "Build this shape",
    avoid: "Don't build this",
    study: "Real, don't clone",
    watch: "Not a pick",
  };

  function render(root) {
    var input = root.querySelector("input");
    var hits = root.querySelector(".hits");
    var prefix = root.getAttribute("data-prefix") || "";
    var q = input.value.trim().toLowerCase();
    if (!q) {
      hits.replaceChildren();
      hits.hidden = true;
      return;
    }
    var list = catalog.filter(function (s) {
      return (s.name + " " + s.founder + " " + s.category + " " + s.headline + " " + s.pitch).toLowerCase().indexOf(q) !== -1;
    }).slice(0, 10);
    hits.hidden = false;
    if (!list.length) {
      hits.textContent = "Nothing matches. Try a product, a founder, or a category.";
      return;
    }
    hits.replaceChildren.apply(hits, list.map(function (s) {
      var a = document.createElement("a");
      a.className = "hit";
      a.href = prefix + s.id + ".html";
      var tag = document.createElement("span");
      tag.className = "stamp " + (s.tag === "build" ? "holds" : s.tag === "avoid" ? "flex" : "dressed");
      tag.textContent = tags[s.tag] || s.tag;
      var name = document.createElement("strong");
      name.textContent = s.name;
      var meta = document.createElement("span");
      meta.className = "muted";
      meta.textContent = s.headline;
      a.append(tag, name, meta);
      return a;
    }));
  }

  document.querySelectorAll("[data-finder]").forEach(function (root) {
    var input = root.querySelector("input");
    input.addEventListener("input", function () { render(root); });
    input.addEventListener("keydown", function (event) {
      if (event.key !== "Enter") return;
      var first = root.querySelector(".hit");
      if (!first) return;
      event.preventDefault();
      window.location.href = first.getAttribute("href");
    });
    document.addEventListener("click", function (event) {
      if (!root.contains(event.target)) root.querySelector(".hits").hidden = true;
    });
    input.addEventListener("focus", function () { render(root); });
  });
})();
