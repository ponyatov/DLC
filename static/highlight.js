function g(w)    { return w.join("") }
function s(c, w) { return "<span class=" + c + ">" + w + "</span>" }

grammar = PEG.buildParser(`
    dump = (class/id/op/ws/char)*
    class = l:lt w:[a-z]+ c:":"   { return l+s("clazz",g(w))+s("op",c) }
    id    = a:"@" h:[0-9a-f]+     { return s("id",a+g(h)) }
    op    = w:[=:]                { return s("op",w) }
    ws    = s:[ \\t\\r\\n]+       { return g(s) }
    char  = c:.                   { return c }

    lt    = "<"                   { return s("lgt","&lt;") }
    gt    = ">"                   { return s("lgt","&gt;") }
`)

function highlight(grammar, item) {
    console.log('highlight', grammar, item);
    item.html(grammar.parse(item.text()));
}

$(
    $(".dump").each(
        (idx, item) => highlight(grammar, $(item))
    )
)
