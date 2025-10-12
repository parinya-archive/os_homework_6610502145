#import calc: *

#let round_for_display(value) = {
  let rounded = calc.round(value, places: 2)
  let rounded_int = calc.round(value, places: 0)
  if calc.abs(rounded - rounded_int) < 0.005 {
    return rounded_int
  }
  return rounded
}

#let graph_chart(data, size: (12cm, 6cm), caption: [], x_ticks: 5, y_ticks: 5, margin: 18pt, line_color: blue) = {
  if data.len() == 0 {
    return figure(caption: caption, supplement: "Graph", kind: "plot", [No data provided])
  }

  let xs = data.map(pair => pair.at(0))
  let ys = data.map(pair => pair.at(1))

  let x_min = calc.min(..xs)
  let x_max = calc.max(..xs)
  let y_min = calc.min(..ys)
  let y_max = calc.max(..ys)

  if x_max == x_min {
    x_max = x_min + 1
  }
  if y_max == y_min {
    y_max = y_min + 1
  }

  let (width, height) = size
  let inner_width = width - 2 * margin
  let inner_height = height - 2 * margin

  let x_range = x_max - x_min
  let y_range = y_max - y_min

  let scaled_points = data.map(pair => (
    (pair.at(0) - x_min) / x_range * inner_width,
    -((pair.at(1) - y_min) / y_range * inner_height)
  ))

  figure(caption: caption, supplement: "Graph", kind: "plot", {
    box(width: width, height: height, {
      // axes
      place(dx: margin, dy: height - margin, line(length: inner_width, angle: 0deg, stroke: black))
      place(dx: margin, dy: height - margin, line(length: inner_height, angle: 90deg, stroke: black))

      // x-axis ticks and labels
      for i in range(0, x_ticks + 1) {
        let ratio = i / x_ticks
        let tick_x = margin + ratio * inner_width
        let value = x_min + ratio * x_range
        place(dx: tick_x, dy: height - margin, line(length: 6pt, angle: 90deg, stroke: black))
        place(dx: tick_x, dy: height - margin + 10pt,
          align(center + top, text(size: 9pt)[#round_for_display(value)]))
      }

      // y-axis ticks and labels
      for i in range(0, y_ticks + 1) {
        let ratio = i / y_ticks
        let tick_y = height - margin - ratio * inner_height
        let value = y_min + ratio * y_range
        place(dx: margin, dy: tick_y, line(length: 6pt, angle: 0deg, stroke: black))
        place(dx: margin - 10pt, dy: tick_y,
          align(right + center, text(size: 9pt)[#round_for_display(value)]))
      }

      // polyline connecting data points
      place(dx: margin, dy: height - margin,
        polygon(fill: none, stroke: (paint: line_color, width: 1.5pt), ..scaled_points))

      // markers for each point
      for (x, y) in scaled_points {
        place(dx: margin + x, dy: height - margin + y,
          circle(radius: 2.5pt, fill: line_color))
      }
    })
  })
}
