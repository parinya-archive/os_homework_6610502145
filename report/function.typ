#let header(content) = {
  counter("header-count").step()
  context {
    let n = counter("header-count").display()
    text(size: 14pt, weight: "bold")[#n. #content]
  }
}


#let topic(content) = {
  align(center)[
    #text(size: 16pt, weight: "bold", content)
  ]
}
